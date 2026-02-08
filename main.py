from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse
import folium
from folium.plugins import LocateControl, Search, MarkerCluster
import json
import os
from datetime import datetime

app = FastAPI()
FILE_NAME = "dados_final_v8.json"

def carregar_dados():
    if not os.path.exists(FILE_NAME):
        # Base de dados expandida com coordenadas reais e precisas
        dados = [
            {"id": 0, "banco": "BAI", "muni": "Luanda", "zona": "Marginal", "lat": -8.8105, "lng": 13.2355, "dinheiro": True},
            {"id": 1, "banco": "BFA", "muni": "Luanda", "zona": "Maianga", "lat": -8.8315, "lng": 13.2325, "dinheiro": True},
            {"id": 2, "banco": "BIC", "muni": "Luanda", "zona": "Mutamba", "lat": -8.8135, "lng": 13.2305, "dinheiro": False},
            {"id": 3, "banco": "ATL", "muni": "Talatona", "zona": "Cidade Financeira", "lat": -8.9240, "lng": 13.1850, "dinheiro": True},
            {"id": 4, "banco": "BIC", "muni": "Talatona", "zona": "Shopping", "lat": -8.9185, "lng": 13.1815, "dinheiro": True},
            {"id": 5, "banco": "BFA", "muni": "Viana", "zona": "Viana Park", "lat": -8.9150, "lng": 13.3600, "dinheiro": True},
            {"id": 6, "banco": "BAI", "muni": "Viana", "zona": "Zango 3", "lat": -9.0020, "lng": 13.4550, "dinheiro": True},
            {"id": 7, "banco": "STB", "muni": "Kilamba", "zona": "Bloco B", "lat": -8.9955, "lng": 13.2755, "dinheiro": True},
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
    # Criar o mapa base
    mapa = folium.Map(
        location=[-8.8383, 13.2344], 
        zoom_start=13, 
        tiles="cartodbpositron", 
        zoom_control=False,
        control_scale=True
    )
    
    # Plugin de localização (GPS)
    LocateControl(
        auto_start=True, # Tenta localizar assim que abre
        flyTo=True,
        locateOptions={"enableHighAccuracy": True}
    ).add_to(mapa)

    cluster = MarkerCluster(name="Bancos").add_to(mapa)

    for atm in atms:
        cor = "green" if atm["dinheiro"] else "red"
        # Design do marcador circular com sigla
        icon_html = f"""<div style="background-color: {cor}; border: 2px solid white; border-radius: 50%; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.3);">{atm['banco']}</div>"""
        
        popup_html = f"""
        <div style="font-family: sans-serif; width: 150px; text-align: center;">
            <b>{atm['banco']}</b><br><small>{atm['zona']}</small><br>
            <hr>
            Status: <b style="color:{cor};">{'DISPONÍVEL' if atm['dinheiro'] else 'SEM NOTAS'}</b><br>
            <a href="/trocar?id={atm['id']}&status={'false' if atm['dinheiro'] else 'true'}" 
               style="display:inline-block; margin-top:10px; padding:8px 15px; background:{cor}; color:white; text-decoration:none; border-radius:15px; font-size:10px;">
               ATUALIZAR
            </a>
        </div>
        """
        folium.Marker(
            location=[atm["lat"], atm["lng"]],
            popup=folium.Popup(popup_html, max_width=200),
            icon=folium.DivIcon(html=icon_html),
            name=f"{atm['banco']} {atm['zona']} {atm['muni']}"
        ).add_to(cluster)

    # Barra de Pesquisa
    Search(layer=cluster, geom_type="Point", placeholder="Procurar banco ou zona...", collapsed=False, search_label="name").add_to(mapa)

    mapa_html = mapa._repr_html_()
    
    # HTML FINAL - CORREÇÃO DE ECRÃ TOTAL
    full_html = f"""
    <!DOCTYPE html>
    <html style="height: 100%; margin: 0;">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <style>
            body {{ height: 100%; margin: 0; padding: 0; }}
            .folium-map {{ height: 100vh !important; width: 100vw !important; }}
            .app-bar {{
                position: fixed; top: 10px; left: 50%; transform: translateX(-50%);
                width: 90%; max-width: 400px; background: white; z-index: 1000;
                padding: 12px; border-radius: 25px; box-shadow: 0 2px 10px rgba(0,0,0,0.2);
                text-align: center; font-family: sans-serif; font-weight: bold;
                pointer-events: none; border: 1px solid #eee;
            }}
            /* Reposicionar botões do mapa */
            .leaflet-top.leaflet-left {{ top: 70px !important; }}
        </style>
    </head>
    <body>
        <div class="app-bar">🏧 DINHEIRO AKI <span style="color:#27ae60;">LUANDA</span></div>
        <div style="height: 100vh; width: 100vw;">{mapa_html}</div>
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