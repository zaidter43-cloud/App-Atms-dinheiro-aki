from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse
import folium
from folium.plugins import LocateControl, Search, MarkerCluster
import json
import os
from datetime import datetime

app = FastAPI()
FILE_NAME = "dados_v20.json"
ADMIN_PIN = "2424"

def carregar_dados():
    if not os.path.exists(FILE_NAME):
        dados = [
            {"id": 0, "banco": "BAI", "muni": "Luanda", "zona": "Marginal", "lat": -8.8120, "lng": 13.2300, "dinheiro": True},
            {"id": 1, "banco": "BFA", "muni": "Luanda", "zona": "Maianga", "lat": -8.8315, "lng": 13.2325, "dinheiro": True},
            {"id": 2, "banco": "BIC", "muni": "Talatona", "zona": "Belas Shopping", "lat": -8.9280, "lng": 13.1780, "dinheiro": True},
            {"id": 3, "banco": "ATL", "muni": "Viana", "zona": "Viana Park", "lat": -8.9050, "lng": 13.3550, "dinheiro": True},
            {"id": 4, "banco": "STB", "muni": "Kilamba", "zona": "Bloco B", "lat": -8.9950, "lng": 13.2750, "dinheiro": True},
            {"id": 5, "banco": "SOL", "muni": "Cazenga", "zona": "Marco Histórico", "lat": -8.8450, "lng": 13.2950, "dinheiro": False}
        ]
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
    
    # Mapa base estável (CartoDB) que não bloqueia cliques
    mapa = folium.Map(
        location=[-8.8383, 13.2344], 
        zoom_start=13, 
        tiles="cartodbpositron",
        zoom_control=False
    )

    # Injeção de CSS e Scripts corrigida para não travar o ecrã
    header_logic = f"""
    <link rel="stylesheet" href="https://unpkg.com/leaflet-routing-machine/dist/leaflet-routing-machine.css" />
    <script src="https://unpkg.com/leaflet-routing-machine/dist/leaflet-routing-machine.js"></script>
    <style>
        .leaflet-routing-container {{ display: none !important; }}
        .leaflet-marker-icon, .leaflet-marker-shadow, .leaflet-image-layer, .leaflet-pane > svg path, .leaflet-tile-container {{ pointer-events: auto !important; }}
        #app-header {{
            position: fixed; top: 15px; left: 50%; transform: translateX(-50%);
            width: 85%; max-width: 400px; background: white; z-index: 10000;
            padding: 12px; border-radius: 30px; display: flex; align-items: center; justify-content: space-between;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2); font-family: sans-serif; border-bottom: 3px solid #27ae60;
            pointer-events: none;
        }}
        #app-header * {{ pointer-events: auto; }}
    </style>
    <div id="app-header">
        <div style="width: 30px;"></div>
        <div style="font-weight: bold; font-family: sans-serif;">🏧 DINHEIRO <span style="color:#27ae60;">AKI</span></div>
        <div onclick="location.reload()" style="cursor: pointer; font-size: 18px; padding-right:10px;">🔄</div>
    </div>
    <script>
        var userLat, userLng, routingControl;
        
        navigator.geolocation.getCurrentPosition(function(pos) {{
            userLat = pos.coords.latitude;
            userLng = pos.coords.longitude;
        }}, function() {{ console.log("GPS negado"); }}, {{enableHighAccuracy: true}});

        function tracarRota(destLat, destLng) {{
            var mapElement = document.querySelector('.folium-map').id;
            var mapInstance = window[mapElement];
            
            if (routingControl) {{ mapInstance.removeControl(routingControl); }}
            
            if (!userLat) {{
                alert("Ativa o GPS para traçar a rota!");
                return;
            }}

            routingControl = L.Routing.control({{
                waypoints: [L.latLng(userLat, userLng), L.latLng(destLat, destLng)],
                lineOptions: {{ styles: [{{color: '#27ae60', weight: 6, opacity: 0.7}}] }},
                createMarker: function() {{ return null; }}
            }}).addTo(mapInstance);
            mapInstance.closePopup();
        }}

        function authUpdate(id, status) {{
            var p = prompt("Código 2424:");
            if(p == "{ADMIN_PIN}") {{ window.location.href = "/trocar?id="+id+"&status="+status; }}
        }}
    </script>
    """
    mapa.get_root().header.add_child(folium.Element(header_logic))

    # Plugins
    LocateControl(auto_start=False, flyTo=True).add_to(mapa)
    cluster = MarkerCluster(name="Bancos").add_to(mapa)

    for atm in atms:
        cor = "green" if atm["dinheiro"] else "red"
        icon_html = f'''<div style="background-color: {cor}; border: 2px solid white; border-radius: 50%; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 10px; box-shadow: 0 3px 8px rgba(0,0,0,0.3);">{atm["banco"]}</div>'''
        
        popup_content = f"""
        <div style="text-align:center; font-family: sans-serif; min-width: 180px;">
            <b style="font-size:16px;">{atm["banco"]}</b><br>{atm["zona"]}<hr>
            <button onclick="tracarRota({atm['lat']}, {atm['lng']})" 
                style="background:#27ae60; color:white; border:none; border-radius:20px; padding:12px; width:100%; font-weight:bold; cursor:pointer; margin-bottom:10px;">
                🚀 TRAÇAR ROTA
            </button>
            <button onclick="authUpdate({atm['id']}, '{"false" if atm['dinheiro'] else "true"}')" 
                style="background:transparent; color:gray; border:none; font-size:11px; cursor:pointer;">
                Reportar Estado
            </button>
        </div>
        """
        
        folium.Marker(
            location=[atm["lat"], atm["lng"]],
            popup=folium.Popup(popup_content, max_width=250),
            icon=folium.DivIcon(html=icon_html),
            name=f"{atm['banco']} {atm['zona']}"
        ).add_to(cluster)

    Search(layer=cluster, geom_type="Point", placeholder="Procurar...", collapsed=False, search_label="name", zoom=16).add_to(mapa)

    return HTMLResponse(content=mapa._repr_html_())

@app.get("/trocar")
def trocar_status(id: int, status: str):
    atms = carregar_dados()
    for atm in atms:
        if atm["id"] == id:
            atm["dinheiro"] = (status.lower() == "true")
            break
    salvar_dados(atms)
    return RedirectResponse(url="/")
