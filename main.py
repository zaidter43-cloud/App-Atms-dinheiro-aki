from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import folium
from folium.plugins import LocateControl, Search, MarkerCluster
import json
import os
from datetime import datetime

app = FastAPI()
FILE_NAME = "database_v30.json"
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
    try:
        with open(FILE_NAME, "r") as f: return json.load(f)
    except: return []

def salvar_dados(dados):
    with open(FILE_NAME, "w") as f: json.dump(dados, f, indent=4)

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
        #loader {{
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: white; z-index: 30000;
            display: flex; align-items: center; justify-content: center;
            flex-direction: column; font-family: sans-serif;
        }}
        .spin {{ width: 50px; height: 50px; border: 5px solid #f3f3f3; border-top: 5px solid #27ae60; border-radius: 50%; animation: s 1s linear infinite; }}
        @keyframes s {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
        #app-header {{
            position: fixed; top: 15px; left: 50%; transform: translateX(-50%);
            width: 90%; max-width: 400px; background: white; z-index: 10000;
            padding: 12px; border-radius: 30px; display: flex; align-items: center; justify-content: space-between;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2); font-family: sans-serif;
        }}
        .info-row {{ margin-bottom: 5px; font-size: 12px; }}
        .badge {{ font-size: 11px; padding: 2px 10px; border-radius: 10px; color: white; font-weight: bold; }}
        .f-vazio {{ background: #27ae60; }} .f-medio {{ background: #f1c40f; color: black; }} .f-cheio {{ background: #e67e22; }}
    </style>

    <div id="loader"><div class="spin"></div><p style="color:#27ae60; margin-top:15px; font-weight:bold;">A preparar mapa...</p></div>

    <div id="app-header">
        <div onclick="showL(); location.reload()" style="cursor:pointer; font-size:20px;">🔄</div>
        <div style="font-weight: 800; font-size:16px;">🏧 DINHEIRO <span style="color:#27ae60;">AKI</span></div>
        <div onclick="partilhar()" style="cursor:pointer; font-size:20px;">🔗</div>
    </div>

    <script>
        // Esconder loader quando o mapa carregar
        window.onload = function() {{ setTimeout(() => {{ document.getElementById('loader').style.display = 'none'; }}, 1000); }};
        
        var uLat = -8.8383, uLng = 13.2344;
        navigator.geolocation.getCurrentPosition(function(p){{ uLat=p.coords.latitude; uLng=p.coords.longitude; }});

        function showL() {{ document.getElementById('loader').style.display = 'flex'; }}

        function partilhar() {{
            alert("Partilha Direta: Disponível em breve! Por enquanto, copie o link do navegador.");
        }}

        function ir(lat, lng) {{
            showL();
            try {{
                var m = window[document.querySelector('.folium-map').id];
                if (window.rC) {{ m.removeControl(window.rC); }}
                window.rC = L.Routing.control({{
                    waypoints: [L.latLng(uLat, uLng), L.latLng(lat, lng)],
                    lineOptions: {{ styles: [{{color: '#27ae60', weight: 7, opacity: 0.8}}] }},
                    createMarker: function() {{ return null; }}
                }}).addTo(m);
                m.closePopup();
            }} catch(e) {{ console.log(e); }}
            setTimeout(() => {{ document.getElementById('loader').style.display = 'none'; }}, 800);
        }}

        function setF(id) {{
            var r = prompt("ESTADO DA FILA:\\n1 - Vazio (Livre)\\n2 - Médio (15 min)\\n3 - Cheio (Muita gente)");
            if(r) {{ showL(); var f = r=="1"?"Vazio":r=="2"?"Médio":"Cheio"; window.location.href="/up_f?id="+id+"&f="+f; }}
        }}

        function upA(id, s) {{
            var p = prompt("PIN ADMINISTRATIVO:");
            if(p == "{ADMIN_PIN}") {{ showL(); window.location.href="/up_s?id="+id+"&s="+s; }}
            else if(p !== null) {{ alert("PIN Incorreto!"); }}
        }}
    </script>
    """
    mapa.get_root().header.add_child(folium.Element(ui_content))

    cluster = MarkerCluster(name="Bancos").add_to(mapa)
    for atm in atms:
        cor = "#27ae60" if atm["dinheiro"] else "#e74c3c"
        tempo = calcular_tempo(atm["hora"])
        f_class = f"f-{atm['fila'].lower()}"
        
        icon_html = f'<div style="background:{cor}; border:2px solid white; border-radius:50%; width:36px; height:36px; display:flex; align-items:center; justify-content:center; color:white; font-weight:bold; font-size:10px;">{atm["banco"]}</div>'
        
        pop = f"""
        <div style="text-align:center; font-family:sans-serif; min-width:210px; padding:5px;">
            <b style="font-size:18px; color:#2c3e50;">{atm["banco"]}</b><br>
            <small style="color:#7f8c8d;">{atm["zona"]}</small><hr style="border:0.5px solid #eee;">
            
            <div class="info-row">
                <span style="color:#7f8c8d;">Notas:</span> <b style="color:{cor};">{tempo}</b>
            </div>
            <div class="info-row">
                <span style="color:#7f8c8d;">Fila:</span> <span class="badge {f_class}">{atm['fila']}</span>
            </div>
            
            <button onclick="ir({atm['lat']}, {atm['lng']})" style="background:#2c3e50; color:white; border:none; border-radius:20px; padding:12px; width:100%; font-weight:bold; cursor:pointer; margin:10px 0;">🚀 MOSTRAR CAMINHO</button>
            
            <div style="display:flex; gap:5px; justify-content:center; margin-top:5px;">
                <button onclick="setF({atm['id']})" style="font-size:10px; padding:8px; border:1px solid #ccc; background:white; border-radius:8px; flex:1;">📊 Atualizar Fila</button>
                <button onclick="upA({atm['id']}, '{not atm['dinheiro']}')" style="font-size:10px; border:1px solid #ddd; background:#f9f9f9; border-radius:8px; color:gray; flex:1;">⚙️ Dinheiro (Adm)</button>
            </div>
        </div>
        """
        folium.Marker([atm["lat"], atm["lng"]], popup=folium.Popup(pop, max_width=260), icon=folium.DivIcon(html=icon_html)).add_to(cluster)

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
