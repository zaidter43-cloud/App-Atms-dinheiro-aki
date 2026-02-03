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
        # Base de dados inicial com localizações em Luanda
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

# 3. INTERFACE DO MAPA (WEB FRONTIER)
@app.get("/", response_class=HTMLResponse)
def mostrar_mapa():
    atms = carregar_dados()
    # Centrado em Luanda
    mapa = folium.Map(location=[-8.8383, 13.2344], zoom_start=12)
    LocateControl().add_to(mapa)

    # Cores Oficiais
    cores_bancos = {
        "BAI": "blue",
        "BFA": "orange",
        "BIC": "red",
        "Standard Bank": "darkblue",
        "ATLANTICO": "darkred"
    }

    for atm in atms:
        cor_banco = cores_bancos.get(atm["banco"], "gray")
        cor_status = "green" if atm["dinheiro"] else "red"
        icone_status = "check" if atm["dinheiro"] else "times"
        texto_status = "COM DINHEIRO" if atm["dinheiro"] else "SEM DINHEIRO"
        novo_status = "false" if atm["dinheiro"] else "true"
        
        botao_html = f"""
            <div style='font-family: sans-serif; width: 180px;'>
                <h4 style='margin:0; color:{cor_banco};'>{atm['banco']}</h4>
                <p style='font-size:12px; color:gray;'>{atm['local']}</p>
                <p>Status: <b style='color:{cor_status};'>{texto_status}</b></p>
                <p style='font-size:10px;'>Atualizado: {atm['hora']}</p>
                <hr style='border: 0.5px solid #eee;'>
                <a href='/trocar?id={atm['id']}&status={novo_status}' 
                   style='display:block; padding:10px; background:{cor_status}; color:white; text-decoration:none; border-radius:5px; text-align:center; font-weight:bold;'>
                   ATUALIZAR STATUS
                </a>
            </div>
        """
        
        folium.Marker(
            location=[atm["lat"], atm["lng"]],
            popup=folium.Popup(botao_html, max_width=250),
            icon=folium.Icon(color=cor_banco, icon=icone_status, prefix="fa")
        ).add_to(mapa)

    return mapa._repr_html_()

# 4. LÓGICA DE ATUALIZAÇÃO E CONFIRMAÇÃO
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
    
    # Página de sucesso estilizada
    return HTMLResponse(content=f"""
        <html>
            <body style="font-family: sans-serif; text-align: center; padding-top: 100px; background-color: #f4f4f9;">
                <div style="display: inline-block; background: white; padding: 40px; border-radius: 15px; shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <h1 style="color: #2ecc71;">✅ Atualizado!</h1>
                    <p style="color: #555;">Obrigado por ajudar a comunidade <b>Dinheiro Aki</b>.</p>
                    <p>A redirecionar para o mapa...</p>
                    <br>
                    <a href="/" style="color: #3498db; text-decoration: none;">Clique aqui se não for redirecionado</a>
                </div>
                <script>
                    setTimeout(function(){{ window.location.href = "/"; }}, 2500);
                </script>
            </body>
        </html>
    """)