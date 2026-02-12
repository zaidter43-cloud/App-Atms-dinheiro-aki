from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import folium
from folium.plugins import MarkerCluster, LocateControl
import json
import os
import time
from datetime import datetime

app = FastAPI()
FILE_NAME = "database_luanda_v38.json"
# O PIN fica guardado apenas aqui no servidor
ADMIN_PIN_SERVER = "2424"

def carregar_dados():
    if not os.path.exists(FILE_NAME):
        dados = [
            # LUANDA CENTRO
            {"id": 0, "banco": "BAI", "muni": "Luanda", "zona": "Mutamba (Sede)", "lat": -8.8147, "lng": 13.2305, "dinheiro": True, "hora": datetime.now().isoformat(), "fila": "Vazio"},
            {"id": 1, "banco": "BFA", "muni": "Luanda", "zona": "Kinaxixi", "lat": -8.8182, "lng": 13.2381, "dinheiro": True, "hora": datetime.now().isoformat(), "fila": "Médio"},
            {"id": 2, "banco": "BIC", "muni": "Luanda", "zona": "Marginal", "lat": -8.8085, "lng": 13.2330, "dinheiro": True, "hora": datetime.now().isoformat(), "fila": "Vazio"},
            # TALATONA / SAMBA
            {"id": 3, "banco": "SOL", "muni": "Talatona", "zona": "Belas Shopping", "lat": -8.9288, "lng": 13.1782, "dinheiro": True, "hora": datetime.now().isoformat(), "fila": "Cheio"},
            {"id": 4, "banco": "ATL", "muni": "Talatona", "zona": "Via S8", "lat": -8.9220, "lng": 13.1860, "dinheiro": True, "hora": datetime.now().isoformat(), "fila": "Médio"},
            {"id": 5, "banco": "KEVE", "muni": "Samba", "zona": "Corimba", "lat": -8.8750, "lng": 13.1950, "dinheiro": True, "hora": datetime.now().isoformat(), "fila": "Vazio"},
            # VIANA / KILAMBA
            {"id": 6, "banco": "BFA", "muni": "Viana", "zona": "Ponte Amarela", "lat": -8.9020, "lng": 13.3650, "dinheiro": True, "hora": datetime.now().isoformat(), "fila": "Cheio"},
            {"id": 7, "banco": "BAI", "muni": "Kilamba", "zona": "Bloco B", "lat": -8.9970, "lng": 13.2710, "dinheiro": True, "hora": datetime.now().isoformat(), "fila": "Vazio"},
            {"id": 8, "banco": "ECONO", "muni": "Morro Bento", "zona": "Kero", "lat": -8.8920, "lng": 13.2080, "dinheiro": True, "hora": datetime.now().isoformat(), "fila": "Médio"},
            {"id": 9, "banco": "STB", "muni": "Cazenga", "zona": "Mabor", "lat": -8.8450, "lng": 13.2950, "dinheiro": False, "hora": datetime.now().isoformat(), "fila": "Vazio"}
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
    LocateControl(auto_start=False, fly_to=True).add_to(mapa)

    ui = f"""
    <link rel="stylesheet" href="https://unpkg.com/leaflet-routing-machine/dist/leaflet-routing-machine.css" />
    <script src="https://unpkg.com/leaflet-routing-machine/dist/leaflet-routing-machine.js"></script>
    <style>
        .leaflet-routing-container {{ display: none !important; }}
        #progress-bar {{ position: fixed; top: 0; left: 0; width: 100%; height: 4px; background: transparent; z-index: 40000; }}
        #progress-fill {{ height: 100%; width: 0%; background: #27ae60; transition: width 0.4s; }}
        #app-header {{
            position: fixed; top: 15px; left: 50%; transform: translateX(-50%);
            width: 90%; max-width: 450px; background: white; z-index: 10000;
            padding: 12px; border-radius: 35px; display: flex; align-items: center; justify-content: space-between;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15); font-family: sans-serif;
        }}
        .badge {{ font-size: 11px; padding: 3px 10px; border-radius: 12px; color: white; font-weight: bold; }}
        .f-vazio {{ background: #27ae60; }} .f-medio {{ background: #f1c40f; color: black; }} .f-cheio {{ background: #e67e22; }}
    </style>

    <div id="progress-bar"><div id="progress-fill"></div></div>

    <div id="app-header">
        <div onclick="document.getElementById('progress-fill').style.width='100%'; location.reload();" style="cursor:pointer; font-size:20px;">🔄</div>
        <div style="font-weight: 800; font-size:16px;">🏧 DINHEIRO <span style="color:#27ae60;">AKI</span></div>
        <div onclick="alert('Partilha direta disponível em breve!')" style="cursor:pointer; font-size:20px;">🔗</div>
    </div>

    <script>
        var uLat = -8.8383, uLng = 13.2344;
        navigator.geolocation.getCurrentPosition(function(p){{ uLat=p.coords.latitude; uLng=p.coords.longitude; }});

        function ir(lat, lng) {{
            document.getElementById('progress-fill').style.width='100%';
            var m = window[document.querySelector('.folium-map').id];
            if (window.rC) {{ m.removeControl(window.rC); }}
            window.rC = L.Routing.control({{
                waypoints: [L.latLng(uLat, uLng), L.latLng(lat, lng)],
                lineOptions: {{ styles: [{{color: '#2c3e50', weight: 7, opacity: 0.8}}] }},
                addWaypoints: false, fitSelectedRoutes: true, show: false
            }}).addTo(m);
            m.closePopup();
            setTimeout(() => {{ document.getElementById('progress-fill').style.width='0%'; }}, 1000);
        }}

        function setF(id) {{
            var r = prompt("FILA: 1-Vazio | 2-Médio | 3-Cheio");
            if(r) {{ 
                document.getElementById('progress-fill').style.width='100%';
                var f = (r=="1"?"Vazio":(r=="2"?"Médio":"Cheio"));
                window.location.href = "/up_f?id="+id+"&f="+f;
            }}
        }}

        function upA(id, s) {{
            var p = prompt("PIN ADMINISTRATIVO:");
            if(p) {{
                document.getElementById('progress-fill').style.width='100%';
                // Enviamos o PIN para o servidor validar, não validamos no JS
                window.location.href = "/up_s?id="+id+"&s="+s+"&pin="+p;
            }}
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
        
        icon = f'<div style="background:{cor}; border:3px solid white; border-radius:50%; width:36px; height:36px; color:white; font-weight:bold; font-size:10px; display:flex; align-items:center; justify-content:center; box-shadow:0 4px 8px rgba(0,0,0,0.2);">{atm["banco"]}</div>'
        
        pop = f"""
        <div style="text-align:center; font-family:sans-serif; width:220px; padding:10px;">
            <b style="font-size:18px;">{atm["banco"]}</b><br><small style="color:gray;">{atm["zona"]}</small><hr style="border:0.5px solid #eee; margin:10px 0;">
            <div style="margin-bottom:8px;">Notas: <b style="color:{cor};">{tempo}</b></div>
            <div style="margin-bottom:15px;">Fila: <span class="badge {f_class}">{f_txt}</span></div>
            <button onclick="ir({atm['lat']}, {atm['lng']})" style="background:#2c3e50; color:white; border:none; border-radius:20px; padding:12px; width:100%; font-weight:bold; cursor:pointer;">🚀 MOSTRAR CAMINHO</button>
            <div style="display:flex; gap:8px; margin-top:15px;">
                <button onclick="setF({atm['id']})" style="font-size:11px; padding:8px; flex:1; border-radius:10px; border:1px solid #ccc; background:white;">📊 Fila</button>
                <button onclick="upA({atm['id']}, '{not atm['dinheiro']}')" style="font-size:11px; padding:8px; flex:1; border-radius:10px; border:none; color:gray; background:#f9f9f9;">⚙️ Admin</button>
            </div>
        </div>
        """
        folium.Marker([atm["lat"], atm["lng"]], popup=folium.Popup(pop, max_width=300), icon=folium.DivIcon(html=icon)).add_to(cluster)

    return HTMLResponse(content=mapa._repr_html_())

@app.get("/up_f")
def up_f(id: int, f: str):
    d = carregar_dados()
    for a in d:
        if a["id"] == id: a["fila"], a["hora"] = f, datetime.now().isoformat(); break
    salvar_dados(d)
    return RedirectResponse(url="/?t="+str(time.time()))

@app.get("/up_s")
def up_s(id: int, s: str, pin: str):
    # A SEGURANÇA ACONTECE AQUI (SERVER-SIDE)
    if pin != ADMIN_PIN_SERVER:
        return HTMLResponse("PIN INCORRETO! <a href='/'>Voltar</a>", status_code=403)
    
    d = carregar_dados()
    for a in d:
        if a["id"] == id: a["dinheiro"], a["hora"] = (s.lower()=="true"), datetime.now().isoformat(); break
    salvar_dados(d)
    return RedirectResponse(url="/?t="+str(time.time()))
