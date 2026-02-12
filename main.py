from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import folium
from folium.plugins import LocateControl, Search, MarkerCluster
import json
import os
from datetime import datetime, timedelta

app = FastAPI()
FILE_NAME = "database_v23.json"
ADMIN_PIN = "2424"

# MOTOR DE DADOS COM ESTADO DE FILA E TEMPO
def carregar_dados():
    if not os.path.exists(FILE_NAME):
        dados = [
            {"id": 0, "banco": "BAI", "muni": "Luanda", "zona": "Marginal", "lat": -8.8120, "lng": 13.2300, "dinheiro": True, "votos": 10, "hora": datetime.now().isoformat(), "fila": "Vazio"},
            {"id": 1, "banco": "BFA", "muni": "Luanda", "zona": "Maianga", "lat": -8.8315, "lng": 13.2325, "dinheiro": True, "votos": 25, "hora": datetime.now().isoformat(), "fila": "Médio"},
            {"id": 2, "banco": "BIC", "muni": "Talatona", "zona": "Belas Shopping", "lat": -8.9280, "lng": 13.1780, "dinheiro": True, "votos": 14, "hora": datetime.now().isoformat(), "fila": "Cheio"},
        ]
        salvar_dados(dados)
        return dados
    with open(FILE_NAME, "r") as f:
        return json.load(f)

def salvar_dados(dados):
    with open(FILE_NAME, "w") as f:
        json.dump(dados, f, indent=4)

def calcular_tempo(iso_date):
    diff = datetime.now() - datetime.fromisoformat(iso_date)
    minutos = int(diff.total_seconds() / 60)
    if minutos < 60: return f"há {minutos} min"
    return f"há {minutos // 60}h"

@app.get("/", response_class=HTMLResponse)
def mostrar_mapa(request: Request):
    atms = carregar_dados()
    mapa = folium.Map(location=[-8.8383, 13.2344], zoom_start=13, tiles="cartodbpositron", zoom_control=False)

    ui_script = f"""
    <style>
        .leaflet-routing-container {{ display: none !important; }}
        #app-header {{
            position: fixed; top: 15px; left: 50%; transform: translateX(-50%);
            width: 90%; max-width: 400px; background: white; z-index: 10000;
            padding: 12px; border-radius: 30px; display: flex; align-items: center; justify-content: space-between;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2); font-family: sans-serif;
        }}
        .status-badge {{ font-size: 10px; padding: 2px 8px; border-radius: 10px; color: white; margin-left: 5px; }}
        .fila-vazio {{ background: #27ae60; }} .fila-medio {{ background: #f1c40f; }} .fila-cheio {{ background: #e67e22; }}
    </style>
    
    <div id="app-header">
        <div onclick="location.reload()" style="cursor:pointer;">🔄</div>
        <div style="font-weight: 800;">🏧 DINHEIRO <span style="color:#27ae60;">AKI</span></div>
        <div style="width:20px;"></div>
    </div>

    <script>
        var userLat = -8.8383, userLng = 13.2344;
        navigator.geolocation.getCurrentPosition(function(pos) {{
            userLat = pos.coords.latitude; userLng = pos.coords.longitude;
        }});

        function tracarRota(destLat, destLng) {{
            var mapInstance = window[document.querySelector('.folium-map').id];
            if (window.routingControl) {{ mapInstance.removeControl(window.routingControl); }}
            window.routingControl = L.Routing.control({{
                waypoints: [L.latLng(userLat, userLng), L.latLng(destLat, destLng)],
                lineOptions: {{ styles: [{{color: '#27ae60', weight: 6}}] }},
                createMarker: function() {{ return null; }}
            }}).addTo(mapInstance);
            mapInstance.closePopup();
        }}

        function updateFila(id) {{
            var f = prompt("Estado da Fila (1-Vazio, 2-Médio, 3-Cheio):");
            var status = f == "1" ? "Vazio" : f == "2" ? "Médio" : "Cheio";
            window.location.href = "/update_fila?id="+id+"&fila="+status;
        }}

        function adminAction(id, status) {{
            var p = prompt("PIN (2424):");
            if(p == "{ADMIN_PIN}") {{ window.location.href = "/trocar?id="+id+"&status="+status; }}
        }}
    </script>
    """
    mapa.get_root().header.add_child(folium.Element(ui_script))
    
    # Adicionar bibliotecas de rota caso faltem
    mapa.get_root().header.add_child(folium.Element('<link rel="stylesheet" href="https://unpkg.com/leaflet-routing-machine/dist/leaflet-routing-machine.css" /><script src="https://unpkg.com/leaflet-routing-machine/dist/leaflet-routing-machine.js"></script>'))

    cluster = MarkerCluster(name="Bancos").add_to(mapa)
    for atm in atms:
        cor = "#27ae60" if atm["dinheiro"] else "#e74c3c"
        tempo = calcular_tempo(atm["hora"])
        fila_classe = f"fila-{atm['fila'].lower()}"
        
        icon_html = f'''<div style="background:{cor}; border:2px solid white; border-radius:50%; width:36px; height:36px; display:flex; align-items:center; justify-content:center; color:white; font-weight:bold; font-size:10px;">{atm["banco"]}</div>'''
        
        popup_content = f"""
        <div style="text-align:center; font-family:sans-serif; width:190px;">
            <b style="font-size:16px;">{atm["banco"]}</b><br>
            <span style="font-size:11px; color:gray;">{atm["zona"]}</span><br>
            <div style="margin:8px 0;">
                <span style="color:{cor}; font-weight:bold;">{tempo}</span>
                <span class="status-badge {fila_classe}">Fila: {atm['fila']}</span>
            </div>
            <button onclick="tracarRota({atm['lat']}, {atm['lng']})" style="background:#27ae60; color:white; border:none; border-radius:20px; padding:10px; width:100%; font-weight:bold; cursor:pointer;">🚀 VER CAMINHO</button>
            <div style="display:flex; justify-content:center; gap:5px; margin-top:10px;">
                <button onclick="updateFila({atm['id']})" style="font-size:10px; cursor:pointer; background:none; border:1px solid #ccc; border-radius:10px; padding:2px 5px;">📊 Atualizar Fila</button>
                <button onclick="adminAction({atm['id']}, '{"false" if atm['dinheiro'] else "true"}')" style="font-size:10px; cursor:pointer; background:none; border:none; color: #7f8c8d;">⚙️ Admin</button>
            </div>
        </div>
        """
        folium.Marker([atm["lat"], atm["lng"]], popup=folium.Popup(popup_content, max_width=250), icon=folium.DivIcon(html=icon_html)).add_to(cluster)

    return HTMLResponse(content=mapa._repr_html_())

@app.get("/update_fila")
def update_fila(id: int, fila: str):
    atms = carregar_dados()
    for atm in atms:
        if atm["id"] == id:
            atm["fila"] = fila
            atm["hora"] = datetime.now().isoformat()
            break
    salvar_dados(atms)
    return RedirectResponse(url="/")

@app.get("/trocar")
def trocar_status(id: int, status: str):
    atms = carregar_dados()
    for atm in atms:
        if atm["id"] == id:
            atm["dinheiro"] = (status.lower() == "true")
            atm["hora"] = datetime.now().isoformat()
            break
    salvar_dados(atms)
    return RedirectResponse(url="/")
