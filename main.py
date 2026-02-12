from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import folium
from folium.plugins import LocateControl, Search, MarkerCluster
import json
import os
from datetime import datetime

app = FastAPI()
FILE_NAME = "database_v28.json"
ADMIN_PIN = "2424"

def carregar_dados():
    if not os.path.exists(FILE_NAME):
        dados = [
            {"id": 0, "banco": "BAI", "muni": "Luanda", "zona": "Marginal", "lat": -8.8120, "lng": 13.2300, "dinheiro": True, "votos": 10, "hora": datetime.now().isoformat(), "fila": "Vazio"},
            {"id": 1, "banco": "BFA", "muni": "Luanda", "zona": "Maianga", "lat": -8.8315, "lng": 13.2325, "dinheiro": True, "votos": 25, "hora": datetime.now().isoformat(), "fila": "Médio"},
            {"id": 2, "banco": "BIC", "muni": "Talatona", "zona": "Belas Shopping", "lat": -8.9280, "lng": 13.1780, "dinheiro": True, "votos": 14, "hora": datetime.now().isoformat(), "fila": "Cheio"}
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

    ui_content = f"""
    <link rel="stylesheet" href="https://unpkg.com/leaflet-routing-machine/dist/leaflet-routing-machine.css" />
    <script src="https://unpkg.com/leaflet-routing-machine/dist/leaflet-routing-machine.js"></script>
    <style>
        .leaflet-routing-container {{ display: none !important; }}
        #loader-container {{
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(255,255,255,0.8); z-index: 20000;
            display: none; align-items: center; justify-content: center;
            flex-direction: column; font-family: sans-serif;
        }}
        .spinner {{ width: 40px; height: 40px; border: 4px solid #f3f3f3; border-top: 4px solid #27ae60; border-radius: 50%; animation: spin 1s linear infinite; }}
        @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
        #app-header {{
            position: fixed; top: 15px; left: 50%; transform: translateX(-50%);
            width: 90%; max-width: 400px; background: white; z-index: 10000;
            padding: 12px; border-radius: 30px; display: flex; align-items: center; justify-content: space-between;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2); font-family: sans-serif;
        }}
        .badge {{ font-size: 10px; padding: 2px 8px; border-radius: 10px; color: white; font-weight: bold; margin-top: 5px; display: inline-block; }}
        .f-vazio {{ background: #27ae60; }} .f-medio {{ background: #f1c40f; color: black; }} .f-cheio {{ background: #e67e22; }}
    </style>

    <div id="loader-container"><div class="spinner"></div><p style="color:#27ae60; margin-top:10px;">A processar...</p></div>

    <div id="app-header">
        <div onclick="location.reload()" style="cursor:pointer; font-size:18px;">🔄</div>
        <div style="font-weight: 800; font-size:15px;">🏧 DINHEIRO <span style="color:#27ae60;">AKI</span></div>
        <div onclick="partilhar()" style="cursor:pointer; font-size:18px;">🔗</div>
    </div>

    <script>
        var uLat = -8.8383, uLng = 13.2344;
        navigator.geolocation.getCurrentPosition(function(p){{ uLat=p.coords.latitude; uLng=p.coords.longitude; }});

        function showL() {{ document.getElementById('loader-container').style.display = 'flex'; }}

        function partilhar() {{
            if (navigator.share) {{
                navigator.share({{ title: 'Dinheiro Aki', text: 'Vê ATMs com notas em Luanda!', url: window.location.href }});
            }} else {{ alert("Copia o link: " + window.location.href); }}
        }}

        function ir(lat, lng) {{
            var mId = document.querySelector('.folium-map').id;
            var mInstance = window[mId];
            if (window.rC) {{ mInstance.removeControl(window.rC); }}
            window.rC = L.Routing.control({{
                waypoints: [L.latLng(uLat, uLng), L.latLng(lat, lng)],
                lineOptions: {{ styles: [{{color: '#27ae60', weight: 6}}] }},
                createMarker: function() {{ return null; }}
            }}).addTo(mInstance);
            mInstance.closePopup();
        }}

        function setF(id) {{
            var r = prompt("Fila: 1-Vazio | 2-Médio | 3-Cheio");
            if(r) {{ showL(); var f = r=="1"?"Vazio":r=="2"?"Médio":"Cheio"; window.location.href="/up_f?id="+id+"&f="+f; }}
        }}

        function upA(id, s) {{
            if(prompt("PIN Admin (2424):")=="{ADMIN_PIN}") {{ showL(); window.location.href="/up_s?id="+id+"&s="+s; }}
        }}
    </script>
    """
    mapa.get_root().header.add_child(folium.Element(ui_content))

    cluster = MarkerCluster(name="Bancos").add_to(mapa)
    for atm in atms:
        cor = "#27ae60" if atm["dinheiro"] else "#e74c3c"
        tempo = calcular_tempo(atm["hora"])
        f_class = f"f-{atm['fila'].lower()}"
        
        icon_html = f'<div style="background:{cor}; border:2px solid white; border-radius:50%; width:34px; height:34px; display:flex; align-items:center; justify-content:center; color:white; font-weight:bold; font-size:9px;">{atm["banco"]}</div>'
        
        pop = f"""
        <div style="text-align:center; font-family:sans-serif; min-width:180px;">
            <b style="font-size:16px;">{atm["banco"]}</b><br><small>{atm["zona"]}</small><hr>
            <div style="margin-bottom:8px;">
                <span style="color:{cor}; font-weight:bold; font-size:12px;">{tempo}</span><br>
                <span class="badge {f_class}">Fila: {atm['fila']}</span>
            </div>
            <button onclick="ir({atm['lat']}, {atm['lng']})" style="background:#27ae60; color:white; border:none; border-radius:20px; padding:10px; width:100%; font-weight:bold; cursor:pointer;">🚀 MOSTRAR CAMINHO</button>
            <div style="margin-top:10px; display:flex; gap:5px; justify-content:center;">
                <button onclick="setF({atm['id']})" style="font-size:10px; padding:5px; border:1px solid #ccc; background:white; border-radius:5px;">📊 Atualizar Fila</button>
                <button onclick="upA({atm['id']}, '{not atm['dinheiro']}')" style="font-size:10px; border:1px solid #ddd; background:#f9f9f9; border-radius:5px; color:gray;">⚙️ Status Admin</button>
            </div>
        </div>
        """
        folium.Marker([atm["lat"], atm["lng"]], popup=folium.Popup(pop, max_width=250), icon=folium.DivIcon(html=icon_html), name=f"{atm['banco']} {atm['zona']}").add_to(cluster)

    Search(layer=cluster, geom_type="Point", placeholder="Procurar...", collapsed=False, search_label="name").add_to(mapa)
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
