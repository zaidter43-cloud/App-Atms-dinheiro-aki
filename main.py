from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse
import folium
from folium.plugins import LocateControl, Search
import json
import os
from datetime import datetime

app = FastAPI()
# Mudamos para v3 para forçar a atualização da lista real
FILE_NAME = "dados_v3.json"

def carregar_dados():
    if not os.path.exists(FILE_NAME):
        # LOCALIZAÇÕES REAIS EM LUANDA (Coordenadas aproximadas dos centros comerciais e sedes)
        dados_reais = [
            {"id": 0, "banco": "BAI", "local": "Sede (Marginal)", "lat": -8.8105, "lng": 13.2355, "dinheiro": True, "hora": "08:00"},
            {"id": 1, "banco": "BFA", "local": "Sede (Maianga)", "lat": -8.8315, "lng": 13.2325, "dinheiro": True, "hora": "08:00"},
            {"id": 2, "banco": "BIC", "local": "Talatona (Shopping)", "lat": -8.9185, "lng": 13.1815, "dinheiro": False, "hora": "09:30"},
            {"id": 3, "banco": "STB", "local": "Standard Bank (Kilamba)", "lat": -8.9955, "lng": 13.2755, "dinheiro": True, "hora": "10:00"},
            {"id": 4, "banco": "ATL", "local": "Atlantico (Cidade Financeira)", "lat": -8.9240, "lng": 13.1850, "dinheiro": True, "hora": "07:45"},
            {"id": 5, "banco": "BAI", "local": "Aeroporto 4 de Fevereiro", "lat": -8.8510, "lng": 13.2320, "dinheiro": False, "hora": "11:00"},
            {"id": 6, "banco": "BFA", "local": "Belas Shopping", "lat": -8.9280, "lng": 13.1780, "dinheiro": True, "hora": "12:15"},
            {"id": 7, "banco": "BIC", "local": "Viana (Ponte)", "lat": -8.9060, "lng": 13.3760, "dinheiro": False, "hora": "14:00"},
            {"id": 8, "banco": "SOL", "local": "Mutamba", "lat": -8.8135, "lng": 13.2305, "dinheiro": True, "hora": "08:30"},
            {"id": 9, "banco": "KEV", "local": "Cazenga (Cuca)", "lat": -8.8355, "lng": 13.2865, "dinheiro": True, "hora": "09:00"},
            {"id": 10, "banco": "BFA", "local": "Zango 3 (Multicenter)", "lat": -9.0020, "lng": 13.4550, "dinheiro": False, "hora": "13:45"},
            {"id": 11, "banco": "BAI", "local": "Morro Bento (Kero)", "lat": -8.8940, "lng": 13.1930, "dinheiro": True, "hora": "10:20"},
            {"id": 12, "banco": "BIC", "local": "Alvalade", "lat": -8.8390, "lng": 13.2430, "dinheiro": True, "hora": "15:00"},
            {"id": 13, "banco": "BCI", "local": "Ilha de Luanda", "lat": -8.7940, "lng": 13.2200, "dinheiro": True, "hora": "09:15"},
            {"id": 14, "banco": "BFA", "local": "Nova Vida (Kero)", "lat": -8.8910, "lng": 13.2410, "dinheiro": False, "hora": "11:30"}
        ]
        salvar_dados(dados_reais)
        return dados_reais
    with open(FILE_NAME, "r") as f:
        return json.load(f)

def salvar_dados(dados):
    with open(FILE_NAME, "w") as f:
        json.dump(dados, f, indent=4)

@app.get("/", response_class=HTMLResponse)
def mostrar_mapa():
    atms = carregar_dados()
    mapa = folium.Map(location=[-8.8383, 13.2344], zoom_start=12)
    LocateControl().add_to(mapa)

    # Cores personalizadas por banco
    cores_bancos = {
        "BAI": "blue", "BFA": "orange", "BIC": "red", 
        "STB": "darkblue", "ATL": "darkred", "SOL": "orange", 
        "KEV": "green", "BCI": "darkgreen"
    }

    grupo_atms = folium.FeatureGroup(name="ATMs Luanda")

    for atm in atms:
        cor_banco = cores_bancos.get(atm["banco"], "gray")
        cor_status = "green" if atm["dinheiro"] else "red"
        
        # Criamos o ícone com a abreviação do banco usando DivIcon (HTML puro no marcador)
        icon_html = f"""
            <div style="
                background-color: {cor_status};
                border: 2px solid white;
                border-radius: 50%;
                width: 35px; height: 35px;
                display: flex; align-items: center; justify-content: center;
                color: white; font-weight: bold; font-size: 10px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.5);
                text-align: center; font-family: sans-serif;
            ">
                {atm['banco']}
            </div>
        """
        
        popup_html = f"""
            <div style='font-family: sans-serif; width: 180px;'>
                <h4 style='margin:0; color:{cor_banco};'>{atm['banco']}</h4>
                <p style='font-size:12px; color:gray;'>{atm['local']}</p>
                <p>Status: <b style='color:{cor_status};'>{'COM DINHEIRO' if atm['dinheiro'] else 'SEM DINHEIRO'}</b></p>
                <p style='font-size:10px;'>Atualizado: {atm['hora']}</p>
                <hr>
                <a href='/trocar?id={atm['id']}&status={'false' if atm['dinheiro'] else 'true'}' 
                   style='display:block; padding:10px; background:{cor_status}; color:white; text-decoration:none; border-radius:5px; text-align:center; font-weight:bold;'>
                   ATUALIZAR STATUS
                </a>
            </div>
        """
        
        folium.Marker(
            location=[atm["lat"], atm["lng"]],
            popup=folium.Popup(popup_html, max_width=250),
            icon=folium.DivIcon(html=icon_html),
            name=f"{atm['banco']} - {atm['local']}"
        ).add_to(grupo_atms)

    grupo_atms.add_to(mapa)

    Search(
        layer=grupo_atms,
        geom_type="Point",
        placeholder="Pesquisar Banco ou Local...",
        collapsed=False,
        search_label="name"
    ).add_to(mapa)

    mapa_html = mapa._repr_html_()
    
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ margin: 0; padding: 0; overflow: hidden; }}
            #loader {{ position: fixed; width: 100%; height: 100%; top: 0; left: 0; background: white; z-index: 10000; display: flex; flex-direction: column; align-items: center; justify-content: center; transition: opacity 0.5s ease; }}
            .spinner {{ border: 8px solid #f3f3f3; border-top: 8px solid #27ae60; border-radius: 50%; width: 50px; height: 50px; animation: spin 1s linear infinite; }}
            @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
            .header {{ position: fixed; top: 0; left: 0; width: 100%; z-index: 1000; background: #2c3e50; color: white; padding: 15px 0; text-align: center; font-family: sans-serif; font-weight: bold; box-shadow: 0 2px 10px rgba(0,0,0,0.3); }}
            #map-container {{ margin-top: 52px; height: calc(100vh - 52px); }}
            .leaflet-control-search {{ margin-top: 65px !important; }}
        </style>
    </head>
    <body>
        <div id="loader"><div class="spinner"></div><p style="font-family:sans-serif; margin-top:15px;">Mapeando Luanda...</p></div>
        <div class="header">🏧 DINHEIRO <span style="color:#27ae60;">AKI</span></div>
        <div id="map-container">{mapa_html}</div>
        <script>
            window.onload = function() {{
                setTimeout(function() {{
                    var loader = document.getElementById('loader');
                    loader.style.opacity = '0';
                    setTimeout(function() {{ loader.style.display = 'none'; }}, 500);
                }}, 1000);
            }};
        </script>
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