from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import folium
from folium.plugins import MarkerCluster, LocateControl
import json
import os
import random
from datetime import datetime

app = FastAPI()
FILE_NAME = "db_luanda_v42.json"
ADMIN_PIN = "2424"

# Cores oficiais dos bancos em Angola
CORES_BANCOS = {
    "BAI": "#004a99", "BFA": "#ff6600", "BIC": "#e30613", 
    "SOL": "#f9b233", "ATL": "#00a1de", "BCI": "#005da4",
    "KEVE": "#7b6348", "ECONO": "#003366", "STB": "#000000"
}

def inicializar_base():
    if not os.path.exists(FILE_NAME):
        municipios = [
            {"n": "Luanda", "lat": -8.814, "lng": 13.230, "q": 800},
            {"n": "Talatona", "lat": -8.928, "lng": 13.178, "q": 500},
            {"n": "Viana", "lat": -8.902, "lng": 13.365, "q": 400},
            {"n": "Kilamba", "lat": -8.997, "lng": 13.271, "q": 250},
            {"n": "Cacuaco", "lat": -8.777, "lng": 13.365, "q": 150}
        ]
        bancos = list(CORES_BANCOS.keys())
        dados = []
        for m in municipios:
            for i in range(m["q"]):
                dados.append({
                    "id": len(dados),
                    "b": random.choice(bancos),
                    "lat": round(m["lat"] + random.uniform(-0.04, 0.04), 5),
                    "lng": round(m["lng"] + random.uniform(-0.04, 0.04), 5),
                    "s": random.choice([True, True, False]), # Status: Tem dinheiro?
                    "f": random.choice(["Vazio", "Médio", "Cheio"])
                })
        with open(FILE_NAME, "w") as f: json.dump(dados, f)

@app.on_event("startup")
def startup(): inicializar_base()

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    with open(FILE_NAME, "r") as f: atms = json.load(f)
    
    mapa = folium.Map(location=[-8.8383, 13.2344], zoom_start=12, tiles="cartodbpositron", zoom_control=False)
    LocateControl(fly_to=True).add_to(mapa)

    # UI Técnica e Segura
    ui = f"""
    <style>
        #header {{ position: fixed; top: 10px; left: 50%; transform: translateX(-50%); width: 90%; max-width: 400px; background: white; z-index: 10000; padding: 12px; border-radius: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.2); display: flex; justify-content: space-between; align-items: center; font-family: sans-serif; }}
        .dot {{ width: 12px; height: 12px; border-radius: 50%; display: inline-block; margin-right: 5px; }}
    </style>
    <div id="header">
        <b onclick="location.reload()">🔄</b>
        <span style="font-weight: 900;">🏧 DINHEIRO <span style="color:#27ae60;">AKI</span></span>
        <small style="background: #eee; padding: 4px 8px; border-radius: 10px;">{len(atms)} ATMs</small>
    </div>
    <script>
        var atms_data = {json.dumps(atms)};
        var cores_bancos = {json.dumps(CORES_BANCOS)};
        
        window.onload = function() {{
            var m = window[document.querySelector('.folium-map').id];
            var cluster = L.markerClusterGroup();
            
            atms_data.forEach(function(a) {{
                var corStatus = a.s ? '#27ae60' : '#e74c3c';
                var corBanco = cores_bancos[a.b];
                
                var icon = L.divIcon({{
                    html: `<div style="background:${{corBanco}}; border: 3px solid ${{corStatus}}; width:30px; height:30px; border-radius:50%; color:white; font-size:8px; display:flex; align-items:center; justify-content:center; font-weight:bold; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">${{a.b}}</div>`,
                    className: '', iconSize: [30, 30]
                }});

                var marker = L.marker([a.lat, a.lng], {{icon: icon}});
                marker.bindPopup(`
                    <div style="text-align:center; font-family:sans-serif;">
                        <b style="font-size:16px; color:${{corBanco}}">${{a.b}}</b><br>
                        Status: <b style="color:${{corStatus}}">${{a.s ? 'TEM NOTAS' : 'SEM NOTAS'}}</b><br>
                        Fila: <b>${{a.f}}</b><hr>
                        <button onclick="window.open('https://www.google.com/maps/dir/?api=1&destination=${{a.lat}},${{a.lng}}')" style="background:#2c3e50; color:white; border:none; padding:8px 15px; border-radius:15px; cursor:pointer; width:100%;">🚀 ABRIR GPS</button>
                    </div>
                `);
                cluster.addLayer(marker);
            }});
            m.addLayer(cluster);
        }};
    </script>
    """
    mapa.get_root().header.add_child(folium.Element(ui))
    return HTMLResponse(content=mapa._repr_html_())
