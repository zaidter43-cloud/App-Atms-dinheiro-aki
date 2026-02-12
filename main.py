from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse
import folium
from folium.plugins import LocateControl, Search, MarkerCluster
import json
import os
from datetime import datetime

app = FastAPI()
FILE_NAME = "dados_v19_final.json"
ADMIN_PIN = "2424"

def carregar_dados():
    if not os.path.exists(FILE_NAME):
        dados = [
            {"id": 0, "banco": "BAI", "muni": "Luanda", "zona": "Marginal (Sede)", "lat": -8.8120, "lng": 13.2300, "dinheiro": True},
            {"id": 1, "banco": "BFA", "muni": "Luanda", "zona": "Maianga", "lat": -8.8315, "lng": 13.2325, "dinheiro": True},
            {"id": 2, "banco": "BIC", "muni": "Talatona", "zona": "Belas Shopping", "lat": -8.9280, "lng": 13.1780, "dinheiro": True},
            {"id": 3, "banco": "ATL", "muni": "Viana", "zona": "Viana Park", "lat": -8.9050, "lng": 13.3550, "dinheiro": True},
            {"id": 4, "banco": "STB", "muni": "Kilamba", "zona": "Bloco B", "lat": -8.9950, "lng": 13.2750, "dinheiro": True},
            {"id": 5, "banco": "SOL", "muni": "Cazenga", "zona": "Marco Histórico", "lat": -8.8450, "lng": 13.2950, "dinheiro": False}
        ]
        for d in dados: d["hora"] = datetime.now().strftime("%H:%M")
        salvar_dados(dados)
        return dados
    with open(FILE_NAME, "r") as f:
        return json.load(f)

def salvar_dados(dados):
    with open(FILE_NAME, "w") as f:
        json.dump(dados, f, indent=4)

@app.get("/", response_class=HTMLResponse)
def mostrar_mapa():
    atms = carregar_dados()
    
    # MUDANÇA AQUI: Usando o servidor de mapas do Google para ver detalhes de ruas e prédios
    mapa = folium.Map(
        location=[-8.8383, 13.2344], 
        zoom_start=15, # Começa mais perto para ver os detalhes
        tiles='https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', # Google Maps Road Map
        attr='Google',
        zoom_control=False
    )
    
    # Camada Satélite Opcional (Podes trocar no menu do mapa)
    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
        attr='Google Satélite',
        name='Satélite (Google)'
    ).add_to(mapa)

    header_extra = f"""
    <link rel="stylesheet" href="https://unpkg.com/leaflet-routing-machine/dist/leaflet-routing-machine.css" />
    <script src="https://unpkg.com/leaflet-routing-machine/dist/leaflet-routing-machine.js"></script>
    <style>
        .leaflet-routing-container {{ display: none !important; }}
        #app-header {{
            position: fixed; top: 15px; left: 50%; transform: translateX(-50%);
            width: 90%; max-width: 400px; background: white; z-index: 9999;
            padding: 12px; border-radius: 30px; display: flex; align-items: center; justify-content: space-between;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2); font-family: sans-serif; border-bottom: 3px solid #27ae60;
        }}
    </style>
    <div id="app-header">
        <div style="width: 30px;"></div>
        <div style="font-weight: bold;">🏧 DINHEIRO <span style="color:#27ae60;">AKI</span></div>
        <div onclick="location.reload()" style="cursor: pointer; font-size: 18px; padding-right:10px;">🔄</div>
    </div>
    <script>
        var userLat, userLng, routingControl;
        navigator.geolocation.getCurrentPosition(function(pos) {{
            userLat = pos.coords.latitude;
            userLng = pos.coords.longitude;
        }});

        function tracarRota(destLat, destLng) {{
            var mapElement = document.getElementsByClassName('folium-map')[0].id;
            var mapInstance = window[mapElement];
            if (routingControl) {{ mapInstance.removeControl(routingControl); }}
            routingControl = L.Routing.control({{
                waypoints: [L.latLng(userLat, userLng), L.latLng(destLat, destLng)],
                lineOptions: {{ styles: [{{color: '#1a73e8', weight: 6}}] }},
                createMarker: function() {{ return null; }}
            }}).addTo(mapInstance);
            mapInstance.closePopup();
        }}
    </script>
    """
    mapa.get_root().header.add_child(folium.Element(header_extra))

    # Adicionar controle de camadas (para trocar entre mapa normal e satélite)
    folium.LayerControl(position='bottomright').add_to(mapa)
    
    LocateControl(auto_start=True, flyTo=True).add_to(mapa)
    cluster = MarkerCluster(name="Bancos").add_to(mapa)

    for atm in atms:
        cor = "green" if atm["dinheiro"] else "red"
        icon_html = f'''<div style="background-color: {cor}; border: 2px solid white; border-radius: 50%; width: 34px; height: 34px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 9px; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">{atm["banco"]}</div>'''
        
        folium.Marker(
            location=[atm["lat"], atm["lng"]],
            popup=folium.Popup(f'<div style="text-align:center;"><b style="font-size:14px;">{atm["banco"]}</b><br>{atm["zona"]}<br><button onclick="tracarRota({atm["lat"]}, {atm["lng"]})" style="background:#1a73e8;color:white;border:none;border-radius:15px;padding:8px;margin-top:10px;width:100%;font-weight:bold;">TRAÇAR ROTA</button></div>', max_width=200),
            icon=folium.DivIcon(html=icon_html),
            name=f"{atm['banco']} {atm['zona']}"
        ).add_to(cluster)

    Search(layer=cluster, geom_type="Point", placeholder="Procurar...", collapsed=False, search_label="name", zoom=17).add_to(mapa)

    return HTMLResponse(content=mapa._repr_html_())
