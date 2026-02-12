from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import folium
from folium.plugins import MarkerCluster, LocateControl
import json
import os
from datetime import datetime

app = FastAPI()
FILE_NAME = "db_luanda_v32.json"
ADMIN_PIN = "2424"

def carregar_dados():
    if not os.path.exists(FILE_NAME):
        dados = [
            # LUANDA CENTRO
            {"id": 0, "banco": "BAI", "muni": "Luanda", "zona": "Mutamba", "lat": -8.8147, "lng": 13.2305, "dinheiro": True, "hora": datetime.now().isoformat(), "fila": "Vazio"},
            {"id": 1, "banco": "BFA", "muni": "Luanda", "zona": "Kinaxixi", "lat": -8.8180, "lng": 13.2385, "dinheiro": True, "hora": datetime.now().isoformat(), "fila": "Médio"},
            {"id": 2, "banco": "BIC", "muni": "Luanda", "zona": "Marginal", "lat": -8.8090, "lng": 13.2320, "dinheiro": True, "hora": datetime.now().isoformat(), "fila": "Vazio"},
            # TALATONA / MORRO BENTO
            {"id": 3, "banco": "BAI", "muni": "Talatona", "zona": "Belas Shopping", "lat": -8.9285, "lng": 13.1785, "dinheiro": True, "hora": datetime.now().isoformat(), "fila": "Cheio"},
            {"id": 4, "banco": "BFA", "muni": "Talatona", "zona": "Centro Logístico", "lat": -8.9210, "lng": 13.1850, "dinheiro": True, "hora": datetime.now().isoformat(), "fila": "Médio"},
            {"id": 5, "banco": "SOL", "muni": "Morro Bento", "zona": "Kero", "lat": -8.8870, "lng": 13.2010, "dinheiro": True, "hora": datetime.now().isoformat(), "fila": "Vazio"},
            # KILAMBA / CAMAMA
            {"id": 6, "banco": "ATL", "muni": "Kilamba", "zona": "Quarteirão X", "lat": -8.9980, "lng": 13.2700, "dinheiro": True, "hora": datetime.now().isoformat(), "fila": "Médio"},
            {"id": 7, "banco": "BPC", "muni": "Camama", "zona": "Jardim do Éden", "lat": -8.9350, "lng": 13.2550, "dinheiro": False, "hora": datetime.now().isoformat(), "fila": "Vazio"},
            # VIANA
            {"id": 8, "banco": "BIC", "muni": "Viana", "zona": "Ponte Amarela", "lat": -8.9020, "lng": 13.3650, "dinheiro": True, "hora": datetime.now().isoformat(), "fila": "Cheio"},
            {"id": 9, "banco": "BAI", "muni": "Viana", "zona": "Viana Park", "lat": -8.9150, "lng": 13.3550, "dinheiro": True, "hora": datetime.now().isoformat(), "fila": "Vazio"}
        ]
        salvar_dados(dados)
        return dados
    with open(FILE_NAME, "r") as f: return json.load(f)

def salvar_dados(dados):
    with open(FILE_NAME, "w") as f: json.dump(dados, f, indent=4)

def calcular_tempo(iso_date):
    try:
        diff = datetime.now() - datetime.fromisoformat(iso_date)
        minutos = int(diff.total_seconds() / 60)
        if minutos < 1: return "agora"
        if minutos < 60: return f"{minutos}m"
        return f"{minutos // 60}h"
    except: return "--"

@app.get("/", response_class=HTMLResponse)
def mostrar_mapa(request: Request):
    atms = carregar_dados()
    mapa = folium.Map(location=[-8.8383, 13.2344], zoom_start=12, tiles="cartodbpositron", zoom_control=False)
    
    LocateControl(auto_start=False, fly_to=True, keep_current_zoom_level=True).add_to(mapa)

    ui = f"""
    <link rel="stylesheet" href="https://unpkg.com/leaflet-routing-machine/dist/leaflet-routing-machine.css" />
    <script src="https://unpkg.com/leaflet-routing-machine/dist/leaflet-routing-machine.js"></script>
    <style>
        .leaflet-routing-container {{ display: none !important; }}
        #loader {{
            position: fixed; top: 0; left: 0; width: 100%; height: 3px;
            background: #27ae60; z-index: 40000; display: none;
            animation: load 1s infinite linear; transform-origin: 0% 50%;
        }}
        @keyframes load {{ 0% {{ transform: scaleX(0); }} 50% {{ transform: scaleX(0.5); }} 100% {{ transform: scaleX(1); }} }}
        #app-header {{
            position: fixed; top: 15px; left: 50%; transform: translateX(-50%);
            width: 90%; max-width: 400px; background: white; z-index: 10000;
            padding: 12px; border-radius: 30px; display: flex; align-items: center; justify-content: space-between;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2); font-family: sans-serif;
        }}
        .badge {{ font-size: 11px; padding: 3px 10px; border-radius: 12px; color: white; font-weight: bold; display: inline-block; }}
        .f-vazio {{ background: #27ae60; }} .f-medio {{ background: #f1c40f; color: black; }} .f-cheio {{ background: #e67e22; }}
    </style>

    <div id="loader"></div>

    <div id="app-header">
        <div onclick="showL(); location.reload()" style="cursor:pointer; font-size:20px;">🔄</div>
        <div style="font-weight: 800; font-size:16px; letter-spacing:-0.5px;">🏧 DINHEIRO <span style="color:#27ae60;">AKI</span></div>
        <div onclick="alert('Partilha brevemente disponível!')" style="cursor:pointer; font-size:20px;">🔗</div>
    </div>

    <script>
        var uLat = -8.8383, uLng = 13.2344;
        navigator.geolocation.getCurrentPosition(function(p){{ uLat=p.coords.latitude; uLng=p.coords.longitude; }});

        function showL() {{ document.getElementById('loader').style.display = 'block'; }}

        function ir(lat, lng) {{
            showL();
            var m = window[document.querySelector('.folium-map').id];
            if (window.rC) {{ m.removeControl(window.rC); }}
            window.rC = L.Routing.control({{
                waypoints: [L.latLng(uLat, uLng), L.latLng(lat, lng)],
                lineOptions: {{ styles: [{{color: '#2c3e50', weight: 8, opacity: 0.8}}] }},
                addWaypoints: false, draggableWaypoints: false, fitSelectedRoutes: true, show: false
            }}).addTo(m);
            m.closePopup();
            setTimeout(() => {{ document.getElementById('loader').style.display = 'none'; }}, 800);
        }}

        function setF(id) {{
            var r = prompt("FILA: 1-Vazio | 2-Médio | 3-Cheio");
            if(r) {{ showL(); var f = (r=="1"?"Vazio":(r=="2"?"Médio":"Cheio")); window.location.href="/up_f?id="+id+"&f="+f; }}
        }}

        function upA(id, s) {{
            if(prompt("PIN ADMIN:") == "{ADMIN_PIN}") {{ showL(); window.location.href="/up_s?id="+id+"&s="+s; }}
        }}
    </script>
    """
    mapa.get_root().header.add_child(folium.Element(ui))

    cluster = MarkerCluster().add_to(mapa)
    for atm in atms:
        cor = "#27ae60" if atm["dinheiro"] else "#e74c3c"
        tempo = calcular_tempo(atm["hora"])
        f_txt = atm.get("fila", "Vazio")
        f_class = f"f-{f_txt.lower()}"
        
        icon = f'<div style="background:{cor}; border:2px solid white; border-radius:50%; width:36px; height:36px; color:white; font-weight:bold; font-size:10px; display:flex; align-items:center; justify-content:center; box-shadow:0 2px 5px rgba(0,0,0,0.2);">{atm["banco"]}</div>'
        
        pop = f"""
        <div style="text-align:center; font-family:sans-serif; width:200px; padding:5px;">
            <b style="font-size:16px;">{atm["banco"]}</b><br><small style="color:gray;">{atm["zona"]}</small><hr style="border:0.5px solid #eee; margin:10px 0;">
            <div style="margin-bottom:8px; font-size:13px;">Notas: <b style="color:{cor};">{tempo}</b></div>
            <div style="margin-bottom:12px;">Fila: <span class="badge {f_class}">{f_txt}</span></div>
            <button onclick="ir({atm['lat']}, {atm['lng']})" style="background:#2c3e50; color:white; border:none; border-radius:20px; padding:12px; width:100%; font-weight:bold; cursor:pointer;">🚀 MOSTRAR CAMINHO</button>
            <div style="display:flex; gap:5px; margin-top:12px;">
                <button onclick="setF({atm['id']})" style="font-size:10px; padding:8px; flex:1; border-radius:8px; border:1px solid #ccc; background:white;">📊 Fila</button>
                <button onclick="upA({atm['id']}, '{not atm['dinheiro']}')" style="font-size:10px; padding:8px; flex:1; border-radius:8px; border:none; color:gray; background:#f5f5f5;">⚙️ Admin</button>
            </div>
        </div>
        """
        folium.Marker([atm["lat"], atm["lng"]], popup=folium.Popup(pop, max_width=280), icon=folium.DivIcon(html=icon)).add_to(cluster)

    return HTMLResponse(content=mapa._repr_html_())

@app.get("/up_f")
def up_f(id: int, f: str):
    d = carregar_dados()
    for a in d:
        if a["id"] == id: a["fila"], a["hora"] = f, datetime.now().isoformat(); break
    salvar_dados(d); return RedirectResponse(url="/")

@app.get("/up_s")
def up_s(id: int, s: str):
    d = carregar_dados()
    for a in d:
        if a["id"] == id: a["dinheiro"], a["hora"] = (s.lower()=="true"), datetime.now().isoformat(); break
    salvar_dados(d); return RedirectResponse(url="/")
