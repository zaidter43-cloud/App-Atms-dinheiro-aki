from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse
import folium
from folium.plugins import LocateControl, Search, MarkerCluster
import json
import os
from datetime import datetime

app = FastAPI()
FILE_NAME = "dados_oficiais.json"
ADMIN_PIN = "2424"

def carregar_dados():
    if not os.path.exists(FILE_NAME):
        # Lista base robusta
        dados = [
            {"id": 0, "banco": "BAI", "muni": "Luanda", "zona": "Marginal", "lat": -8.8105, "lng": 13.2355, "dinheiro": True},
            {"id": 1, "banco": "BFA", "muni": "Luanda", "zona": "Maianga", "lat": -8.8315, "lng": 13.2325, "dinheiro": True},
            {"id": 2, "banco": "BIC", "muni": "Talatona", "zona": "Shopping", "lat": -8.9185, "lng": 13.1815, "dinheiro": False},
            {"id": 3, "banco": "ATL", "muni": "Viana", "zona": "Viana Park", "lat": -8.9150, "lng": 13.3600, "dinheiro": True},
            {"id": 4, "banco": "STB", "muni": "Kilamba", "zona": "Bloco B", "lat": -8.9955, "lng": 13.2755, "dinheiro": True},
            {"id": 5, "banco": "SOL", "muni": "Luanda", "zona": "Ilha", "lat": -8.7940, "lng": 13.2200, "dinheiro": True},
            {"id": 6, "banco": "KEV", "muni": "Cazenga", "zona": "Cuca", "lat": -8.8355, "lng": 13.2865, "dinheiro": True}
        ]
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
    
    # Criar o mapa (Folium já cria um ecrã inteiro por defeito se não lhe dermos limites)
    mapa = folium.Map(
        location=[-8.8383, 13.2344], 
        zoom_start=13, 
        tiles="cartodbpositron", 
        zoom_control=False
    )
    
    # Injetar o CABEÇALHO e o SCRIPT DE SEGURANÇA diretamente no mapa
    # Isso garante que apareçam POR CIMA do mapa sem estragar os bancos
    script_seguranca = f"""
        <div style="position: fixed; top: 15px; left: 50%; transform: translateX(-50%); 
                    width: 85%; max-width: 350px; background: white; z-index: 9999; 
                    padding: 12px; border-radius: 30px; text-align: center; 
                    box-shadow: 0 4px 15px rgba(0,0,0,0.2); font-family: sans-serif; 
                    font-weight: bold; border-bottom: 3px solid #27ae60; pointer-events: none;">
            🏧 DINHEIRO <span style="color:#27ae60;">AKI</span>
        </div>
        <script>
            function authUpdate(id, status) {{
                var p = prompt("Código de Segurança (2424):");
                if(p == "{ADMIN_PIN}") {{ 
                    window.location.href = "/trocar?id=" + id + "&status=" + status; 
                }} else if (p != null) {{
                    alert("Código incorreto.");
                }}
            }}
        </script>
        <style>
            .leaflet-top {{ top: 80px !important; }}
        </style>
    """
    mapa.get_root().html.add_child(folium.Element(script_seguranca))

    # GPS
    LocateControl(auto_start=True, flyTo=True, locateOptions={"enableHighAccuracy": True}).add_to(mapa)

    # Cluster de Bancos
    cluster = MarkerCluster(name="Bancos").add_to(mapa)

    for atm in atms:
        cor = "green" if atm["dinheiro"] else "red"
        icon_html = f'''<div style="background-color: {cor}; border: 2.5px solid white; border-radius: 50%; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">{atm['banco']}</div>'''
        
        popup_html = f'''
        <div style="font-family: sans-serif; width: 170px; text-align: center;">
            <b style="font-size:16px;">{atm['banco']}</b><br><small style="color:gray;">{atm['zona']}</small><hr>
            Status: <b style="color:{cor};">{'COM NOTAS' if atm['dinheiro'] else 'VAZIO'}</b><br>
            <button onclick="authUpdate({atm['id']}, '{'false' if atm['dinheiro'] else 'true'}')" 
               style="margin-top:10px; padding:10px; width:100%; background:{cor}; color:white; border:none; border-radius:15px; font-weight:bold; cursor:pointer;">
               MUDAR STATUS
            </button>
        </div>
        '''
        folium.Marker(
            location=[atm["lat"], atm["lng"]],
            popup=folium.Popup(popup_html, max_width=250),
            icon=folium.DivIcon(html=icon_html),
            name=f"{atm['banco']} {atm['zona']}"
        ).add_to(cluster)

    # Pesquisa
    Search(layer=cluster, geom_type="Point", placeholder="Procurar banco...", collapsed=False, search_label="name").add_to(mapa)

    # Retornar o mapa puro (o Folium trata do ecrã inteiro automaticamente assim)
    return HTMLResponse(content=mapa._repr_html_())

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
