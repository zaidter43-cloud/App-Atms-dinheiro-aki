from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import folium
from folium.plugins import MarkerCluster, LocateControl
import json
import os
import time
from datetime import datetime

app = FastAPI()
FILE_NAME = "db_fixed_v34.json"
ADMIN_PIN = "2424"

# Memória temporária para evitar "colar" se o disco falhar
_cache_dados = []

def carregar_dados():
    global _cache_dados
    if not os.path.exists(FILE_NAME):
        _cache_dados = [
            {"id": 0, "banco": "BAI", "muni": "Luanda", "zona": "Mutamba", "lat": -8.8147, "lng": 13.2305, "dinheiro": True, "hora": datetime.now().isoformat(), "fila": "Vazio"},
            {"id": 1, "banco": "BFA", "muni": "Luanda", "zona": "Kinaxixi", "lat": -8.8182, "lng": 13.2381, "dinheiro": True, "hora": datetime.now().isoformat(), "fila": "Médio"},
            {"id": 2, "banco": "BIC", "muni": "Talatona", "zona": "Belas Shopping", "lat": -8.9288, "lng": 13.1782, "dinheiro": True, "hora": datetime.now().isoformat(), "fila": "Cheio"}
        ]
        salvar_dados(_cache_dados)
        return _cache_dados
    try:
        with open(FILE_NAME, "r") as f:
            _cache_dados = json.load(f)
            return _cache_dados
    except:
        return _cache_dados if _cache_dados else []

def salvar_dados(dados):
    try:
        with open(FILE_NAME, "w") as f:
            json.dump(dados, f, indent=4)
    except Exception as e:
        print(f"Erro ao salvar: {e}")

@app.get("/", response_class=HTMLResponse)
def mostrar_mapa(request: Request):
    atms = carregar_dados()
    mapa = folium.Map(location=[-8.8383, 13.2344], zoom_start=12, tiles="cartodbpositron", zoom_control=False)
    
    LocateControl(auto_start=False, fly_to=True).add_to(mapa)

    ui = f"""
    <link rel="stylesheet" href="https://unpkg.com/leaflet-routing-machine/dist/leaflet-routing-machine.css" />
    <script src="https://unpkg.com/leaflet-routing-machine/dist/leaflet-routing-machine.js"></script>
    <style>
        .leaflet-routing-container {{ display: none !important; }}
        #loader-overlay {{
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(255,255,255,0.9); z-index: 50000;
            display: none; align-items: center; justify-content: center; font-family: sans-serif;
        }}
        .bar-container {{ width: 80%; background: #eee; height: 4px; border-radius: 2px; overflow: hidden; }}
        .bar-fill {{ width: 30%; height: 100%; background: #27ae60; animation: progress 0.8s infinite linear; }}
        @keyframes progress {{ 0% {{ margin-left: -30%; }} 100% {{ margin-left: 100%; }} }}
        
        #app-header {{
            position: fixed; top: 15px; left: 50%; transform: translateX(-50%);
            width: 90%; max-width: 400px; background: white; z-index: 10000;
            padding: 12px; border-radius: 30px; display: flex; align-items: center; justify-content: space-between;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2); font-family: sans-serif;
        }}
    </style>

    <div id="loader-overlay">
        <div style="width: 100%; text-align: center;">
            <div class="bar-container" style="margin: 0 auto;"><div class="bar-fill"></div></div>
            <p style="color: #27ae60; font-weight: bold; margin-top: 10px;">A atualizar dados...</p>
        </div>
    </div>

    <div id="app-header">
        <div onclick="execAction(() => location.reload())" style="cursor:pointer; font-size:20px;">🔄</div>
        <div style="font-weight: 800;">🏧 DINHEIRO <span style="color:#27ae60;">AKI</span></div>
        <div onclick="alert('Partilha disponível em breve!')" style="cursor:pointer; font-size:20px;">🔗</div>
    </div>

    <script>
        function execAction(callback) {{
            document.getElementById('loader-overlay').style.display = 'flex';
            setTimeout(callback, 100);
        }}

        var uLat = -8.8383, uLng = 13.2344;
        navigator.geolocation.getCurrentPosition(function(p){{ uLat=p.coords.latitude; uLng=p.coords.longitude; }});

        function ir(lat, lng) {{
            execAction(() => {{
                var m = window[document.querySelector('.folium-map').id];
                if (window.rC) {{ m.removeControl(window.rC); }}
                window.rC = L.Routing.control({{
                    waypoints: [L.latLng(uLat, uLng), L.latLng(lat, lng)],
                    lineOptions: {{ styles: [{{color: '#27ae60', weight: 8}}] }},
                    addWaypoints: false, fitSelectedRoutes: true, show: false
                }}).addTo(m);
                m.closePopup();
                document.getElementById('loader-overlay').style.display = 'none';
            }});
        }}

        function setF(id) {{
            var r = prompt("FILA: 1-Vazio | 2-Médio | 3-Cheio");
            if(r) {{ 
                execAction(() => {{
                    var f = (r=="1"?"Vazio":(r=="2"?"Médio":"Cheio"));
                    window.location.href = "/up_f?id="+id+"&f="+f + "&t=" + Date.now();
                }});
            }}
        }}

        function upA(id, s) {{
            if(prompt("PIN ADMIN:") == "{ADMIN_PIN}") {{ 
                execAction(() => {{
                    window.location.href = "/up_s?id="+id+"&s="+s + "&t=" + Date.now();
                }});
            }}
        }}
    </script>
    """
    mapa.get_root().header.add_child(folium.Element(ui))

    cluster = MarkerCluster().add_to(mapa)
    for atm in atms:
        cor = "#27ae60" if atm["dinheiro"] else "#e74c3c"
        # Lógica de tempo simplificada para evitar bugs de cálculo
        try:
            diff = (datetime.now() - datetime.fromisoformat(atm["hora"])).total_seconds() / 60
            tempo = f"há {int(diff)}m" if diff < 60 else f"há {int(diff//60)}h"
            if diff < 1: tempo = "agora"
        except: tempo = "--"
        
        f_txt = atm.get("fila", "Vazio")
        
        icon = f'<div style="background:{cor}; border:2px solid white; border-radius:50%; width:36px; height:36px; color:white; font-weight:bold; font-size:10px; display:flex; align-items:center; justify-content:center;">{atm["banco"]}</div>'
        
        pop = f"""
        <div style="text-align:center; font-family:sans-serif; width:200px;">
            <b>{atm["banco"]}</b><br><small>{atm["zona"]}</small><hr>
            <div>Notas: <b style="color:{cor};">{tempo}</b></div>
            <div style="margin:5px 0;">Fila: <b>{f_txt}</b></div>
            <button onclick="ir({atm['lat']}, {atm['lng']})" style="background:#2c3e50; color:white; border:none; border-radius:20px; padding:10px; width:100%; font-weight:bold; cursor:pointer;">🚀 CAMINHO</button>
            <div style="display:flex; gap:5px; margin-top:10px;">
                <button onclick="setF({atm['id']})" style="font-size:10px; padding:5px; flex:1; border-radius:5px; border:1px solid #ccc;">📊 Fila</button>
                <button onclick="upA({atm['id']}, '{not atm['dinheiro']}')" style="font-size:10px; padding:5px; flex:1; border:none; color:gray;">⚙️ Status</button>
            </div>
        </div>
        """
        folium.Marker([atm["lat"], atm["lng"]], popup=folium.Popup(pop), icon=folium.DivIcon(html=icon)).add_to(cluster)

    return HTMLResponse(content=mapa._repr_html_())

@app.get("/up_f")
def up_f(id: int, f: str):
    d = carregar_dados()
    for a in d:
        if a["id"] == id:
            a["fila"], a["hora"] = f, datetime.now().isoformat()
            break
    salvar_dados(d)
    time.sleep(0.5) # Delay para o Render não bugar
    return RedirectResponse(url="/?v=" + str(time.time()))

@app.get("/up_s")
def up_s(id: int, s: str):
    d = carregar_dados()
    for a in d:
        if a["id"] == id:
            a["dinheiro"], a["hora"] = (s.lower()=="true"), datetime.now().isoformat()
            break
    salvar_dados(d)
    time.sleep(0.5)
    return RedirectResponse(url="/?v=" + str(time.time()))
