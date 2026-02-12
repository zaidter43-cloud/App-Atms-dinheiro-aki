from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import folium
from folium.plugins import LocateControl
import json
import os
from datetime import datetime

app = FastAPI()
FILE_NAME = "db_luanda_v49.json"
ADMIN_PIN_SERVER = "2424"

BANCOS_CONFIG = {
    "BAI": "#004a99", "BFA": "#ff6600", "BIC": "#e30613", 
    "SOL": "#f9b233", "ATL": "#00a1de", "BCI": "#005da4",
    "KEVE": "#7b6348", "ECONO": "#003366", "STB": "#000000"
}

def inicializar_base():
    if not os.path.exists(FILE_NAME):
        dados = [
            {"id": 0, "banco": "BAI", "zona": "Mutamba Sede", "muni": "Luanda", "lat": -8.8147, "lng": 13.2305},
            {"id": 1, "banco": "BFA", "zona": "Kinaxixi", "muni": "Luanda", "lat": -8.8182, "lng": 13.2381},
            {"id": 2, "banco": "BIC", "zona": "Kero Talatona", "muni": "Talatona", "lat": -8.9180, "lng": 13.1900},
            {"id": 3, "banco": "SOL", "zona": "Belas Shopping", "muni": "Talatona", "lat": -8.9288, "lng": 13.1782},
            {"id": 4, "banco": "ATL", "zona": "Ponte Amarela", "muni": "Viana", "lat": -8.9020, "lng": 13.3650},
            {"id": 5, "banco": "BAI", "zona": "Zango 0", "muni": "Viana", "lat": -8.9620, "lng": 13.4020},
            {"id": 6, "banco": "BFA", "zona": "Kilamba Bloco B", "muni": "Belas", "lat": -8.9970, "lng": 13.2710},
            {"id": 7, "banco": "BCI", "zona": "Mabor", "muni": "Cazenga", "lat": -8.8450, "lng": 13.2950},
            {"id": 8, "banco": "ATL", "zona": "Vila de Cacuaco", "muni": "Cacuaco", "lat": -8.7770, "lng": 13.3650},
            {"id": 9, "banco": "KEVE", "zona": "Corimba", "muni": "Samba", "lat": -8.8750, "lng": 13.1950}
        ]
        # Adicionar mais pontos para completar 50
        for i in range(len(dados), 50):
            dados.append({"id": i, "banco": "BFA", "zona": f"ATM Principal {i}", "muni": "Luanda", "lat": -8.85+(i*0.001), "lng": 13.25+(i*0.001)})
        
        for d in dados: d.update({"s": True, "f": "Vazio", "h": datetime.now().isoformat()})
        with open(FILE_NAME, "w") as f: json.dump(dados, f, indent=4)

@app.on_event("startup")
def startup(): inicializar_base()

@app.get("/", response_class=HTMLResponse)
def home():
    with open(FILE_NAME, "r") as f: atms = json.load(f)
    
    # Criamos o mapa com um nome de objeto fixo para o JS encontrar
    mapa = folium.Map(location=[-8.8383, 13.2344], zoom_start=12, tiles="cartodbpositron", zoom_control=False)
    LocateControl(fly_to=True).add_to(mapa)

    ui = f"""
    <style>
        #app-header {{ position: fixed; top: 12px; left: 50%; transform: translateX(-50%); width: 92%; max-width: 480px; background: white; z-index: 10000; padding: 12px; border-radius: 35px; box-shadow: 0 4px 20px rgba(0,0,0,0.15); font-family: sans-serif; }}
        .search-bar {{ display: flex; align-items: center; background: #f4f4f7; border-radius: 20px; padding: 6px 15px; margin-top: 10px; }}
        #q {{ border: none; background: transparent; width: 100%; padding: 5px; outline: none; }}
        .badge {{ font-size: 10px; padding: 3px 10px; border-radius: 12px; color: white; font-weight: bold; }}
        .f-vazio {{ background: #27ae60; }} .f-medio {{ background: #f1c40f; color: #2c3e50; }} .f-cheio {{ background: #e67e22; }}
        .btn-nav {{ background: #2c3e50; color: white; border: none; padding: 12px; border-radius: 20px; width: 100%; font-weight: bold; margin-top: 10px; cursor: pointer; }}
    </style>

    <div id="app-header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span onclick="location.reload()">🔄</span>
            <span style="font-weight: 800;">🏧 DINHEIRO <span style="color:#27ae60;">AKI</span></span>
            <span onclick="partilhar()">📤</span>
        </div>
        <div class="search-bar">
            <span>🔍</span>
            <input type="text" id="q" placeholder="Procurar banco ou município..." onkeyup="filtrar()">
        </div>
    </div>

    <script>
        var data = {json.dumps(atms)};
        var cores = {json.dumps(BANCOS_CONFIG)};
        var markers = [];

        function initMapMarkers() {{
            // Correção do Bug: Encontrar o mapa independente do ID dinâmico
            var mapElement = document.querySelector('.folium-map');
            if (!mapElement) return setTimeout(initMapMarkers, 100);
            
            var m = window[mapElement.id];
            
            data.forEach(function(a) {{
                var corS = a.s ? '#27ae60' : '#e74c3c';
                var icon = L.divIcon({{
                    html: `<div style="background:${{cores[a.b]}}; border: 3px solid ${{corS}}; width:32px; height:32px; border-radius:50%; color:white; font-size:9px; display:flex; align-items:center; justify-content:center; font-weight:bold; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">${{a.b}}</div>`,
                    className: '', iconSize: [32, 32]
                }});

                var marker = L.marker([a.lat, a.lng], {{icon: icon}}).addTo(m);
                marker.bindPopup(`
                    <div style="text-align:center; font-family:sans-serif; width:200px;">
                        <b style="font-size:18px;">${{a.b}}</b><br><small>${{a.muni}} - ${{a.zona}}</small><hr>
                        <div style="margin-bottom:8px;">Status: <b style="color:${{corS}}">${{a.s ? 'COM DINHEIRO' : 'SEM DINHEIRO'}}</b></div>
                        <div>Fila: <span class="badge ${{a.f=='Vazio'?'f-vazio':a.f=='Médio'?'f-medio':'f-cheio'}}">${{a.f}}</span></div>
                        <button onclick="window.open('https://www.google.com/maps/dir/?api=1&destination=${{a.lat}},${{a.lng}}')" class="btn-nav">🚀 NAVEGAR</button>
                        <div style="margin-top:10px;"><small onclick="adm(${{a.id}}, ${{!a.s}})" style="color:#ccc; cursor:pointer;">⚙️ Admin</small></div>
                    </div>
                `);
                markers.push({{el: marker, tag: (a.b + a.muni + a.zona).toLowerCase()}});
            }});
        }}

        window.onload = initMapMarkers;

        function filtrar() {{
            var val = document.getElementById('q').value.toLowerCase();
            markers.forEach(function(m) {{
                if (m.tag.includes(val)) m.el.getElement().style.opacity = "1";
                else m.el.getElement().style.opacity = "0.1";
            }});
        }}

        function partilhar() {{
            if (navigator.share) navigator.share({{ title: 'Dinheiro Aki', url: window.location.href }});
            else alert("Copia: " + window.location.href);
        }}

        function adm(id, s) {{
            var p = prompt("PIN:");
            if(p) window.location.href = "/up_s?id="+id+"&s="+s+"&pin="+p;
        }}
    </script>
    """
    mapa.get_root().header.add_child(folium.Element(ui))
    return HTMLResponse(content=mapa._repr_html_())

@app.get("/up_s")
def up_s(id: int, s: str, pin: str):
    if pin != ADMIN_PIN_SERVER: return HTMLResponse("Erro", status_code=403)
    with open(FILE_NAME, "r") as f: d = json.load(f)
    for a in d:
        if a["id"] == id: a["s"] = (s.lower() == "true"); break
    with open(FILE_NAME, "w") as f: json.dump(d, f)
    return RedirectResponse(url="/")
