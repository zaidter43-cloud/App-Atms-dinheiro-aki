from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import folium
from folium.plugins import MarkerCluster, LocateControl
import json
import os
import time
from datetime import datetime

app = FastAPI()
FILE_NAME = "db_v35.json"
ADMIN_PIN = "2424"

def carregar_dados():
    if not os.path.exists(FILE_NAME):
        dados = [
            {"id": 0, "banco": "BAI", "muni": "Luanda", "zona": "Mutamba", "lat": -8.8147, "lng": 13.2305, "dinheiro": True, "hora": datetime.now().isoformat(), "fila": "Vazio"},
            {"id": 1, "banco": "BFA", "muni": "Luanda", "zona": "Maianga", "lat": -8.8300, "lng": 13.2350, "dinheiro": True, "hora": datetime.now().isoformat(), "fila": "Médio"}
        ]
        salvar_dados(dados)
        return dados
    with open(FILE_NAME, "r") as f: return json.load(f)

def salvar_dados(dados):
    with open(FILE_NAME, "w") as f: json.dump(dados, f, indent=4)

@app.get("/", response_class=HTMLResponse)
def mostrar_mapa(request: Request):
    atms = carregar_dados()
    mapa = folium.Map(location=[-8.8383, 13.2344], zoom_start=13, tiles="cartodbpositron", zoom_control=False)
    
    ui = f"""
    <link rel="stylesheet" href="https://unpkg.com/leaflet-routing-machine/dist/leaflet-routing-machine.css" />
    <script src="https://unpkg.com/leaflet-routing-machine/dist/leaflet-routing-machine.js"></script>
    <style>
        #loader {{
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: white; z-index: 99999; display: flex; 
            align-items: center; justify-content: center; flex-direction: column;
        }}
        .spin {{ width: 40px; height: 40px; border: 4px solid #f3f3f3; border-top: 4px solid #27ae60; border-radius: 50%; animation: s 0.8s linear infinite; }}
        @keyframes s {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
        #app-header {{
            position: fixed; top: 10px; left: 50%; transform: translateX(-50%);
            width: 90%; max-width: 400px; background: white; z-index: 1000;
            padding: 10px; border-radius: 25px; display: flex; align-items: center; justify-content: space-between;
            box-shadow: 0 4px 10px rgba(0,0,0,0.2); font-family: sans-serif;
        }}
    </style>

    <div id="loader"><div class="spin"></div><p>A carregar Dinheiro Aki...</p></div>

    <div id="app-header">
        <div onclick="location.reload()" style="cursor:pointer;">🔄</div>
        <div style="font-weight:bold;">🏧 DINHEIRO <span style="color:#27ae60;">AKI</span></div>
        <div onclick="alert('Link: ' + window.location.href)" style="cursor:pointer;">🔗</div>
    </div>

    <script>
        // FORÇA O LOADER A FECHAR EM 3 SEGUNDOS, aconteça o que acontecer
        setTimeout(function(){{ document.getElementById('loader').style.display = 'none'; }}, 3000);

        var uLat = -8.8383, uLng = 13.2344;
        navigator.geolocation.getCurrentPosition(
            function(p){{ uLat=p.coords.latitude; uLng=p.coords.longitude; }},
            function(e){{ console.log("GPS negado"); }}
        );

        function ir(lat, lng) {{
            var m = window[document.querySelector('.folium-map').id];
            if (window.rC) {{ m.removeControl(window.rC); }}
            window.rC = L.Routing.control({{
                waypoints: [L.latLng(uLat, uLng), L.latLng(lat, lng)],
                lineOptions: {{ styles: [{{color: '#27ae60', weight: 7}}] }},
                addWaypoints: false, show: false
            }}).addTo(m);
            m.closePopup();
        }}

        function setF(id) {{
            var r = prompt("Fila: 1-Vazio | 2-Médio | 3-Cheio");
            if(r) {{ window.location.href = "/up_f?id="+id+"&f="+(r=="1"?"Vazio":r=="2"?"Médio":"Cheio"); }}
        }}

        function upA(id, s) {{
            if(prompt("PIN (2424):") == "{ADMIN_PIN}") {{ window.location.href = "/up_s?id="+id+"&s="+s; }}
        }}
    </script>
    """
    mapa.get_root().header.add_child(folium.Element(ui))
    cluster = MarkerCluster().add_to(mapa)

    for atm in atms:
        cor = "#27ae60" if atm["dinheiro"] else "#e74c3c"
        icon = f'<div style="background:{cor}; border:2px solid white; border-radius:50%; width:30px; height:30px; color:white; font-size:9px; display:flex; align-items:center; justify-content:center;">{atm["banco"]}</div>'
        pop = f"""
        <div style="text-align:center; width:180px; font-family:sans-serif;">
            <b>{atm["banco"]}</b><br>{atm["zona"]}<hr>
            Fila: <b>{atm["fila"]}</b><br>
            <button onclick="ir({atm['lat']}, {atm['lng']})" style="background:#2c3e50; color:white; border:none; border-radius:15px; padding:8px; width:100%; margin-top:5px; cursor:pointer;">🚀 ROTA</button>
            <div style="display:flex; gap:3px; margin-top:8px;">
                <button onclick="setF({atm['id']})" style="font-size:9px; flex:1;">📊 Fila</button>
                <button onclick="upA({atm['id']}, '{not atm['dinheiro']}')" style="font-size:9px; flex:1;">⚙️ Adm</button>
            </div>
        </div>
        """
        folium.Marker([atm["lat"], atm["lng"]], popup=folium.Popup(pop), icon=folium.DivIcon(html=icon)).add_to(cluster)

    return HTMLResponse(content=mapa._repr_html_())

@app.get("/up_f")
def up_f(id: int, f: str):
    d = carregar_dados()
    for a in d:
        if a["id"] == id: a["fila"], a["hora"] = f, datetime.now().isoformat(); break
    salvar_dados(d)
    return RedirectResponse(url="/")

@app.get("/up_s")
def up_s(id: int, s: str):
    d = carregar_dados()
    for a in d:
        if a["id"] == id: a["dinheiro"], a["hora"] = (s.lower()=="true"), datetime.now().isoformat(); break
    salvar_dados(d)
    return RedirectResponse(url="/")
