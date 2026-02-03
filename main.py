from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse
import folium
from folium.plugins import LocateControl
import json
import os
from datetime import datetime

# 1. INICIALIZAÇÃO
app = FastAPI()
# Mudamos o nome para v2 para o sistema carregar a lista nova de 15 bancos
FILE_NAME = "dados_v2.json"

# 2. GESTÃO DE DADOS
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

# 3. INTERFACE
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
                <p style='font-size:10px;'>Atualizado: {atm['hora']}</p>
                <hr>
                <a href='/trocar?id={atm['id']}&status={'false' if atm['dinheiro'] else 'true'}' 
                   style='display:block; padding:10px; background:{cor_status}; color:white; text-decoration:none; border-radius:5px; text-align:center; font-weight:bold;'>
                   ATUALIZAR STATUS
                </a>
            </div>
        """
        folium.Marker(location=[atm["lat"], atm["lng"]], 
                      popup=folium.Popup(botao_html, max_width=250),
                      icon=folium.Icon(color=cor_banco, icon=icone_status, prefix="fa")).add_to(mapa)

    mapa