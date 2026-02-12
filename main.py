from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import folium
from folium.plugins import MarkerCluster, LocateControl
import json
import os
import time
from datetime import datetime

app = FastAPI()
FILE_NAME = "db_luanda_v45.json"
ADMIN_PIN_SERVER = "2424"

# Configuração de Cores Oficiais
BANCOS_CONFIG = {
    "BAI": "#004a99", "BFA": "#ff6600", "BIC": "#e30613", 
    "SOL": "#f9b233", "ATL": "#00a1de", "BCI": "#005da4",
    "KEVE": "#7b6348", "ECONO": "#003366", "STB": "#000000"
}

def inicializar_base():
    if not os.path.exists(FILE_NAME):
        # 50 ATMs cobrindo TODOS os municípios de Luanda
        dados = [
            # LUANDA (CENTRO)
            {"id": 0, "banco": "BAI", "zona": "Mutamba Sede", "muni": "Luanda", "lat": -8.8147, "lng": 13.2305},
            {"id": 1, "banco": "BFA", "zona": "Kinaxixi", "muni": "Luanda", "lat": -8.8182, "lng": 13.2381},
            {"id": 2, "banco": "BIC", "zona": "Marginal", "muni": "Luanda", "lat": -8.8085, "lng": 13.2330},
            # TALATONA
            {"id": 3, "banco": "SOL", "zona": "Belas Shopping", "muni": "Talatona", "lat": -8.9288, "lng": 13.1782},
            {"id": 4, "banco": "ATL", "zona": "Talatona Shopping", "muni": "Talatona", "lat": -8.9225, "lng": 13.1810},
            # VIANA
            {"id": 5, "banco": "BFA", "zona": "Ponte Amarela", "muni": "Viana", "lat": -8.9020, "lng": 13.3650},
            {"id": 6, "banco": "BAI", "zona": "Zango 0", "muni": "Viana", "lat": -8.9620, "lng": 13.4020},
            # BELAS / KILAMBA
            {"id": 7, "banco": "BAI", "zona": "Kilamba Bloco B", "muni": "Belas", "lat": -8.9970, "lng": 13.2710},
            {"id": 8, "banco": "BIC", "zona": "Kilamba Bloco K", "muni": "Belas", "lat": -8.9920, "lng": 13.2780},
            # CAZENGA
            {"id": 9, "banco": "BCI", "zona": "Mabor", "muni": "Cazenga", "lat": -8.8450, "lng": 13.2950},
            {"id": 10, "banco": "SOL", "zona": "Marco Histórico", "muni": "Cazenga", "lat": -8.8350, "lng": 13.2850},
            # CACUACO
            {"id": 11, "banco": "ATL", "zona": "Vila de Cacuaco", "muni": "Cacuaco", "lat": -8.7770, "lng": 13.3650},
            {"id": 12, "banco": "BFA", "muni": "Cacuaco", "zona": "Kifangondo", "lat": -8.7550, "lng": 13.3950},
            # SAMBA
            {"id": 13, "banco": "KEVE", "zona": "Corimba", "muni": "Samba", "lat": -8.8750, "lng": 13.1950},
            # QUIÇAMA / ICOLO E BENGO (Pontos Estratégicos)
            {"id": 14, "banco": "BAI", "muni": "Icolo e Bengo", "zona": "Catete Centro", "lat": -9.1000, "lng": 13.4800},
            {"id": 15, "banco": "BFA", "muni": "Quiçama", "zona": "Muxima", "lat": -9.5200, "lng": 13.8500},
        ]
        # Preenchimento para completar 50 pontos...
        for i in range(len(dados), 50):
            dados.append({"id": i, "banco": "BFA", "zona": f"ATM Principal {i}", "muni": "Luanda", "lat": -8.85+(i*0.002), "lng": 13.25+(i*0.002)})
        
        for d in dados: d.update({"s": True, "f": "Vazio", "h": datetime.now().isoformat()})
        with open(FILE_NAME, "w") as f: json.dump(dados, f, indent=4)

@app.on_event("startup")
def startup(): inicializar_base()

@app.get("/", response_class=HTMLResponse)
def home():
    with open(FILE_NAME, "r") as f: atms = json.load(f)
    mapa = folium.Map(location=[-8.8383, 13.2344], zoom_start=11, tiles="cartodbpositron", zoom_control=False)
    LocateControl(fly_to=True).add_to(mapa)

    ui = f"""
    <style>
        #app-header {{ position: fixed; top: 10px; left: 50%; transform: translateX(-50%); width: 92%; max-width: 500px; background: white; z-index: 10000; padding: 10px; border-radius: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.2); font-family: sans-serif; }}
        .search-container {{ display: flex; align-items: center; background: #f1f3f4; border-radius: 20px; padding: 5px 15px; margin-top: 8px; }}
        #search-input {{ border: none; background: transparent; width: 100%; padding: 8px; outline: none; }}
        .badge {{ font-size: 10px; padding: 2px 8px; border-radius: 10px; color: white; font-weight: bold; }}
        .f-vazio {{ background: #27ae60; }} .f-medio {{ background: #f1c40f; color: black; }} .f-cheio {{ background: #e67e22; }}
    </style>

    <div id="app-header">
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 0 10px;">
            <b onclick="location.reload()">🔄</b>
            <span style="font-weight: 800;">🏧 DINHEIRO <span style="color:#27ae60;">AKI</span></span>
            <b onclick="partilhar()">🔗</b>
        </div>
        <div class="search-container">
            <span>🔍</span>
            <input type="text" id="search-input" placeholder="Procurar banco ou zona (ex: BAI ou Viana)" onkeyup="filtrar()">
        </div>
    </div>

    <script>
        var atms_data = {json.dumps(atms)};
        var cores = {json.dumps(BANCOS_CONFIG)};
        var markers = [];

        window.onload = function() {{
            var m = window[document.querySelector('.folium-map').id];
            atms_data.forEach(function(a) {{
                var corS = a.s ? '#27ae60' : '#e74c3c';
                var icon = L.divIcon({{
                    html: `<div style="background:${{cores[a.b]}}; border: 3px solid ${{corS}}; width:32px; height:32px; border-radius:50%; color:white; font-size:9px; display:flex; align-items:center; justify-content:center; font-weight:bold; box-shadow: 0 3px 6px rgba(0,0,0,0.2);">${{a.b}}</div>`,
                    className: '', iconSize: [32, 32]
                }});
                var marker = L.marker([a.lat, a.lng], {{icon: icon}}).addTo(m);
                marker.bindPopup(`
                    <div style="text-align:center; font-family:sans-serif; width:180px;">
                        <b style="font-size:16px;">${{a.b}}</b><br><small>${{a.muni}} - ${{a.zona}}</small><hr>
                        <span style="color:${{corS}}; font-weight:bold;">${{a.s ? '● COM DINHEIRO' : '○ SEM DINHEIRO'}}</span><br>
                        Fila: <span class="badge ${{a.f=='Vazio'?'f-vazio':a.f=='Médio'?'f-medio':'f-cheio'}}">${{a.f}}</span><br><br>
                        <button onclick="window.open('https://www.google.com/maps/dir/?api=1&destination=${{a.lat}},${{a.lng}}')" style="background:#2c3e50; color:white; border:none; padding:10px; border-radius:15px; width:100%; cursor:pointer; font-weight:bold;">🚀 NAVEGAR</button>
                        <button onclick="adm(${{a.id}}, ${{!a.s}})" style="margin-top:8px; border:none; color:gray; background:none; font-size:10px;">⚙️ Admin</button>
                    </div>
                `);
                markers.push({{obj: marker, banco: a.b.toLowerCase(), zona: a.zona.toLowerCase(), muni: a.muni.toLowerCase()}});
            }});
        }};

        function filtrar() {{
            var val = document.getElementById('search-input').value.toLowerCase();
            markers.forEach(function(m) {{
                if (m.banco.includes(val) || m.zona.includes(val) || m.muni.includes(val)) {{
                    m.obj.getElement().style.display = 'block';
                }} else {{
                    m.obj.getElement().style.display = 'none';
                }}
            }});
        }}

        function partilhar() {{
            if (navigator.share) {{
                navigator.share({{ title: 'Dinheiro Aki', text: 'Vê onde há dinheiro nos ATMs em Luanda!', url: window.location.href }});
            }} else {{ alert("Copia o link: " + window.location.href); }}
        }}

        function adm(id, s) {{ var p = prompt("PIN:"); if(p) window.location.href="/up_s?id="+id+"&s="+s+"&pin="+p; }}
    </script>
    """
    mapa.get_root().header.add_child(folium.Element(ui))
    return HTMLResponse(content=mapa._repr_html_())

@app.get("/up_s")
def up_s(id: int, s: str, pin: str):
    if pin != ADMIN_PIN_SERVER: return HTMLResponse("Erro", status_code=403)
    with open(FILE_NAME, "r") as f: d = json.load(f)
    for a in d:
        if a["id"] == id: a["s"] = (s.lower() == "true"); a["h"] = datetime.now().isoformat(); break
    with open(FILE_NAME, "w") as f: json.dump(d, f)
    return RedirectResponse(url="/")
