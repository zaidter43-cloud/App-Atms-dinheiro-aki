from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse
import folium
from folium.plugins import LocateControl
import json
import os
from datetime import datetime

# 1. INICIALIZAÇÃO
app = FastAPI()
FILE_NAME = "dados_atms.json"

# 2. GESTÃO DE DADOS (MEMÓRIA)
def carregar_dados():
    if not os.path.exists(FILE_NAME):
        dados_iniciais = [
            {"id": 0, "banco": "BAI", "local": "Sede - Luanda", "lat": -8.8147, "lng": 13.2302, "dinheiro": True, "hora": "Sem dados"},
            {"id": 1, "banco": "BFA", "local": "Talatona Shopping", "lat": -8.9180, "lng": 13.1810, "dinheiro": False, "hora": "Sem dados"},
            {"id": 2, "banco": "BIC", "local": "Aeroporto", "lat": -8.8500, "lng": 13.2333, "dinheiro": True, "hora": "Sem dados"},
            {"id": 3, "banco": "Standard Bank", "local": "Kilamba", "lat": -8.9950, "lng": 13.2750, "dinheiro": True, "hora": "Sem dados"},
            {"id": 4, "banco": "ATLANTICO", "local": "Viana", "lat": -8.9050, "lng": 13.3750, "dinheiro": False, "hora": "Sem dados"},
        ]
        salvar_dados(dados_iniciais)
        return dados_iniciais
    with open(FILE_NAME, "r") as f:
        return json.load(f)

def salvar_dados(dados):
    with open(FILE_NAME, "w") as f:
        json.dump(dados, f, indent=4)

# 3. INTERFACE DO MAPA COM TÍTULO PROFISSIONAL
# ... (as partes do carregar_dados e salvar_dados continuam iguais acima)

@app.get("/", response_class=HTMLResponse)
def mostrar_mapa():
    atms = carregar_dados()
    mapa = folium.Map(location=[-8.8383, 13.2344], zoom_start=12)
    LocateControl().add_to(mapa)

    cores_bancos = {"BAI": "blue", "BFA": "orange", "BIC": "red", "Standard Bank": "darkblue", "ATLANTICO": "darkred"}

    for atm in atms:
        cor_banco = cores_bancos.get(atm["banco"], "gray")
        cor_status = "green" if atm["dinheiro"] else "red"
        icone_status = "check" if atm["dinheiro"] else "times"
        
        botao_html = f"""
            <div style='font-family: sans-serif; width: 180px;'>
                <h4 style='margin:0; color:{cor_banco};'>{atm['banco']}</h4>
                <p style='font-size:12px; color:gray;'>{atm['local']}</p>
                <p>Status: <b style='color:{cor_status};'>{'COM DINHEIRO' if atm['dinheiro'] else 'SEM DINHEIRO'}</b></p>
                <hr>
                <a href='/trocar?id={atm['id']}&status={'false' if atm['dinheiro'] else 'true'}' 
                   style='display:block; padding:8px; background:{cor_status}; color:white; text-decoration:none; border-radius:5px; text-align:center; font-weight:bold;'>
                   ATUALIZAR
                </a>
            </div>
        """
        folium.Marker(location=[atm["lat"], atm["lng"]], 
                      popup=folium.Popup(botao_html, max_width=250),
                      icon=folium.Icon(color=cor_banco, icon=icone_status, prefix="fa")).add_to(mapa)

    mapa_html = mapa._repr_html_()
    
    # NOVO: HTML COM TÍTULO CORRIGIDO E ECRÃ DE CARREGAMENTO
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            /* Ecrã de Carregamento */
            #loader {{
                position: fixed; width: 100%; height: 100%; top: 0; left: 0;
                background: white; z-index: 10000; display: flex;
                flex-direction: column; align-items: center; justify-content: center;
                transition: opacity 0.5s ease;
            }}
            .spinner {{
                border: 8px solid #f3f3f3; border-top: 8px solid #27ae60;
                border-radius: 50%; width: 60px; height: 60px;
                animation: spin 1s linear infinite;
            }}
            @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}

            /* Título que cobre a parte de cima (NavBar) */
            .header {{
                position: fixed; top: 0; left: 0; width: 100%; z-index: 9999;
                background: #2c3e50; color: white; padding: 15px 0;
                text-align: center; font-family: sans-serif; box-shadow: 0 2px 10px rgba(0,0,0,0.3);
            }}
        </style>
    </head>
    <body style="margin:0;">
        <div id="loader">
            <div class="spinner"></div>
            <p style="font-family:sans-serif; margin-top:20px; color:#2c3e50;">A carregar mapa de Luanda...</p>
        </div>

        <div class="header">
            <span style="font-size: 20px; font-weight: bold;">🏧 DINHEIRO <span style="color:#27ae60;">AKI</span></span>
        </div>

        <div style="margin-top: 50px;">
            {mapa_html}
        </div>

        <script>
            window.onload = function() {{
                setTimeout(function() {{
                    document.getElementById('loader').style.opacity = '0';
                    setTimeout(function() {{
                        document.getElementById('loader').style.display = 'none';
                    }}, 500);
                }}, 1000);
            }};
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=full_html)

# 4. LÓGICA DE ATUALIZAÇÃO
@app.get("/trocar")
def trocar_status(id: int, status: str):
    atms = carregar_dados()
    tem_dinheiro = (status.lower() == "true")
    hora_agora = datetime.now().strftime("%H:%M")
    
    for atm in atms:
        if atm["id"] == id:
            atm["dinheiro"] = tem_dinheiro
            atm["hora"] = hora_agora
            break
            
    salvar_dados(atms)
    return RedirectResponse(url="/")