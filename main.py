from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse
import folium
from folium.plugins import LocateControl, Search
import json
import os
from datetime import datetime

app = FastAPI()
FILE_NAME = "dados_v5.json"

def carregar_dados():
    if not os.path.exists(FILE_NAME):
        # (Mantemos a mesma base de dados robusta anterior)
        dados = [
            {"id": 0, "banco": "BAI", "muni": "Luanda", "zona": "Marginal", "lat": -8.8105, "lng": 13.2355, "dinheiro": True},
            {"id": 1, "banco": "BFA", "muni": "Luanda", "zona": "Maianga", "lat": -8.8315, "lng": 13.2325, "dinheiro": True},
            {"id": 2, "banco": "BIC", "muni": "Luanda", "zona": "Mutamba", "lat": -8.8135, "lng": 13.2305, "dinheiro": False},
            {"id": 3, "banco": "BCI", "muni": "Luanda", "zona": "Eixo Viário", "lat": -8.8180, "lng": 13.2360, "dinheiro": True},
            {"id": 4, "banco": "ATL", "muni": "Luanda", "zona": "Alvalade", "lat": -8.8390, "lng": 13.2430, "dinheiro": True},
            {"id": 5, "banco": "SOL", "muni": "Luanda", "zona": "Ilha", "lat": -8.7940, "lng": 13.2200, "dinheiro": True},
            {"id": 7, "banco": "BAI", "muni": "Talatona", "zona": "Sede", "lat": -8.9240, "lng": 13.1850, "dinheiro": True},
            {"id": 8, "banco": "BIC", "muni": "Talatona", "zona": "Shopping", "lat": -8.9185, "lng": 13.1815, "dinheiro": True},
            {"id": 10, "banco": "BFA", "muni": "Talatona", "zona": "Kero", "lat": -8.9100, "lng": 13.1950, "dinheiro": True},
            {"id": 12, "banco": "BFA", "muni": "Belas", "zona": "Shopping", "lat": -8.9280, "lng": 13.1780, "dinheiro": True},
            {"id": 13, "banco": "BAI", "muni": "Belas", "zona": "Morro Bento", "lat": -8.8940, "lng": 13.1930, "dinheiro": False},
            {"id": 16, "banco": "BIC", "muni": "Viana", "zona": "Ponte", "lat": -8.9060, "lng": 13.3760, "dinheiro": True},
            {"id": 18, "banco": "BAI", "muni": "Viana", "zona": "Zango 3", "lat": -9.0020, "lng": 13.4550, "dinheiro": True},
            {"id": 21, "banco": "STB", "muni": "Kilamba", "zona": "Bloco B", "lat": -8.9955, "lng": 13.2755, "dinheiro": True},
            {"id": 25, "banco": "KEV", "muni": "Cazenga", "zona": "Cuca", "lat": -8.8355, "lng": 13.2865, "dinheiro": True},
        ]
        for d in dados: d["hora"] = "08:00"
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
    
    # Criar mapa com altura 100%
    mapa = folium.Map(location=[-8.8383, 13.2344], zoom_start=12, tiles="cartodbpositron")
    
    LocateControl(auto_start=False, flyTo=True, keepCurrentZoomLevel=True).add_to(mapa)

    municipios = sorted(list(set(atm["muni"] for atm in atms)))
    camadas = {}
    
    for muni in municipios:
        camadas[muni] = folium.FeatureGroup(name=f"📍 {muni}")

    for atm in atms:
        cor_status = "green" if atm["dinheiro"] else "red"
        icon_html = f"""<div style="background-color: {cor_status}; border: 2px solid white; border-radius: 50%; width: 34px; height: 34px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 9px; box-shadow: 0 2px 4px rgba(0,0,0,0.3);">{atm['banco']}</div>"""
        
        popup_html = f"""<div style='font-family: sans-serif; width: 160px;'><b>{atm['banco']}</b><br><small>{atm['zona']}</small><br><br>Status: <b style='color:{cor_status};'>{'OK' if atm['dinheiro'] else 'VAZIO'}</b><br><hr><a href='/trocar?id={atm['id']}&status={'false' if atm['dinheiro'] else 'true'}' style='display:block; padding:8px; background:{cor_status}; color:white; text-decoration:none; border-radius:4px; text-align:center;'>ATUALIZAR</a></div>"""
        
        folium.Marker(location=[atm["lat"], atm["lng"]], popup=folium.Popup(popup_html), icon=folium.DivIcon(html=icon_html), name=f"{atm['banco']} {atm['zona']}").add_to(camadas[atm["muni"]])

    for m in municipios:
        camadas[m].add_to(mapa)

    folium.LayerControl(position='topright', collapsed=True).add_to(mapa)
    Search(layer=camadas[municipios[0]], geom_type="Point", placeholder="Procurar...", collapsed=True, search_label="name").add_to(mapa)

    mapa_html = mapa._repr_html_()
    
    full_html = f"""
    <!DOCTYPE html>
    <html style="height: 100%; margin: 0; padding: 0;">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <style>
            html, body {{ height: 100%; width: 100%; margin: 0; padding: 0; overflow: hidden; }}
            #map-container {{ height: 100vh; width: 100vw; position: absolute; top: 0; left: 0; z-index: 0; }}
            .header-glass {{
                position: fixed; top: 10px; left: 50%; transform: translateX(-50%);
                width: 90%; max-width: 400px; z-index: 1000;
                background: rgba(26, 37, 47, 0.9); backdrop-filter: blur(5px);
                color: white; padding: 12px; border-radius: 20px;
                text-align: center; font-family: sans-serif; font-weight: bold;
                box-shadow: 0 4px 15px rgba(0,0,0,0.3); pointer-events: none;
            }}
            /* Ajuste dos controlos do Folium para não baterem no header */
            .leaflet-top {{ top: 70px !important; }}
        </style>
    </head>
    <body>
        <div class="header-glass">
            🏧 DINHEIRO <span style="color:#27ae60;">AKI</span>
        </div>

        <div id="map-container">
            {mapa_html}
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=full_html)

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