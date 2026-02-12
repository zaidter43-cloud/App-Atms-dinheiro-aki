from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import folium
from folium.plugins import LocateControl, Search, MarkerCluster
import json
import os
from datetime import datetime

app = FastAPI()
FILE_NAME = "database_v25.json"
ADMIN_PIN = "2424"

def carregar_dados():
    if not os.path.exists(FILE_NAME):
        dados = [
            {"id": 0, "banco": "BAI", "muni": "Luanda", "zona": "Marginal", "lat": -8.8120, "lng": 13.2300, "dinheiro": True, "votos": 10, "hora": datetime.now().isoformat(), "fila": "Vazio"},
            {"id": 1, "banco": "BFA", "muni": "Luanda", "zona": "Maianga", "lat": -8.8315, "lng": 13.2325, "dinheiro": True, "votos": 25, "hora": datetime.now().isoformat(), "fila": "Médio"},
            {"id": 2, "banco": "BIC", "muni": "Talatona", "zona": "Belas Shopping", "lat": -8.9280, "lng": 13.1780, "dinheiro": True, "votos": 14, "hora": datetime.now().isoformat(), "fila": "Cheio"},
            {"id": 3, "banco": "ATL", "muni": "Viana", "zona": "Viana Park", "lat": -8.9050, "lng": 13.3550, "dinheiro": False, "votos": 5, "hora": datetime.now().isoformat(), "fila": "Vazio"}
        ]
        salvar_dados(dados)
        return dados
    with open(FILE_NAME, "r") as f:
        return json.load(f)

def salvar_dados(dados):
    with open(FILE_NAME, "w") as f:
        json.dump(dados, f, indent=4)

def calcular_tempo(iso_date):
    try:
        diff = datetime.now() - datetime.fromisoformat(iso_date)
        minutos = int(diff.total_seconds() / 60)
        if minutos < 1: return "agora mesmo"
        if minutos < 60: return f"há {minutos} min"
        return f"há {minutos // 60}h"
    except: return "sem dados"

@app.get("/", response_class=HTMLResponse)
def mostrar_mapa(request: Request):
    atms = carregar_dados()
    mapa = folium.Map(location=[-8.8383, 13.2344], zoom_start=13, tiles="cartodbpositron", zoom_control=False)

    header_content = f"""
    <link rel="stylesheet" href="https://unpkg.com/leaflet-routing-machine/dist/leaflet-routing-machine.css" />
    <script src="https://unpkg.com/leaflet-routing-machine/dist/leaflet-routing-machine.js"></script>
    <style>
        .leaflet-routing-container {{ display: none !important; }}
        #app-header {{
            position: fixed; top: 15px; left: 50%; transform: translateX(-50%);
            width: 90%; max-width: 400px; background: white; z-index: 10000;
            padding: 12px; border-radius: 30px; display: flex; align-items: center; justify-content: space-between;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2); font-family: sans-serif;
        }}
        .badge {{ font-size: 10px; padding: 3px 10px; border-radius: 12px; color: white; font-weight: bold; }}
        .f-vazio {{ background: #27ae60; }} .f-medio {{ background: #f1c40f; color: black; }} .f-cheio {{ background: #e67e22; }}
    </style>
    
    <div id="app-header">
        <div onclick="location.reload()" style="cursor:pointer; font-size:20px;">🔄</div>
        <div style="font-weight: 800; letter-spacing: -0.5px;">🏧 DINHEIRO <span style="color:#27ae60;">AKI</span></div>
        <div onclick="partilharApp()" style="cursor:pointer; font-size:20px;">🔗</div>
    </div>

    <script>
        var uLat = -8.8383, uLng = 13.2344;
        navigator.geolocation.getCurrentPosition(function(p){{ uLat=p.coords.latitude; uLng=p.coords.longitude; }});

        function partilharApp() {{
            if (navigator.share) {{
                navigator.share({{
                    title: 'Dinheiro Aki',
                    text: 'Encontra ATMs com notas em Luanda agora!',
                    url: window.location.href
                }}).catch(console.error);
            }} else {{
                alert("Copia o link para partilhar: " + window.location.href);
            }}
        }}

        function ir(lat, lng) {{
            var m = window[document.querySelector('.folium-map').id];
            if (window.rC) {{ m.removeControl(window.rC); }}
            window.rC = L.Routing.control({{
                waypoints: [L.latLng(uLat
