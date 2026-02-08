from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse
import folium
from folium.plugins import LocateControl, Search, MarkerCluster
import json
import os
from datetime import datetime

app = FastAPI()
# Mudamos para v5 para a nova base de dados massiva
FILE_NAME = "dados_v5.json"

def carregar_dados():
    if not os.path.exists(FILE_NAME):
        # BASE DE DADOS EXPANDIDA POR MUNICÍPIOS E ZONAS
        dados = [
            # LUANDA (CENTRO/MAIANGA/INGOMBOTA)
            {"id": 0, "banco": "BAI", "muni": "Luanda", "zona": "Marginal", "lat": -8.8105, "lng": 13.2355, "dinheiro": True},
            {"id": 1, "banco": "BFA", "muni": "Luanda", "zona": "Maianga", "lat": -8.8315, "lng": 13.2325, "dinheiro": True},
            {"id": 2, "banco": "BIC", "muni": "Luanda", "zona": "Mutamba", "lat": -8.8135, "lng": 13.2305, "dinheiro": False},
            {"id": 3, "banco": "BCI", "muni": "Luanda", "zona": "Eixo Viário", "lat": -8.8180, "lng": 13.2360, "dinheiro": True},
            {"id": 4, "banco": "ATL", "muni": "Luanda", "zona": "Alvalade", "lat": -8.8390, "lng": 13.2430, "dinheiro": True},
            {"id": 5, "banco": "SOL", "muni": "Luanda", "zona": "Ilha", "lat": -8.7940, "lng": 13.2200, "dinheiro": True},
            {"id": 6, "banco": "BIR", "muni": "Luanda", "zona": "Kinaxixi", "lat": -8.8155, "lng": 13.2345, "dinheiro": False},

            # TALATONA
            {"id": 7, "banco": "BAI", "muni": "Talatona", "zona": "Sede", "lat": -8.9240, "lng": 13.1850, "dinheiro": True},
            {"id": 8, "banco": "BIC", "muni": "Talatona", "zona": "Shopping", "lat": -8.9185, "lng": 13.1815, "dinheiro": True},
            {"id": 9, "banco": "STB", "muni": "Talatona", "zona": "Via S8", "lat": -8.9350, "lng": 13.1900, "dinheiro": False},
            {"id": 10, "banco": "BFA", "muni": "Talatona", "zona": "Kero", "lat": -8.9100, "lng": 13.1950, "dinheiro": True},
            {"id": 11, "banco": "VTB", "muni": "Talatona", "zona": "Cidade Financeira", "lat": -8.9250, "lng": 13.1860, "dinheiro": True},

            # BELAS / BENFICA
            {"id": 12, "banco": "BFA", "muni": "Belas", "zona": "Shopping", "lat": -8.9280, "lng": 13.1780, "dinheiro": True},
            {"id": 13, "banco": "BAI", "muni": "Belas", "zona": "Morro Bento", "lat": -8.8940, "lng": 13.1930, "dinheiro": False},
            {"id": 14, "banco": "BIC", "muni": "Belas", "zona": "Benfica", "lat": -8.9450, "lng": 13.1900, "dinheiro": True},
            {"id": 15, "banco": "BE", "muni": "Belas", "zona": "Futungo", "lat": -8.9050, "lng": 13.1750, "dinheiro": True},

            # VIANA
            {"id": 16, "banco": "BIC", "muni": "Viana", "zona": "Ponte", "lat": -8.9060, "lng": 13.3760, "dinheiro": True},
            {"id": 17, "banco": "BFA", "muni": "Viana", "zona": "Viana Park", "lat": -8.9150, "lng": 13.3600, "dinheiro": False},
            {"id": 18, "banco": "BAI", "muni": "Viana", "zona": "Zango 3", "lat": -9.0020, "lng": 13.4550, "dinheiro": True},
            {"id": 19, "banco": "SOL", "muni": "Viana", "zona": "Zango 0", "lat": -8.9650, "lng": 13.4850, "dinheiro": True},
            {"id": 20, "banco": "ATL", "muni": "Viana", "zona": "Viana Vila", "lat": -8.8950, "lng": 13.3700, "dinheiro": False},

            # KILAMBA / CAMAMA
            {"id": 21, "banco": "STB", "muni": "Kilamba", "zona": "Bloco B", "lat": -8.9955, "lng": 13.2755, "dinheiro": True},
            {"id": 22, "banco": "BAI", "muni": "Kilamba", "zona": "Edifício Novo", "lat": -9.0050, "lng": 13.2800, "dinheiro": False},
            {"id": 23, "banco": "BFA", "muni": "Camama", "zona": "Jardim do Éden", "lat": -8.9350, "lng": 13.2650, "dinheiro": True},
            {"id": 24, "banco": "SOL", "muni": "Camama", "zona": "Calemba 2", "lat": -8.9200, "lng": 13.2900, "dinheiro": True},

            # CAZENGA / SAMBIZANGA
            {"id": 25, "banco": "KEV", "muni": "Cazenga", "zona": "Cuca", "lat": -8.8355, "lng": 13.2865, "dinheiro": True},
            {"id": 26, "banco": "BCI", "muni": "Cazenga", "zona": "Marco Histórico", "lat": -8.8250, "lng": 13.2750, "dinheiro": False},
            {"id": 27, "banco": "BFA", "muni": "Cazenga", "zona": "Hoji Ya Henda", "lat": -8.8200, "lng": 13.3000, "dinheiro": True},
            {"id": 28, "banco": "BAI", "muni": "Sambizanga", "zona": "Mercado", "lat": -8.8050, "lng": 13.2550, "dinheiro": True},
        ]
        # Adicionar hora inicial
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
    mapa = folium.Map(location=[-8.8383, 13.2344], zoom_start=12)
    
    # 1. BOTÃO LOCALIZAÇÃO (Onde eu estou)
    LocateControl(auto_start=False, flyTo=True, keepCurrentZoomLevel=True, 
                  strings={"title": "Mostrar onde estou"}).add_to(mapa)

    # 2. SEPARAÇÃO POR CAMADAS (MUNICÍPIOS)
    municipios = sorted(list(set(atm["muni"] for atm in atms)))
    camadas = {}
    
    for muni in municipios:
        # Usamos MarkerCluster para não poluir o mapa
        camadas[muni] = folium.FeatureGroup(name=f"🏢 {muni}")

    for atm in atms:
        cor_status = "green" if atm["dinheiro"] else "red"
        label_pesquisa = f"{atm['banco']} - {atm['zona']} ({atm['muni']})"
        
        # Ícone visual com sigla
        icon_html = f"""
            <div style="background-color: {cor_status}; border: 2px solid white; border-radius: 50%;
                width: 36px; height: 36px; display: flex; align-items: center; justify-content: center;
                color: white; font-weight: bold; font-size: 9px; box-shadow: 0 2px 6px rgba(0,0,0,0.4);">
                {atm['banco']}
            </div>
        """
        
        popup_html = f"""
            <div style='font-family: sans-serif; width: 190px;'>
                <b style='color:#2c3e50; font-size:14px;'>{atm['banco']}</b><br>
                <span style='color:gray; font-size:11px;'>{atm['muni']} - {atm['zona']}</span><br><br>
                Status: <b style='color:{cor_status};'>{'DISPONÍVEL' if atm['dinheiro'] else 'INDISPONÍVEL'}</b><br>
                <small>Última atualização: {atm['hora']}</small><br><hr>
                <a href='/trocar?id={atm['id']}&status={'false' if atm['dinheiro'] else 'true'}' 
                   style='display:block; padding:10px; background:{cor_status}; color:white; text-decoration:none; border-radius:6px; text-align:center; font-weight:bold;'>
                   MUDAR STATUS
                </a>
            </div>
        """
        
        folium.Marker(
            location=[atm["lat"], atm["lng"]],
            popup=folium.Popup(popup_html, max_width=250),
            icon=folium.DivIcon(html=icon_html),
            name=label_pesquisa
        ).add_to(camadas[atm["muni"]])

    # Adicionar camadas ao mapa
    for m in municipios:
        camadas[m].add_to(mapa)

    # 3. CONTROLO DE CAMADAS (Para escolher o que ver)
    folium.LayerControl(position='topright', collapsed=False).add_to(mapa)

    # 4. PESQUISA GLOBAL (Por nome de banco ou zona)
    # Procuramos na primeira camada como referência para o Search
    Search(layer=camadas[municipios[0]], geom_type="Point", placeholder="Procurar (ex: BAI Viana)",
           collapsed=False, search_label="name").add_to(mapa)

    mapa_html = mapa._repr_html_()
    
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ margin: 0; padding: 0; }}
            .header {{ position: fixed; top: 0; left: 0; width: 100%; z-index: 1001; background: #1a252f; color: white; padding: 12px 0; text-align: center; font-family: sans-serif; box-shadow: 0 2px 8px rgba(0,0,0,0.5); }}
            #map-container {{ margin-top: 45px; height: calc(100vh - 45px); }}
            .leaflet-control-layers {{ margin-top: 60px !important; border: 2px solid #27ae60 !important; font-family: sans-serif; }}
            .leaflet-control-search {{ margin-top: 60px !important; }}
        </style>
    </head>
    <body>
        <div class="header">🏧 DINHEIRO AKI <span style="color:#27ae60;">LUANDA</span></div>
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