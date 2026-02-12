from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import folium
from folium.plugins import LocateControl
import json
import os
from datetime import datetime

app = FastAPI()
FILE_NAME = "db_luanda_v48.json"
ADMIN_PIN_SERVER = "2424"

# Configuração Técnica de Cores (Design v32/33)
BANCOS_CONFIG = {
    "BAI": "#004a99", "BFA": "#ff6600", "BIC": "#e30613", 
    "SOL": "#f9b233", "ATL": "#00a1de", "BCI": "#005da4",
    "KEVE": "#7b6348", "ECONO": "#003366", "STB": "#000000"
}

def inicializar_base():
    if not os.path.exists(FILE_NAME):
        # 50 Pontos Estratégicos por Município
        dados = [
            {"id": 0, "banco": "BAI", "zona": "Mutamba Sede", "muni": "Luanda", "lat": -8.8147, "lng": 13.2305},
            {"id": 1, "banco": "BFA", "zona": "Kinaxixi", "muni": "Luanda", "lat": -8.8182, "lng": 13.2381},
            {"id": 2, "banco": "BIC", "zona": "Kero Talatona", "muni": "Talatona", "lat": -8.9180, "lng": 13.1900},
            {"id": 3, "banco": "SOL", "zona": "Belas Shopping", "muni": "Talatona", "lat": -8.9288, "lng": 13.1782},
            {"id": 4, "banco": "ATL", "zona": "Ponte Amarela", "muni": "Viana", "lat": -8.9020, "lng": 13.3650},
            {"id": 5, "banco": "BAI", "zona": "Zango 0", "muni": "Viana", "lat": -8.9620, "lng": 13.4020},
            {"id": 6, "banco": "BFA", "zona": "Kilamba Bloco B", "muni": "Belas", "lat": -8.9970, "lng": 13.2710},
            {"id": 7, "banco": "BCI", "zona": "Mabor", "muni": "Cazenga", "lat": -8.8450, "lng": 13.2950},
            {"id": 8, "banco": "ATL", "zona": "Vila de Cacuaco", "muni": "Cacuaco", "lat": -8.7770, "lng": 13.3650},
            {"id": 9, "banco": "KEVE", "zona": "Corimba", "muni": "Samba", "lat": -8.8750, "lng": 13.1950}
        ]
        # Gerar placeholders para completar 50 pontos reais
        for i in range(len(dados), 50):
            dados.append({"id": i, "banco": "BFA", "zona": f"ATM Principal {i}", "muni": "Luanda", "lat": -8.85+(i*0.0015), "lng": 13.25+(i*0.0015)})
        
        for d in dados: d.update({"s": True, "f": "Vazio", "h": datetime.now().isoformat()})
        with open(FILE_NAME, "w") as f: json.dump(dados, f, indent=4)

@app.on_event("startup")
def startup(): inicializar_base()

@app.get("/", response_class=HTMLResponse)
def home():
    with open(FILE_NAME, "r") as f: atms = json.load(f)
    mapa = folium.Map(location=[-8.8383, 13.2344], zoom_start=12, tiles="cartodbpositron", zoom_control=False)
    
    # Localização nativa
    LocateControl(fly_to=True, keepCurrentZoomLevel=False).add_to(mapa)

    # UI v32/v33: Técnica e Scannable
    ui = f"""
    <style>
        #app-header {{
            position: fixed; top: 12px; left: 50%; transform: translateX(-50%);
            width: 92%; max-width: 480px; background: white; z-index: 10000;
            padding: 12px; border-radius: 35px; box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}
        .top-bar {{ display: flex; justify-content: space-between; align-items: center; padding: 0 5px; }}
        .search-bar {{ 
            display: flex; align-items: center; background: #f4f4f7; 
            border-radius: 20px; padding: 6px 15px; margin-top: 10px;
        }}
        #q {{ border: none; background: transparent; width: 100%; padding: 5px; outline: none; font-size: 14px; color: #333; }}
        
        /* Badges Técnicos v33 */
        .badge {{ font-size: 10px; padding: 3px 10px; border-radius: 12px; color: white; font-weight: bold; text-transform: uppercase; }}
        .f-vazio {{ background: #27ae60; }} 
        .f-medio {{ background: #f1c40f; color: #2c3e50; }} 
        .f-cheio {{ background: #e67e22; }}
        
        .btn-nav {{ 
            background: #2c3e50; color: white; border: none; padding: 12px; 
            border-radius: 20px; width: 100%; font-weight: bold; cursor: pointer;
            margin-top: 10px; transition: 0.2s;
        }}
        .btn-nav:active {{ transform: scale(0.98); background: #1a252f; }}
    </style>

    <div id="app-header">
        <div class="top-bar">
            <span onclick="location.reload()" style="cursor:pointer; font-size:18px;">🔄</span>
            <span style="font-weight: 800; font-size:16px; letter-spacing: 0.5px;">🏧 DINHEIRO <span style="color:#27ae60;">AKI</span></span>
            <span onclick="partilhar()" style="cursor:pointer; font-size:18px;">📤</span>
        </div>
        <div class="search-bar">
            <span>🔍</span>
            <input type="text" id="q" placeholder="Procurar banco ou município..." onkeyup="filtrar()">
        </div>
    </div>

    <script>
        var data = {json.dumps(atms)};
        var cores = {json.dumps(BANCOS_CONFIG)};
        var markers = [];

        window.onload = function() {{
            var m = window[document.querySelector('.folium-map').id];
            
            data.forEach(function(a) {{
                var corStatus = a.s ? '#27ae60' : '#e74c3c';
                var corB = cores[a.b] || '#000';
                
                // Design de Marcador Técnico v32
                var icon = L.divIcon({{
                    html: `<div style="background:${{corB}}; border: 3px solid ${{corStatus}}; width:32px; height:32px; border-radius:50%; color:white; font-size:9px; display:flex; align-items:center; justify-content:center; font-weight:bold; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">${{a.b}}</div>`,
                    className: '', iconSize: [32, 32]
                }});

                var marker = L.marker([a.lat, a.lng], {{icon: icon}}).addTo(m);
                
                marker.bindPopup(`
                    <div style="text-align:center; font-family:sans-serif; width:200px; padding:5px;">
                        <b style="font-size:18px; color:${{corB}}">${{a.b}}</b><br>
                        <small style="color:#7f8c8d; font-weight:bold;">${{a.muni}} - ${{a.zona}}</small>
                        <hr style="border:0.5px solid #eee; margin:10px 0;">
                        <div style="margin-bottom:8px;">Status: <b style="color:${{corStatus}}">${{a.s ? 'TEM NOTAS' : 'SEM NOTAS'}}</b></div>
                        <div>Fila: <span class="badge ${{a.f=='Vazio'?'f-vazio':a.f=='Médio
