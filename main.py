from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse
import folium
from folium.plugins import LocateControl, Search, MarkerCluster
import json
import os
from datetime import datetime

app = FastAPI()
FILE_NAME = "dados_v15.json"
ADMIN_PIN = "2424"

def carregar_dados():
    if not os.path.exists(FILE_NAME):
        # Base de dados robusta com 30+ pontos em Luanda
        dados = [
            {"id": 0, "banco": "BAI", "muni": "Luanda", "zona": "Marginal", "lat": -8.8105, "lng": 13.2355, "dinheiro": True},
            {"id": 1, "banco": "BFA", "muni": "Luanda", "zona": "Maianga", "lat": -8.8315, "lng": 13.2325, "dinheiro": True},
            {"id": 2, "banco": "BIC", "muni": "Talatona", "zona": "Belas Shopping", "lat": -8.9280, "lng": 13.1780, "dinheiro": True},
            {"id": 3, "banco": "ATL", "muni": "Viana", "zona": "Viana Park", "lat": -8.9150, "lng": 13.3600, "dinheiro": True},
            {"id": 4, "banco": "STB", "muni": "Kilamba", "zona": "Bloco B", "lat": -8.9955, "lng": 13.2755, "dinheiro": True},
            {"id": 5, "banco": "SOL", "muni": "Cazenga", "zona": "Cuca", "lat": -8.8355, "lng": 13.2865, "dinheiro": False},
            {"id": 6, "banco": "BE", "muni": "Luanda", "zona": "Kinaxixi", "lat": -8.8191, "lng": 13.2505, "dinheiro": True},
            {"id": 7, "banco": "BCI", "muni": "Sambizanga", "zona": "Mercado", "lat": -8.8050, "lng": 13.2550, "dinheiro": False},
        ]
        # Gerar mais pontos para completar volume
        for i in range(8, 35):
            dados.append({"id": i, "banco": "BFA", "muni": "Luanda", "zona": f"ATM Zona {i}", "lat": -8.82 + (i*0.006), "lng": 13.24 + (i*0.004), "dinheiro": True})
        
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
    # Mapa focado em Luanda sem zoom automático invasivo
    mapa = folium.Map(location=[-8.8383, 13.2344], zoom_start=13, tiles="cartodbpositron", zoom_control=False)
    
    # Injetar CSS e Menu flutuante
    menu_ui = f"""
    <div style="position: fixed; top: 15px; left: 50%; transform: translateX(-50%); width: 90%; max-width: 400px; background: white; z-index: 9999; padding: 12px; border-radius: 30px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 4px 15px rgba(0,0,0,0.2); font-family: sans-serif; border-bottom: 3px solid #27ae60;">
        <div style="width: 30px;"></div>
        <div style="font-weight: bold; letter-spacing: 1px;">🏧 DINHEIRO <span style="color:#27ae60;">AKI</span></div>
        <div onclick="document.getElementById('side-menu').style.display='block'" style="cursor: pointer; font-size: 20px; font-weight: bold; padding-right: 10px;">⋮</div>
    </div>
    <div id="side-menu" style="display: none; position: fixed; top: 75px; right: 20px; width: 180px; background: white; z-index: 10000; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); font-family: sans-serif; padding: 15px;">
        <div style="text-align: right; cursor: pointer; color: red;" onclick="this.parentElement.style.display='none'">✖</div>
        <b style="font-size: 12px;">FILTROS</b><hr>
        <div style="padding: 10px 0; cursor: pointer;" onclick="location.reload()">🔄 Todos os Bancos</div>
        <div style="padding: 10px 0; cursor: pointer; color: green;" onclick="alert('Filtro: Apenas Disponíveis')">✅ Com Dinheiro</div>
    </div>
    <script>
        function authUpdate(id, status) {{
            var p = prompt("Código 2424:");
            if(p == "{ADMIN_PIN}") {{ window.location.href = "/trocar?id="+id+"&status="+status; }}
        }}
    </script>
    <style>.leaflet-top {{ top: 80px !important; }}</style>
    """
    mapa.get_root().html.add_child(folium.Element(menu_ui))

    LocateControl(auto_start=False, flyTo=True).add_to(mapa)
    cluster = MarkerCluster(name="Bancos").add_to(mapa)

    for atm in atms:
        cor = "green" if atm["dinheiro"] else "red"
        icon_html = f'<div style="background-color: {cor}; border: 2px solid white; border-radius: 50%; width: 34px; height: 34px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 9px;">{atm["banco"]}</div>'
        
        folium.Marker(
            location=[atm["lat"], atm["lng"]],
            popup=folium.Popup(f'<div style="text-align:center;font-family:sans-serif;"><b>{atm["banco"]}</b><br>{atm["zona"]}<br><button onclick="authUpdate({atm["id"]}, \'{"false" if atm["dinheiro"] else "true"}\')" style="background:{cor};color:white;border:none;border-radius:10px;padding:8px;margin-top:10px;">ATUALIZAR</button></div>', max_width=200),
            icon=folium.DivIcon(html=icon_html),
            name=f"{atm['banco']} {atm['zona']} {atm['muni']}"
        ).add_to(cluster)

    Search(layer=cluster, geom_type="Point", placeholder="Procurar zona ou banco...", collapsed=False, search_label="name").add_to(mapa)
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
