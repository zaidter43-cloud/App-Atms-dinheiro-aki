from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import folium
from folium.plugins import LocateControl, Search, MarkerCluster
import json
import os
from datetime import datetime

app = FastAPI()
FILE_NAME = "database_atms_angola.json"
ADMIN_PIN = "2424"

# 1. MOTOR DE DADOS COM PERSISTÊNCIA REVISADA
def carregar_dados():
    if not os.path.exists(FILE_NAME):
        # Base de dados expandida com coordenadas precisas de Luanda
        dados = [
            {"id": 0, "banco": "BAI", "muni": "Luanda", "zona": "Marginal", "lat": -8.8120, "lng": 13.2300, "dinheiro": True, "votos": 5},
            {"id": 1, "banco": "BFA", "muni": "Luanda", "zona": "Maianga", "lat": -8.8315, "lng": 13.2325, "dinheiro": True, "votos": 12},
            {"id": 2, "banco": "BIC", "muni": "Talatona", "zona": "Belas Shopping", "lat": -8.9280, "lng": 13.1780, "dinheiro": True, "votos": 8},
            {"id": 3, "banco": "ATL", "muni": "Viana", "zona": "Viana Park", "lat": -8.9050, "lng": 13.3550, "dinheiro": False, "votos": 2},
            {"id": 4, "banco": "STB", "muni": "Kilamba", "zona": "Bloco B", "lat": -8.9950, "lng": 13.2750, "dinheiro": True, "votos": 15},
            {"id": 5, "banco": "SOL", "muni": "Cazenga", "zona": "Cuca", "lat": -8.8450, "lng": 13.2950, "dinheiro": True, "votos": 3},
            {"id": 6, "banco": "KEV", "muni": "Viana", "zona": "Zango 0", "lat": -8.9620, "lng": 13.4150, "dinheiro": True, "votos": 7},
            {"id": 7, "banco": "BCI", "muni": "Samba", "zona": "Gamek", "lat": -8.8780, "lng": 13.2150, "dinheiro": False, "votos": 1}
        ]
        salvar_dados(dados)
        return dados
    with open(FILE_NAME, "r") as f:
        return json.load(f)

def salvar_dados(dados):
    with open(FILE_NAME, "w") as f:
        json.dump(dados, f, indent=4)

@app.get("/", response_class=HTMLResponse)
def mostrar_mapa(request: Request):
    atms = carregar_dados()
    
    # Criar mapa base com CartoDB (mais leve para mobile)
    mapa = folium.Map(
        location=[-8.8383, 13.2344], 
        zoom_start=13, 
        tiles="cartodbpositron", 
        zoom_control=False
    )

    # 2. INJEÇÃO DE INTERFACE PRO (PWA + CSS + NAVEGAÇÃO)
    ui_app = f"""
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <link rel="apple-touch-icon" href="https://img.icons8.com/color/512/atm.png">
    
    <link rel="stylesheet" href="https://unpkg.com/leaflet-routing-machine/dist/leaflet-routing-machine.css" />
    <script src="https://unpkg.com/leaflet-routing-machine/dist/leaflet-routing-machine.js"></script>

    <style>
        .leaflet-routing-container {{ display: none !important; }}
        .leaflet-control-locate {{ border: none !important; box-shadow: 0 2px 10px rgba(0,0,0,0.2) !important; }}
        
        #main-header {{
            position: fixed; top: 15px; left: 50%; transform: translateX(-50%);
            width: 88%; max-width: 450px; background: white; z-index: 10000;
            padding: 12px; border-radius: 25px; display: flex; align-items: center; justify-content: space-between;
            box-shadow: 0 5px 20px rgba(0,0,0,0.15); font-family: 'Segoe UI', sans-serif;
            border-bottom: 4px solid #27ae60;
        }}
        
        #filter-bar {{
            position: fixed; bottom: 25px; left: 50%; transform: translateX(-50%);
            width: auto; background: rgba(255,255,255,0.9); z-index: 9999;
            padding: 8px 15px; border-radius: 20px; display: flex; gap: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1); backdrop-filter: blur(5px);
        }}

        .filter-btn {{
            padding: 5px 12px; border-radius: 15px; font-size: 11px; font-weight: bold;
            border: 1px solid #ddd; background: white; cursor: pointer;
        }}
        
        .leaflet-popup-content {{ font-family: 'Segoe UI', sans-serif; width: 200px !important; }}
    </style>

    <div id="main-header">
        <div onclick="location.reload()" style="cursor:pointer; font-size:18px;">🔄</div>
        <div style="font-weight: 800; color: #2c3e50; font-size: 16px;">🏧 DINHEIRO <span style="color:#27ae60;">AKI</span></div>
        <div onclick="alert('Funcionalidade de Partilha brevemente!')" style="cursor:pointer; font-size:18px;">🔗</div>
    </div>

    <div id="filter-bar">
        <button class="filter-btn" style="color: #27ae60;" onclick="window.location.href='/?filter=cash'">✅ COM NOTAS</button>
        <button class="filter-btn" style="color: #e74c3c;" onclick="window.location.href='/'">📍 TODOS</button>
    </div>

    <script>
        var userLat, userLng, routingControl;
        
        // Auto-detectar localização mal abre
        navigator.geolocation.getCurrentPosition(function(pos) {{
            userLat = pos.coords.latitude;
            userLng = pos.coords.longitude;
        }}, function(err) {{ console.log("GPS bloqueado"); }}, {{enableHighAccuracy: true}});

        function iniciarRota(lat, lng) {{
            var mapElement = document.querySelector('.folium-map').id;
            var mapInstance = window[mapElement];
            
            if (routingControl) {{ mapInstance.removeControl(routingControl); }}
            
            if (!userLat) {{
                alert("Ativa o GPS do telemóvel para traçarmos o caminho!");
                return;
            }}

            routingControl = L.Routing.control({{
                waypoints: [L.latLng(userLat, userLng), L.latLng(lat, lng)],
                lineOptions: {{ styles: [{{color: '#27ae60', weight: 6, opacity: 0.8}}] }},
                createMarker: function() {{ return null; }},
                addWaypoints: false
            }}).addTo(mapInstance);
            
            mapInstance.closePopup();
        }}

        function adminAction(id, status) {{
            var p = prompt("PIN Administrativo (2424):");
            if(p == "{ADMIN_PIN}") {{ window.location.href = "/trocar?id="+id+"&status="+status; }}
        }}
    </script>
    """
    mapa.get_root().header.add_child(folium.Element(ui_app))

    # 3. FILTRAGEM DE DADOS
    query_filter = request.query_params.get("filter")
    atms_para_mostrar = [a for a in atms if a["dinheiro"]] if query_filter == "cash" else atms

    # 4. CLUSTERING E MARCADORES
    cluster = MarkerCluster(name="Bancos", disableClusteringAtZoom=16).add_to(mapa)
    LocateControl(auto_start=False, flyTo=True, keepCurrentZoomLevel=True).add_to(mapa)

    for atm in atms_para_mostrar:
        cor = "#27ae60" if atm["dinheiro"] else "#e74c3c"
        status_txt = "COM DINHEIRO" if atm["dinheiro"] else "SEM NOTAS"
        
        icon_html = f'''<div style="background:{cor}; border:3px solid white; border-radius:50%; width:38px; height:38px; display:flex; align-items:center; justify-content:center; color:white; font-weight:900; font-size:10px; box-shadow:0 4px 10px rgba(0,0,0,0.3);">{atm["banco"]}</div>'''
        
        popup_html = f"""
        <div style="text-align:center;">
            <b style="font-size:18px; color:#2c3e50;">{atm["banco"]}</b><br>
            <span style="color:#7f8c8d; font-size:13px;">{atm["zona"]}</span><br>
            <div style="margin:10px 0; font-weight:bold; color:{cor};">{status_txt}</div>
            
            <button onclick="iniciarRota({atm['lat']}, {atm['lng']})" 
                style="background:#27ae60; color:white; border:none; border-radius:25px; padding:12px; width:100%; font-weight:bold; cursor:pointer; font-size:13px; margin-bottom:10px; box-shadow: 0 4px 10px rgba(39,174,96,0.3);">
                🚀 VER CAMINHO
            </button>
            
            <span onclick="adminAction({atm['id']}, '{"false" if atm['dinheiro'] else "true"}')" 
                  style="color:#bdc3c7; font-size:10px; cursor:pointer; text-decoration:underline;">
                Atualizar Estado (Admin)
            </span>
        </div>
        """
        
        folium.Marker(
            location=[atm["lat"], atm["lng"]],
            popup=folium.Popup(popup_html, max_width=220),
            icon=folium.DivIcon(html=icon_html),
            name=f"{atm['banco']} {atm['zona']} {atm['muni']}"
        ).add_to(cluster)

    Search(layer=cluster, geom_type="Point", placeholder="Procurar zona ou banco...", collapsed=False, search_label="name", zoom=17).add_to(mapa)

    return HTMLResponse(content=mapa._repr_html_())

@app.get("/trocar")
def trocar_status(id: int, status: str):
    atms = carregar_dados()
    for atm in atms:
        if atm["id"] == id:
            atm["dinheiro"] = (status.lower() == "true")
            atm["ultima_v"] = datetime.now().strftime("%H:%M")
            break
    salvar_dados(atms)
    return RedirectResponse(url="/")
