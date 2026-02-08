from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse
import folium
from folium.plugins import LocateControl, Search, MarkerCluster
import json
import os
from datetime import datetime

app = FastAPI()
FILE_NAME = "dados_v10.json"

def carregar_dados():
    if not os.path.exists(FILE_NAME):
        dados = [
            {"id": 0, "banco": "BAI", "muni": "Luanda", "zona": "Marginal", "lat": -8.8105, "lng": 13.2355, "dinheiro": True},
            {"id": 1, "banco": "BFA", "muni": "Luanda", "zona": "Maianga", "lat": -8.8315, "lng": 13.2325, "dinheiro": True},
            {"id": 2, "banco": "BIC", "muni": "Talatona", "zona": "Shopping", "lat": -8.9185, "lng": 13.1815, "dinheiro": False},
            {"id": 3, "banco": "ATL", "muni": "Viana", "zona": "Viana Park", "lat": -8.9150, "lng": 13.3600, "dinheiro": True},
            {"id": 4, "banco": "STB", "muni": "Kilamba", "zona": "Bloco B", "lat": -8.9955, "lng": 13.2755, "dinheiro": True},
            {"id": 5, "banco": "SOL", "muni": "Luanda", "zona": "Ilha", "lat": -8.7940, "lng": 13.2200, "dinheiro": True},
        ]
        for d in dados: d["hora"] = datetime.now().strftime("%H:%M")
        salvar_dados(dados)
        return dados
    with open(FILE_NAME, "r") as f:
        return json.load(f)

def salvar_dados(dados):
    with open(FILE_NAME, "w") as f:
        json.dump(dados, f, indent=4)

@app.get("/", response_class=HTMLResponse)
def mostrar_mapa():
    atms = carregar_dados()
    
    # Criar mapa ocupando 100% sem bordas
    mapa = folium.Map(
        location=[-8.8383, 13.2344], 
        zoom_start=13, 
        tiles="cartodbpositron", 
        zoom_control=False
    )
    
    LocateControl(auto_start=True, flyTo=True, locateOptions={"enableHighAccuracy": True}).add_to(mapa)

    cluster = MarkerCluster(name="ATMs Luanda").add_to(mapa)

    for atm in atms:
        cor = "green" if atm["dinheiro"] else "red"
        icon_html = f"""<div style="background-color: {cor}; border: 2px solid white; border-radius: 50%; width: 35px; height: 35px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">{atm['banco']}</div>"""
        
        popup_html = f"""
        <div style="font-family: sans-serif; width: 160px; text-align: center;">
            <b style="font-size:14px;">{atm['banco']}</b><br><small>{atm['zona']}</small><hr>
            Status: <b style="color:{cor};">{'COM NOTAS' if atm['dinheiro'] else 'VAZIO'}</b><br>
            <a href="/trocar?id={atm['id']}&status={'false' if atm['dinheiro'] else 'true'}" 
               style="display:inline-block; margin-top:8px; padding:8px 12px; background:{cor}; color:white; text-decoration:none; border-radius:20px; font-size:10px; font-weight:bold;">
               ATUALIZAR AGORA
            </a>
        </div>
        """
        folium.Marker(
            location=[atm["lat"], atm["lng"]],
            popup=folium.Popup(popup_html, max_width=200),
            icon=folium.DivIcon(html=icon_html),
            name=f"{atm['banco']} {atm['zona']} {atm['muni']}"
        ).add_to(cluster)

    Search(layer=cluster, geom_type="Point", placeholder="Onde queres levantar?", collapsed=False, search_label="name").add_to(mapa)

    mapa_html = mapa._repr_html_()
    
    return HTMLResponse(content=f"""
    <!DOCTYPE html>
    <html style="margin:0; padding:0; height:100%; width:100%;">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <style>
            body, html {{ margin: 0; padding: 0; height: 100%; width: 100%; overflow: hidden; }}
            #map-wrapper {{ height: 100vh; width: 100vw; position: absolute; top: 0; left: 0; }}
            .custom-header {{
                position: fixed; top: 15px; left: 50%; transform: translateX(-50%);
                width: 85%; max-width: 380px; background: rgba(255,255,255,0.9);
                backdrop-filter: blur(10px); z-index: 1000; padding: 12px;
                border-radius: 30px; text-align: center; font-family: sans-serif;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1); border: 1px solid rgba(0,0,0,0.05);
                pointer-events: none; font-weight: 900; letter-spacing: 1px;
            }}
            .leaflet-top {{ top: 80px !important; }}
        </style>
    </head>
    <body>
        <div class="custom-header">🏧 DINHEIRO <span style="color:#27ae60;">AKI</span></div>
        <div id="map-wrapper">{mapa_html}</div>
    </body>
    </html>
    """)

@app.get("/trocar")
def trocar_status(id: int, status: str):
    atms = carregar_dados()
    for atm in atms:
        if atm["id"] == id:
            atm["dinheiro"] = (status.lower() == "true")
            atm["hora"] = datetime.now().strftime("%H:%M")
            break
    salvar_dados(atms)
    return RedirectResponse(url="/")