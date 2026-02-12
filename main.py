from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import folium
from folium.plugins import MarkerCluster, LocateControl
import json
import os
import random
from datetime import datetime

app = FastAPI()
FILE_NAME = "db_luanda_full.json"
ADMIN_PIN = "2424"

# 1. GERADOR DA BASE DE DADOS (Executado apenas na primeira vez)
def inicializar_base_dados():
    if not os.path.exists(FILE_NAME):
        print("A gerar 2100 ATMs para Luanda...")
        municipios = [
            {"nome": "Luanda (Centro)", "lat": -8.8147, "lng": 13.2305, "qtd": 600},
            {"nome": "Talatona", "lat": -8.9288, "lng": 13.1782, "qtd": 400},
            {"nome": "Viana", "lat": -8.9020, "lng": 13.3650, "qtd": 350},
            {"nome": "Belas (Kilamba)", "lat": -8.9970, "lng": 13.2710, "qtd": 300},
            {"nome": "Cazenga", "lat": -8.8450, "lng": 13.2950, "qtd": 200},
            {"nome": "Cacuaco", "lat": -8.7770, "lng": 13.3650, "qtd": 150},
            {"nome": "Samba", "lat": -8.8750, "lng": 13.1950, "qtd": 100}
        ]
        
        bancos = ["BAI", "BFA", "BIC", "SOL", "ATL", "BCI", "KEVE", "ECONO", "STB"]
        todos_atms = []
        contador = 0
        
        for m in municipios:
            for _ in range(m["qtd"]):
                # Gera uma coordenada levemente aleatória ao redor do centro do município
                lat_random = m["lat"] + random.uniform(-0.02, 0.02)
                lng_random = m["lng"] + random.uniform(-0.02, 0.02)
                
                todos_atms.append({
                    "id": contador,
                    "banco": random.choice(bancos),
                    "muni": m["nome"],
                    "zona": f"Ponto {contador}",
                    "lat": round(lat_random, 5),
                    "lng": round(lng_random, 5),
                    "dinheiro": random.choice([True, True, False]), # Simula estado real
                    "hora": datetime.now().isoformat(),
                    "fila": random.choice(["Vazio", "Médio", "Cheio"])
                })
                contador += 1
        
        with open(FILE_NAME, "w") as f:
            json.dump(todos_atms, f, indent=2)

def carregar_dados():
    with open(FILE_NAME, "r") as f:
        return json.load(f)

@app.on_event("startup")
def startup_event():
    inicializar_base_dados()

@app.get("/", response_class=HTMLResponse)
def mostrar_mapa(request: Request):
    atms = carregar_dados()
    mapa = folium.Map(location=[-8.8383, 13.2344], zoom_start=12, tiles="cartodbpositron", zoom_control=False)
    
    # Botão de localização profissional
    LocateControl(auto_start=False, fly_to=True).add_to(mapa)

    ui = f"""
    <link rel="stylesheet" href="https://unpkg.com/leaflet-routing-machine/dist/leaflet-routing-machine.css" />
    <script src="https://unpkg.com/leaflet-routing-machine/dist/leaflet-routing-machine.js"></script>
    <style>
        .leaflet-routing-container {{ display: none !important; }}
        #app-header {{
            position: fixed; top: 15px; left: 50%; transform: translateX(-50%);
            width: 90%; max-width: 450px; background: white; z-index: 10000;
            padding: 12px; border-radius: 35px; display: flex; align-items: center; justify-content: space-between;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15); font-family: sans-serif;
        }}
        .badge {{ font-size: 11px; padding: 2px 8px; border-radius: 10px; color: white; font-weight: bold; }}
        .f-vazio {{ background: #27ae60; }} .f-medio {{ background: #f1c40f; color: black; }} .f-cheio {{ background: #e67e22; }}
    </style>

    <div id="app-header">
        <div onclick="location.reload()">🔄</div>
        <div style="font-weight: 800; font-size:16px;">🏧 DINHEIRO <span style="color:#27ae60;">AKI</span></div>
        <div style="font-size: 12px; color: gray;">{len(atms)} ATMs</div>
    </div>

    <script>
        var uLat, uLng;
        navigator.geolocation.getCurrentPosition(function(p){{ uLat=p.coords.latitude; uLng=p.coords.longitude; }});

        function ir(lat, lng) {{
            var m = window[document.querySelector('.folium-map').id];
            if (window.rC) {{ m.removeControl(window.rC); }}
            window.rC = L.Routing.control({{
                waypoints: [L.latLng(uLat, uLng), L.latLng(lat, lng)],
                lineOptions: {{ styles: [{{color: '#2c3e50', weight: 6}}] }},
                addWaypoints: false, fitSelectedRoutes: true, show: false
            }}).addTo(m);
        }}
    </script>
    """
    mapa.get_root().header.add_child(folium.Element(ui))

    # CLUSTER É OBRIGATÓRIO PARA 2100 PONTOS
    cluster = MarkerCluster(name="Rede Luanda").add_to(mapa)

    for atm in atms:
        cor = "#27ae60" if atm["dinheiro"] else "#e74c3c"
        f_class = f"f-{atm['fila'].lower()}"
        
        # Ícone técnico minimalista para performance
        icon = f'<div style="background:{cor}; width:12px; height:12px; border-radius:50%; border:2px solid white;"></div>'
        
        pop = f"""
        <div style="text-align:center; font-family:sans-serif; width:180px;">
            <b>{atm["banco"]}</b><br><small>{atm["muni"]}</small><hr>
            Fila: <span class="badge {f_class}">{atm["fila"]}</span><br><br>
            <button onclick="ir({atm['lat']}, {atm['lng']})" style="background:#2c3e50; color:white; border:none; border-radius:15px; padding:8px; width:100%; cursor:pointer; font-weight:bold;">MOSTRAR CAMINHO</button>
        </div>
        """
        folium.Marker([atm["lat"], atm["lng"]], popup=folium.Popup(pop), icon=folium.DivIcon(html=icon)).add_to(cluster)

    return HTMLResponse(content=mapa._repr_html_())
