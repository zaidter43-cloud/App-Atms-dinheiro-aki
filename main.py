from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse
import folium
from folium.plugins import LocateControl, Search
import json
import os
from datetime import datetime

# 1. CONFIGURAÇÃO INICIAL
app = FastAPI()
FILE_NAME = "dados_v2.json"

def carregar_dados():
    if not os.path.exists(FILE_NAME):
        dados_iniciais = [
            {"id": 0, "banco": "BAI", "local": "Sede - Luanda", "lat": -8.8147, "lng": 13.2302, "dinheiro": True, "hora": "09:00"},
            {"id": 1, "banco": "BFA", "local": "Talatona Shopping", "lat": -8.9180, "lng": 13.1810, "dinheiro": False, "hora": "10:30"},
            {"id": 2, "banco": "BIC", "local": "Aeroporto", "lat": -8.8500, "lng": 13.2333, "dinheiro": True, "hora": "11:00"},
            {"id": 3, "banco": "Standard Bank", "local": "Kilamba", "lat": -8.9950, "lng": 13.2750, "dinheiro": True, "hora": "08:45"},
            {"id": 4, "banco": "ATLANTICO", "local": "Viana (Ponte)", "lat": -8.9050, "lng": 13.3750, "dinheiro": False, "hora": "14:20"},
            {"id": 5, "banco": "BAI", "local": "Mutamba", "lat": -8.8140, "lng": 13.2310, "dinheiro": True, "hora": "08:00"},
            {"id": 6, "banco": "BFA", "local": "Maianga", "lat": -8.8310, "lng": 13.2320, "dinheiro": True, "hora": "12:15"},
            {"id": 7, "banco": "BIC", "local": "Ilha de Luanda", "lat": -8.7950, "lng": 13.2210, "dinheiro": False, "hora": "09:30"},
            {"id": 8, "banco": "ATLANTICO", "local": "Zango 0", "lat": -8.9650, "lng": 13.4850, "dinheiro": True, "hora": "10:00"},
            {"id": 9, "banco": "BAI", "local": "Cazenga (Cuca)", "lat": -8.8350, "lng": 13.2850, "dinheiro": True, "hora": "11:45"},
            {"id": 10, "banco": "BFA", "local": "Benfica", "lat": -8.9450, "lng": 13.1950, "dinheiro": False, "hora": "13:20"},
            {"id": 11, "banco": "Standard Bank", "local": "Morro Bento", "lat": -8.8950, "lng": 13.1950, "dinheiro": True, "hora": "07:30"},
            {"id": 12, "banco": "BIC", "local": "Alvalade", "lat": -8.8380, "lng": 13.2420, "dinheiro": True, "hora": "15:10"},
            {"id": 13, "banco": "BAI", "local": "Camama", "lat": -8.9350, "lng": 13.2650, "dinheiro": False, "hora": "09:00"},
            {"id": 14, "banco": "BFA", "local": "Golfe 2", "lat": -8.8950, "lng": 13.2750, "dinheiro": True, "hora": "10:15"}
        ]
        salvar_dados(dados_iniciais)
        return dados_iniciais
    with open(FILE_NAME, "r") as f:
        return json.load(f)

def salvar_dados(dados):
    with open(FILE_NAME, "w") as f:
        json.dump(dados, f, indent=4)

# 2. ROTA PRINCIPAL
@app.get("/", response_class=HTMLResponse)
def mostrar_mapa():
    atms = carregar_dados()
    
    # Criar o mapa
    mapa = folium.Map(location=[-8.8383, 13.2344], zoom_start=12)
    LocateControl().add_to(mapa)

    cores_bancos = {"BAI": "blue", "BFA": "orange", "BIC": "red", "Standard Bank": "darkblue", "ATLANTICO": "darkred"}

    # FeatureGroup é necessário para a pesquisa funcionar
    grupo_atms = folium.FeatureGroup(name="ATMs Luanda")

    for atm in atms:
        cor_banco = cores_bancos.get(atm["banco"], "gray")
        cor_status = "green" if atm["dinheiro"] else "red"
        nome_busca = f"{atm['banco']} - {atm['local']}"
        
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
            tooltip=nome_busca,
            icon=folium.Icon(color=cor_banco, icon="info-sign"),
            name=nome_busca # Campo usado pela pesquisa
        ).add_to(grupo_atms)

    grupo_atms.add_to(mapa)

    # Adicionar Barra de Pesquisa
    Search(
        layer=grupo_atms,
        geom_type="Point",
        placeholder="Pesquisar Banco ou Local...",
        collapsed=False,
        search_label="name"
    ).add_to(mapa)

    mapa_html = mapa._repr_html_()
    
    # Layout Final com CSS para Header e Loader
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ margin: 0; padding: 0; overflow: hidden; }}
            #loader {{
                position: fixed; width: 100%; height: 100%; top: 0; left: 0;
                background: white; z-index: 10000; display: flex;
                flex-direction: column; align-items: center; justify-content: center;
                transition: opacity 0.5s ease;
            }}
            .spinner {{
                border: 8px solid #f3f3f3; border-top: 8px solid #27ae60;
                border-radius: 50%; width: 50px; height: 50px;
                animation: spin 1s linear infinite;
            }}
            @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
            
            .header {{
                position: fixed; top: 0; left: 0; width: 100%; z-index: 1000;
                background: #2c3e50; color: white; padding: 15px 0;
                text-align: center; font-family: sans-serif; font-weight: bold;
                box-shadow: 0 2px 10px rgba(0,0,0,0.3);
            }}
            #map-container {{ margin-top: 52px; height: calc(100vh - 52px); }}
            /* Ajuste da posição da barra de pesquisa do Folium */
            .leaflet-control-search {{ margin-top: 65px !important; }}
        </style>
    </head>
    <body>
        <div id="loader">
            <div class="spinner"></div>
            <p style="font-family:sans-serif; margin-top:15px; color:#2c3e50;">A carregar DINHEIRO AKI...</p>
        </div>

        <div class="header">
            🏧 DINHEIRO <span style="color:#27ae60;">AKI</span>
        </div>

        <div id="map-container">
            {mapa_html}
        </div>

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

# 3. LÓGICA DE ATUALIZAÇÃO
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