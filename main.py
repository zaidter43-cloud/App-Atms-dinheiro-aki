from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse
import folium
from folium.plugins import LocateControl, Search, MarkerCluster
import json
import os
from datetime import datetime

app = FastAPI()
FILE_NAME = "dados_v6.json"

def carregar_dados():
    if not os.path.exists(FILE_NAME):
        # Base de dados expandida e organizada
        dados = [
            # LUANDA CENTRO
            {"id": 0, "banco": "BNA", "muni": "Luanda", "zona": "Marginal", "lat": -8.8106, "lng": 13.2341, "dinheiro": True},
            {"id": 1, "banco": "BAI", "muni": "Luanda", "zona": "Sede", "lat": -8.8105, "lng": 13.2355, "dinheiro": True},
            {"id": 2, "banco": "BFA", "muni": "Luanda", "zona": "Maianga", "lat": -8.8315, "lng": 13.2325, "dinheiro": True},
            {"id": 3, "banco": "BE", "muni": "Luanda", "zona": "Kinaxixi", "lat": -8.8191, "lng": 13.2505, "dinheiro": False},
            
            # NOVA VIDA / TALATONA
            {"id": 4, "banco": "BIC", "muni": "Talatona", "zona": "Atrium Nova Vida", "lat": -8.8966, "lng": 13.2297, "dinheiro": True},
            {"id": 5, "banco": "ATL", "muni": "Talatona", "zona": "Xyami Shopping", "lat": -8.8976, "lng": 13.2255, "dinheiro": True},
            {"id": 6, "banco": "BFA", "muni": "Talatona", "zona": "O Nosso Centro", "lat": -8.8862, "lng": 13.2071, "dinheiro": True},
            {"id": 7, "banco": "SOL", "muni": "Talatona", "zona": "Belas Shopping", "lat": -8.9280, "lng": 13.1780, "dinheiro": True},
            
            # VIANA / ZANGO
            {"id": 8, "banco": "BAI", "muni": "Viana", "zona": "Zango 3", "lat": -9.0020, "lng": 13.4550, "dinheiro": True},
            {"id": 9, "banco": "BIC", "muni": "Viana", "zona": "Ponte", "lat": -8.9060, "lng": 13.3760, "dinheiro": False}
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
    
    # Criar mapa com estilo limpo do Google Maps (CartoDB)
    mapa = folium.Map(location=[-8.8383, 13.2344], zoom_start=13, tiles="cartodbpositron", zoom_control=False)
    
    # GPS DE ALTA PRECISÃO
    LocateControl(
        auto_start=False,
        flyTo=True,
        keepCurrentZoomLevel=False,
        locateOptions={"enableHighAccuracy": True}
    ).add_to(mapa)

    # ORGANIZAÇÃO POR CLUSTERS (Agrupa quando longe)
    marker_cluster = MarkerCluster(name="Todos os Bancos").add_to(mapa)

    for atm in atms:
        cor_status = "green" if atm["dinheiro"] else "red"
        icon_html = f"""<div style="background-color: {cor_status}; border: 2px solid white; border-radius: 50%; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">{atm['banco']}</div>"""
        
        popup_html = f"""<div style='font-family: sans-serif; width: 150px;'><b>{atm['banco']}</b><br><small>{atm['zona']}</small><br><br><b>{'DISPONÍVEL' if atm['dinheiro'] else 'SEM NOTAS'}</b><br><hr><a href='/trocar?id={atm['id']}&status={'false' if atm['dinheiro'] else 'true'}' style='display:block; padding:8px; background:{cor_status}; color:white; text-decoration:none; border-radius:4px; text-align:center;'>ATUALIZAR</a></div>"""
        
        folium.Marker(
            location=[atm["lat"], atm["lng"]],
            popup=folium.Popup(popup_html),
            icon=folium.DivIcon(html=icon_html),
            name=f"{atm['banco']} {atm['zona']} {atm['muni']}"
        ).add_to(marker_cluster)

    # PESQUISA GLOBAL CORRIGIDA
    Search(
        layer=marker_cluster,
        geom_type="Point",
        placeholder="Pesquisar zona ou banco...",
        collapsed=False,
        search_label="name"
    ).add_to(mapa)

    mapa_html = mapa._repr_html_()
    
    full_html = f"""
    <!DOCTYPE html>
    <html style="height: 100%;">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <style>
            body, html {{ height: 100%; width: 100%; margin: 0; padding: 0; overflow: hidden; font-family: sans-serif; }}
            #map-container {{ height: 100vh; width: 100vw; position: absolute; top: 0; left: 0; }}
            .floating-header {{
                position: fixed; top: 12px; left: 50%; transform: translateX(-50%);
                width: 85%; z-index: 1000; background: rgba(255,255,255,0.95);
                padding: 10px; border-radius: 12px; text-align: center;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15); font-weight: bold; color: #1a252f;
                pointer-events: none; border-bottom: 3px solid #27ae60;
            }}
            .leaflet-top {{ top: 75px !important; }}
            .leaflet-control-search {{ width: 280px !important; border-radius: 20px !important; }}
        </style>
    </head>
    <body>
        <div class="floating-header">🏧 DINHEIRO AKI <span style="color:#27ae60;">LUANDA</span></div>
        <div id="map-container">{mapa_html}</div>
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