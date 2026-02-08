from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse
import folium
from folium.plugins import LocateControl, Search, MarkerCluster
import json
import os
from datetime import datetime

app = FastAPI()
FILE_NAME = "dados_v12_final.json"
ADMIN_PIN = "2424"

def carregar_dados():
    if not os.path.exists(FILE_NAME):
        dados = [
            {"id": 0, "banco": "BAI", "muni": "Luanda", "zona": "Marginal", "lat": -8.8105, "lng": 13.2355, "dinheiro": True},
            {"id": 1, "banco": "BFA", "muni": "Luanda", "zona": "Maianga", "lat": -8.8315, "lng": 13.2325, "dinheiro": True},
            {"id": 2, "banco": "BIC", "muni": "Talatona", "zona": "Shopping", "lat": -8.9185, "lng": 13.1815, "dinheiro": False},
            {"id": 3, "banco": "ATL", "muni": "Viana", "zona": "Viana Park", "lat": -8.9150, "lng": 13.3600, "dinheiro": True},
            {"id": 4, "banco": "STB", "muni": "Kilamba", "zona": "Bloco B", "lat": -8.9955, "lng": 13.2755, "dinheiro": True},
            {"id": 5, "banco": "BAI", "muni": "Viana", "zona": "Zango 3", "lat": -9.0020, "lng": 13.4550, "dinheiro": True},
            {"id": 6, "banco": "SOL", "muni": "Luanda", "zona": "Ilha", "lat": -8.7940, "lng": 13.2200, "dinheiro": True},
            {"id": 7, "banco": "BCI", "muni": "Sambizanga", "zona": "Mercado", "lat": -8.8050, "lng": 13.2550, "dinheiro": False}
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
    
    # Criar mapa base
    mapa = folium.Map(
        location=[-8.8383, 13.2344], 
        zoom_start=13, 
        tiles="cartodbpositron", 
        zoom_control=False
    )
    
    # Injeção de CSS de ecrã total absoluto
    mapa.get_root().header.add_child(folium.Element("""
        <style>
            #map { position:absolute !important; top:0; bottom:0; right:0; left:0; }
            .leaflet-control-search { margin-top: 85px !important; border: 2px solid #27ae60 !important; }
            .leaflet-control-locate { margin-top: 85px !important; }
            .leaflet-control-layers { margin-top: 85px !important; }
        </style>
    """))

    LocateControl(auto_start=True, flyTo=True, locateOptions={"enableHighAccuracy": True}).add_to(mapa)

    cluster = MarkerCluster(name="📍 Todos os Bancos").add_to(mapa)
    grupo_disponivel = folium.FeatureGroup(name="✅ Apenas com Dinheiro").add_to(mapa)

    for atm in atms:
        cor = "green" if atm["dinheiro"] else "red"
        icon_html = f"""<div style="background-color: {cor}; border: 2px solid white; border-radius: 50%; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 10px; box-shadow: 0 2px 6px rgba(0,0,0,0.3);">{atm['banco']}</div>"""
        
        popup_html = f"""
        <div style="font-family: sans-serif; width: 180px; text-align: center;">
            <b style="font-size:16px;">{atm['banco']}</b><br><small style="color:gray;">{atm['zona']}</small><hr>
            Status: <b style="color:{cor};">{'DISPONÍVEL' if atm['dinheiro'] else 'VAZIO'}</b><br>
            <button onclick="authUpdate({atm['id']}, '{'false' if atm['dinheiro'] else 'true'}')" 
               style="margin-top:10px; padding:10px; width:100%; background:{cor}; color:white; border:none; border-radius:12px; font-weight:bold; cursor:pointer;">
               ATUALIZAR
            </button>
        </div>
        """
        
        marker = folium.Marker(
            location=[atm["lat"], atm["lng"]],
            popup=folium.Popup(popup_html, max_width=250),
            icon=folium.DivIcon(html=icon_html),
            name=f"{atm['banco']} {atm['zona']}"
        )
        marker.add_to(cluster)
        if atm["dinheiro"]:
            marker.add_to(grupo_disponivel)

    folium.LayerControl(position='topright', collapsed=True).add_to(mapa)
    Search(layer=cluster, geom_type="Point", placeholder="Procurar banco...", collapsed=False, search_label="name").add_to(mapa)

    mapa_html = mapa._repr_html_()
    
    return HTMLResponse(content=f"""
    <!DOCTYPE html>
    <html style="margin:0; padding:0; height:100%; width:100%;">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <style>
            body, html {{ margin: 0; padding: 0; height: 100%; width: 100%; overflow: hidden; position: fixed; }}
            #map-wrapper {{ height: 100vh; width: 100vw; position: absolute; top:0; left:0; }}
            .app-header {{
                position: fixed; top: 15px; left: 50%; transform: translateX(-50%);
                width: 85%; max-width: 380px; background: rgba(255,255,255,0.95);
                backdrop-filter: blur(10px); z-index: 9999; padding: 12px;
                border-radius: 50px; text-align: center; font-family: sans-serif;
                box-shadow: 0 4px 15px rgba(0,0,0,0.15); font-weight: 900;
                border-bottom: 3px solid #27ae60; pointer-events: none;
            }}
        </style>
        <script>
            function authUpdate(id, status) {{
                var p = prompt("Código de Segurança:");
                if(p == "{ADMIN_PIN}") {{ window.location.href = "/trocar?id="+id+"&status="+status; }}
                else if(p != null) {{ alert("Código errado!"); }}
            }}
        </script>
    </head>
    <body>
        <div class="app-header">🏧 DINHEIRO <span style="color:#27ae60;">AKI</span></div>
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