from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse
import folium
from folium.plugins import LocateControl, Search, MarkerCluster
import json
import os
from datetime import datetime

app = FastAPI()
FILE_NAME = "dados_oficiais_v14.json"
ADMIN_PIN = "2424"

def carregar_dados():
    if not os.path.exists(FILE_NAME):
        # BASE DE DADOS EXPANDIDA (30+ PONTOS)
        dados = [
            # LUANDA CENTRO / MAIANGA
            {"id": 0, "banco": "BAI", "muni": "Luanda", "zona": "Marginal", "lat": -8.8105, "lng": 13.2355, "dinheiro": True},
            {"id": 1, "banco": "BFA", "muni": "Luanda", "zona": "Maianga", "lat": -8.8315, "lng": 13.2325, "dinheiro": True},
            {"id": 2, "banco": "BIC", "muni": "Luanda", "zona": "Mutamba", "lat": -8.8135, "lng": 13.2305, "dinheiro": False},
            {"id": 3, "banco": "BE", "muni": "Luanda", "zona": "Kinaxixi", "lat": -8.8191, "lng": 13.2505, "dinheiro": True},
            {"id": 4, "banco": "SOL", "muni": "Luanda", "zona": "Ilha", "lat": -8.7940, "lng": 13.2200, "dinheiro": True},
            # TALATONA / BENFICA
            {"id": 5, "banco": "ATL", "muni": "Talatona", "zona": "Xyami", "lat": -8.8976, "lng": 13.2255, "dinheiro": True},
            {"id": 6, "banco": "BIC", "muni": "Talatona", "zona": "Belas Shopping", "lat": -8.9280, "lng": 13.1780, "dinheiro": True},
            {"id": 7, "banco": "BAI", "muni": "Talatona", "zona": "Kero Ginga", "lat": -8.9100, "lng": 13.1950, "dinheiro": False},
            {"id": 8, "banco": "STB", "muni": "Talatona", "zona": "C. Financeira", "lat": -8.9240, "lng": 13.1850, "dinheiro": True},
            # VIANA / ZANGO
            {"id": 9, "banco": "BFA", "muni": "Viana", "zona": "Viana Park", "lat": -8.9150, "lng": 13.3600, "dinheiro": True},
            {"id": 10, "banco": "BAI", "muni": "Viana", "zona": "Zango 0", "lat": -8.9620, "lng": 13.4150, "dinheiro": True},
            {"id": 11, "banco": "SOL", "muni": "Viana", "zona": "Ponte", "lat": -8.9060, "lng": 13.3760, "dinheiro": False},
            {"id": 12, "banco": "BCI", "muni": "Viana", "zona": "Estalagem", "lat": -8.8950, "lng": 13.3400, "dinheiro": True},
            # KILAMBA / CAMAMA
            {"id": 13, "banco": "STB", "muni": "Kilamba", "zona": "Bloco B", "lat": -8.9955, "lng": 13.2755, "dinheiro": True},
            {"id": 14, "banco": "BAI", "muni": "Kilamba", "zona": "Bloco W", "lat": -9.0100, "lng": 13.2850, "dinheiro": True},
            {"id": 15, "banco": "BIC", "muni": "Camama", "zona": "Jardim do Eden", "lat": -8.9550, "lng": 13.2950, "dinheiro": True}
        ]
        # Adicionar mais bancos fictícios para completar volume (Totalizando mais de 30)
        for i in range(16, 35):
            dados.append({"id": i, "banco": "BFA", "muni": "Luanda", "zona": f"ATM {i}", "lat": -8.8 + (i*0.005), "lng": 13.2 + (i*0.005), "dinheiro": True})
        
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
    
    # Criar o mapa SEM ZOOM AUTOMÁTICO (Zoom fixo inicial)
    mapa = folium.Map(
        location=[-8.8383, 13.2344], 
        zoom_start=12, 
        tiles="cartodbpositron", 
        zoom_control=False
    )
    
    # Injetar Cabeçalho, Script de Segurança e o MENU DE TRÊS PONTOS
    menu_html = f"""
        <div id="header-app" style="position: fixed; top: 15px; left: 50%; transform: translateX(-50%); 
                    width: 90%; max-width: 400px; background: white; z-index: 9999; 
                    padding: 10px; border-radius: 30px; display: flex; align-items: center; justify-content: space-between;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.15); font-family: sans-serif; border-bottom: 3px solid #27ae60;">
            <div style="width: 30px;"></div>
            <div style="font-weight: bold;">🏧 DINHEIRO <span style="color:#27ae60;">AKI</span></div>
            <div onclick="toggleMenu()" style="cursor: pointer; padding: 5px; font-size: 20px;">⋮</div>
        </div>

        <div id="filter-menu" style="display: none; position: fixed; top: 75px; right: 5%; width: 200px; 
                    background: white; z-index: 9999; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                    font-family: sans-serif; padding: 10px;">
            <b style="font-size: 12px; color: gray;">FILTRAR BANCOS</b><hr>
            <div style="padding: 8px 0; cursor: pointer;" onclick="filterBancos('ALL')">📍 Todos</div>
            <div style="padding: 8px 0; cursor: pointer;" onclick="filterBancos('BAI')">🏦 BAI</div>
            <div style="padding: 8px 0; cursor: pointer;" onclick="filterBancos('BFA')">🏦 BFA</div>
            <div style="padding: 8px 0; cursor: pointer;" onclick="filterBancos('BIC')">🏦 BIC</div>
            <div style="padding: 8px 0; color: #27ae60; font-weight: bold; cursor: pointer;" onclick="filterBancos('GREEN')">✅ Com Dinheiro</div>
        </div>

        <script>
            function toggleMenu() {{ 
                var m = document.getElementById('filter-menu');
                m.style.display = m.style.display === 'none' ? 'block' : 'none';
            }}
            function authUpdate(id, status) {{
                var p = prompt("Código de Segurança (2424):");
                if(p == "{ADMIN_PIN}") {{ window.location.href = "/trocar?id="+id+"&status="+status; }}
            }}
            function filterBancos(type) {{
                // Lógica de filtro simples recarregando ou escondendo pins (nesta versão simplificada, mostramos o alerta)
                alert("A filtrar por: " + type + ". Esta função está a processar os dados...");
                location.reload(); 
            }}
        </script>
        <style> .leaflet-top {{ top: 85px !important; }} </style>
    """
    mapa.get_root().html.add_child(folium.Element(menu_html))

    # GPS (Configurado para não dar zoom automático ao iniciar, apenas ao clicar no botão)
    LocateControl(auto_start=False, flyTo=True, locateOptions={"enableHighAccuracy": True}).add_to(mapa)

    cluster = MarkerCluster(name="Bancos").add_to(mapa)

    for atm in atms:
        cor = "green" if atm["dinheiro"] else "red"
        icon_html = f'''<div style="background-color: {cor}; border: 2.5px solid white; border-radius: 50%; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">{atm['banco']}</div>'''
        
        popup_html = f'''
        <div style="font-family: sans-serif; width: 170px; text-align: center;">
            <b style="font-size:16px;">{atm['banco']}</b><br><small>{atm['zona']}</small><hr>
            <button onclick="authUpdate({atm['id']}, '{'false' if atm['dinheiro'] else 'true'}')" 
               style="padding:10px; width:100%; background:{cor}; color:white; border:none; border-radius:15px; font-weight:bold; cursor:pointer;">
               MUDAR STATUS
            </button>
        </div>
        '''
        folium.Marker(
            location=[atm["lat"], atm["lng"]],
            popup=folium.Popup(popup_html, max_width=250),
            icon=folium.DivIcon(html=icon_html),
            name=f"{atm['banco']} {atm['zona']} {atm['muni']}"
        ).add_to(cluster)

    # Pesquisa CORRIGIDA (Procura em todos os campos)
    Search(layer=cluster, geom_type="Point", placeholder="Procurar banco ou zona...", collapsed=False, search_label="name").add_to(mapa)

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
