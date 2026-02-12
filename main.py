from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import folium
from folium.plugins import MarkerCluster, LocateControl
import json
import os
import random
import time
from datetime import datetime

app = FastAPI()
FILE_NAME = "db_luanda_v43.json"
ADMIN_PIN_SERVER = "2424"

# Cores oficiais dos bancos em Angola
BANCOS_CONFIG = {
    "BAI": {"cor": "#004a99"}, "BFA": {"cor": "#ff6600"}, "BIC": {"cor": "#e30613"}, 
    "SOL": {"cor": "#f9b233"}, "ATL": {"cor": "#00a1de"}, "BCI": {"cor": "#005da4"},
    "KEVE": {"cor": "#7b6348"}, "ECONO": {"cor": "#003366"}, "STB": {"cor": "#000000"}
}

def inicializar_base():
    if not os.path.exists(FILE_NAME):
        municipios = [
            {"n": "Luanda Centro", "lat": -8.814, "lng": 13.230, "q": 800},
            {"n": "Talatona", "lat": -8.928, "lng": 13.178, "q": 500},
            {"n": "Viana", "lat": -8.902, "lng": 13.365, "q": 400},
            {"n": "Kilamba", "lat": -8.997, "lng": 13.271, "q": 250},
            {"n": "Cacuaco", "lat": -8.777, "lng": 13.365, "q": 150}
        ]
        bancos = list(BANCOS_CONFIG.keys())
        dados = []
        for m in municipios:
            for _ in range(m["q"]):
                dados.append({
                    "id": len(dados),
                    "b": random.choice(bancos),
                    "lat": round(m["lat"] + random.uniform(-0.05, 0.05), 5),
                    "lng": round(m["lng"] + random.uniform(-0.05, 0.05), 5),
                    "s": random.choice([True, True, False]), # Status dinheiro
                    "f": random.choice(["Vazio", "Médio", "Cheio"]),
                    "h": datetime.now().isoformat()
                })
        with open(FILE_NAME, "w") as f: json.dump(dados, f)

@app.on_event("startup")
def startup(): inicializar_base()

def carregar():
    with open(FILE_NAME, "r") as f: return json.load(f)

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    atms = carregar()
    mapa = folium.Map(location=[-8.8383, 13.2344], zoom_start=12, tiles="cartodbpositron", zoom_control=False)
    LocateControl(fly_to=True, keepCurrentZoomLevel=False).add_to(mapa)

    ui = f"""
    <style>
        #header {{ position: fixed; top: 15px; left: 50%; transform: translateX(-50%); width: 90%; max-width: 450px; background: white; z-index: 10000; padding: 14px; border-radius: 40px; box-shadow: 0 5px 25px rgba(0,0,0,0.2); display: flex; justify-content: space-between; align-items: center; font-family: sans-serif; }}
        .badge {{ font-size: 10px; padding: 2px 8px; border-radius: 10px; color: white; font-weight: bold; }}
        .f-vazio {{ background: #27ae60; }} .f-medio {{ background: #f1c40f; color: black; }} .f-cheio {{ background: #e67e22; }}
    </style>
    <div id="header">
        <b onclick="location.reload()" style="cursor:pointer; font-size:20px;">🔄</b>
        <span style="font-weight: 900; letter-spacing: 1px;">🏧 DINHEIRO <span style="color:#27ae60;">AKI</span></span>
        <div style="background: #f0f0f0; padding: 5px 12px; border-radius: 20px; font-size: 12px; font-weight: bold;">{len(atms)}</div>
    </div>
    <script>
        var atms_data = {json.dumps(atms)};
        var config = {json.dumps(BANCOS_CONFIG)};

        window.onload = function() {{
            var m = window[document.querySelector('.folium-map').id];
            var cluster = L.markerClusterGroup({{ chunkedLoading: true, spiderfyOnMaxZoom: true }});
            
            atms_data.forEach(function(a) {{
                var corStatus = a.s ? '#27ae60' : '#e74c3c';
                var corBanco = config[a.b].cor;
                
                var icon = L.divIcon({{
                    html: `<div style="background:${{corBanco}}; border: 3px solid ${{corStatus}}; width:32px; height:32px; border-radius:50%; color:white; font-size:9px; display:flex; align-items:center; justify-content:center; font-weight:bold; box-shadow: 0 3px 6px rgba(0,0,0,0.16);">${{a.b}}</div>`,
                    className: '', iconSize: [32, 32]
                }});

                var marker = L.marker([a.lat, a.lng], {{icon: icon}});
                marker.bindPopup(`
                    <div style="text-align:center; font-family:sans-serif; width:200px;">
                        <b style="font-size:18px; color:${{corBanco}}">${{a.b}}</b><br>
                        <span style="color:${{corStatus}}; font-weight:bold;">${{a.s ? '● COM DINHEIRO' : '○ SEM DINHEIRO'}}</span><br>
                        Fila: <span class="badge ${{a.f == 'Vazio' ? 'f-vazio' : a.f == 'Médio' ? 'f-medio' : 'f-cheio'}}">${{a.f}}</span><hr>
                        <button onclick="window.open('https://www.google.com/maps/dir/?api=1&destination=${{a.lat}},${{a.lng}}')" style="background:#2c3e50; color:white; border:none; padding:12px; border-radius:20px; cursor:pointer; width:100%; font-weight:bold;">🚀 NAVEGAR AGORA</button>
                        <div style="margin-top:10px; display:flex; gap:5px;">
                            <button onclick="updateStatus(${{a.id}}, ${{!a.s}})" style="flex:1; font-size:10px; padding:5px; border:none; background:#eee; border-radius:5px;">ADM</button>
                        </div>
                    </div>
                `);
                cluster.addLayer(marker);
            }});
            m.addLayer(cluster);
        }};

        function updateStatus(id, newStatus) {{
            var pin = prompt("PIN ADMINISTRATIVO:");
            if(pin) window.location.href = "/up_s?id="+id+"&s="+newStatus+"&pin="+pin;
        }}
    </script>
    """
    mapa.get_root().header.add_child(folium.Element(ui))
    return HTMLResponse(content=mapa._repr_html_())

@app.get("/up_s")
def up_s(id: int, s: str, pin: str):
    if pin != ADMIN_PIN_SERVER:
        return HTMLResponse("PIN INVÁLIDO", status_code=403)
    d = carregar()
    for a in d:
        if a["id"] == id:
            a["s"] = (s.lower() == "true")
            a["h"] = datetime.now().isoformat()
            break
    with open(FILE_NAME, "w") as f: json.dump(d, f)
    return RedirectResponse(url="/?t=" + str(time.time()))
