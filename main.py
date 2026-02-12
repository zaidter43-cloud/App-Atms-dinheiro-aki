from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import folium
from folium.plugins import MarkerCluster
import json
import os
from datetime import datetime

app = FastAPI()
FILE_NAME = "database_luanda_v31.json"
ADMIN_PIN = "2424"

def carregar_dados():
    if not os.path.exists(FILE_NAME):
        dados = [
            {"id": 0, "banco": "BAI", "muni": "Luanda", "zona": "Mutamba", "lat": -8.8147, "lng": 13.2305, "dinheiro": True, "hora": datetime.now().isoformat(), "fila": "Vazio"},
            {"id": 1, "banco": "BFA", "muni": "Luanda", "zona": "Maianga", "lat": -8.8300, "lng": 13.2350, "dinheiro": True, "hora": datetime.now().isoformat(), "fila": "Médio"},
            {"id": 2, "banco": "BIC", "muni": "Talatona", "zona": "Belas Shopping", "lat": -8.9285, "lng": 13.1785, "dinheiro": True, "hora": datetime.now().isoformat(), "fila": "Cheio"},
            {"id": 3, "banco": "ATL", "muni": "Viana", "zona": "Estalagem", "lat": -8.9100, "lng": 13.3600, "dinheiro": False, "hora": datetime.now().isoformat(), "fila": "Vazio"},
            {"id": 4, "banco": "SOL", "muni": "Kilamba", "zona": "Quarteirão X", "lat": -8.9980, "lng": 13.2700, "dinheiro": True, "hora": datetime.now().isoformat(), "fila": "Médio"},
            {"id": 5, "banco": "BPC", "muni": "Samba", "zona": "Av. Reuvers", "lat": -8.8550, "lng": 13.2150, "dinheiro": False, "hora": datetime.now().isoformat(), "fila": "Vazio"},
            {"id": 6, "banco": "KEVE", "muni": "Alvalade", "zona": "Igreja Sagrada Família", "lat": -8.8380, "lng": 13.2420, "dinheiro": True, "hora": datetime.now().isoformat(), "fila": "Vazio"},
            {"id": 7, "banco": "ECONO", "muni": "Luanda", "zona": "Kinaxixi", "lat": -8.8180, "lng": 13.2380, "dinheiro": True, "hora": datetime.now().isoformat(), "fila": "Cheio"},
            {"id": 8, "banco": "BAI", "muni": "Morro Bento", "zona": "Gamek", "lat": -8.8850, "lng": 13.2050, "dinheiro": True, "hora": datetime.now().isoformat(), "fila": "Médio"},
            {"id": 9, "banco": "BFA", "muni": "Benfica", "zona": "Kero Benfica", "lat": -8.9450, "lng": 13.1900, "dinheiro": True, "hora": datetime.now().isoformat(), "fila": "Vazio"}
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
    mapa = folium.Map(location=[-8.8383, 13.2344], zoom_start=13, tiles="cartodbpositron", zoom_control=False)

    ui = f"""
    <link rel="stylesheet" href="https://unpkg.com/leaflet-routing-machine/dist/leaflet-routing-machine.css" />
    <script src="https://unpkg.com/leaflet-routing-machine/dist/leaflet-routing-machine.js"></script>
    <style>
        .leaflet-routing-container {{ display: none !important; }}
        #loader {{
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: white; z-index: 30000; display: flex; align-items: center; justify-content: center;
            flex-direction: column; font-family: sans-serif;
        }}
        .spin {{ width: 40px; height: 40px; border: 4px solid #f3f3f3; border-top: 4px solid #27ae60; border-radius: 50%; animation: s 0.6s linear infinite; }}
        @keyframes s {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
        #app-header {{
            position: fixed; top: 15px; left: 50%; transform: translateX(-50%);
            width: 90%; max-width: 400px; background: white; z-index: 10000;
            padding: 12px; border-radius: 30px; display: flex; align-items: center; justify-content: space-between;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2); font-family: sans-serif;
        }}
        .badge {{ font-size: 11px; padding: 2px 10px; border-radius: 10px; color: white; font-weight: bold; }}
        .f-vazio {{ background: #27ae60; }} .f-medio {{ background: #f1c40f; color: black; }} .f-cheio {{ background: #e67e22; }}
    </style>

    <div id="loader"><div class="spin"></div></div>

    <div id="app-header">
        <div onclick="showL(); location.reload()" style="cursor:pointer;">🔄</div>
        <div style="font-weight: 800;">🏧 DINHEIRO <span style="color:#27ae60;">AKI</span></div>
        <div onclick="alert('Partilha brevemente disponível!')" style="cursor:pointer;">🔗</div>
    </div>

    <script>
        window.onload = function() {{ document.getElementById('loader').style.display = 'none'; }};
        var uLat = -8.8383, uLng = 13.2344;
        navigator.geolocation.getCurrentPosition(function(p){{ uLat=p.coords.latitude; uLng=p.coords.longitude; }});

        function showL() {{ document.getElementById('loader').style.display = 'flex'; }}

        function ir(lat, lng) {{
            showL();
            var m = window[document.querySelector('.folium-map').id];
            if (window.rC) {{ m.removeControl(window.rC); }}
            window.rC = L.Routing.control({{
                waypoints: [L.latLng(uLat, uLng), L.latLng(lat, lng)],
                lineOptions: {{ styles: [{{color: '#27ae60', weight: 8, opacity: 0.9}}] }}
            }}).addTo(m);
            m.closePopup();
            setTimeout(() => {{ document.getElementById('loader').style.display = 'none'; }}, 500);
        }}

        function setF(id) {{
            var r = prompt("Fila: 1-Vazio | 2-Médio | 3-Cheio");
            if(r) {{ showL(); var f = r=="1"?"Vazio":r=="2"?"Médio":"Cheio"; window.location.href="/up_f?id="+id+"&f="+f; }}
        }}

        function upA(id, s) {{
            if(prompt("PIN:") == "{ADMIN_PIN}") {{ showL(); window.location.href="/up_s?id="+id+"&s="+s; }}
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
        
        icon = f'<div style="background:{cor}; border:2px solid white; border-radius:50%; width:34px; height:34px; color:white; font-weight:bold; font-size:9px; display:flex; align-items:center; justify-content:center;">{atm["banco"]}</div>'
        
        pop = f"""
        <div style="text-align:center; font-family:sans-serif; width:190px;">
            <b>{atm["banco"]} - {atm["zona"]}</b><hr>
            <div style="margin:5px 0;">Notas: <b style="color:{cor};">{tempo}</b></div>
            <div style="margin:5px 0;">Fila: <span class="badge {f_class}">{f_txt}</span></div>
            <button onclick="ir({atm['lat']}, {atm['lng']})" style="background:#2c3e50; color:white; border:none; border-radius:20px; padding:10px; width:100%; font-weight:bold; cursor:pointer; margin-top:5px;">🚀 MOSTRAR CAMINHO</button>
            <div style="display:flex; gap:5px; margin-top:10px;">
                <button onclick="setF({atm['id']})" style="font-size:9px; padding:5px; flex:1; border-radius:5px; border:1px solid #ccc;">📊 Fila</button>
                <button onclick="upA({atm['id']}, '{not atm['dinheiro']}')" style="font-size:9px; padding:5px; flex:1; border-radius:5px; border:none; color:gray;">⚙️ Admin</button>
            </div>
        </div>
        """
        folium.Marker([atm["lat"], atm["lng"]], popup=folium.Popup(pop, max_width=250), icon=folium.DivIcon(html=icon)).add_to(cluster)

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
