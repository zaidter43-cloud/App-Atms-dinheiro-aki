from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse
import folium
from folium.plugins import LocateControl, Search, MarkerCluster
import json
import os
from datetime import datetime

app = FastAPI()
FILE_NAME = "dados_final_v7.json"

# 1. BASE DE DADOS EXPANDIDA (LUANDA COMPLETA)
def carregar_dados():
    if not os.path.exists(FILE_NAME):
        dados = [
            # LUANDA CENTRO
            {"id": 0, "banco": "BAI", "muni": "Luanda", "zona": "Marginal", "lat": -8.8105, "lng": 13.2355, "dinheiro": True},
            {"id": 1, "banco": "BFA", "muni": "Luanda", "zona": "Maianga", "lat": -8.8315, "lng": 13.2325, "dinheiro": True},
            {"id": 2, "banco": "BIC", "muni": "Luanda", "zona": "Mutamba", "lat": -8.8135, "lng": 13.2305, "dinheiro": False},
            {"id": 3, "banco": "SOL", "muni": "Luanda", "zona": "Ilha", "lat": -8.7940, "lng": 13.2200, "dinheiro": True},
            # TALATONA / NOVA VIDA
            {"id": 4, "banco": "ATL", "muni": "Talatona", "zona": "Cidade Financeira", "lat": -8.9240, "lng": 13.1850, "dinheiro": True},
            {"id": 5, "banco": "BIC", "muni": "Talatona", "zona": "Shopping", "lat": -8.9185, "lng": 13.1815, "dinheiro": True},
            {"id": 6, "banco": "BAI", "muni": "Talatona", "zona": "Kero Ginga", "lat": -8.9100, "lng": 13.1950, "dinheiro": False},
            # VIANA / ZANGO
            {"id": 7, "banco": "BFA", "muni": "Viana", "zona": "Viana Park", "lat": -8.9150, "lng": 13.3600, "dinheiro": True},
            {"id": 8, "banco": "BAI", "muni": "Viana", "zona": "Zango 3", "lat": -9.0020, "lng": 13.4550, "dinheiro": True},
            {"id": 9, "banco": "SOL", "muni": "Viana", "zona": "Ponte", "lat": -8.9060, "lng": 13.3760, "dinheiro": False},
            # KILAMBA
            {"id": 10, "banco": "STB", "muni": "Kilamba", "zona": "Bloco B", "lat": -8.9955, "lng": 13.2755, "dinheiro": True},
            {"id": 11, "banco": "BCI", "muni": "Kilamba", "zona": "Shopping", "lat": -9.0050, "lng": 13.2800, "dinheiro": True},
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
    
    # Configuração do Mapa (Estilo Google Maps Moderno)
    mapa = folium.Map(location=[-8.8383, 13.2344], zoom_start=13, tiles="cartodbpositron", zoom_control=False)
    
    # GPS DE ALTA PRECISÃO
    LocateControl(
        auto_start=False, flyTo=True, keepCurrentZoomLevel=False,
        locateOptions={"enableHighAccuracy": True},
        strings={"title": "Minha Localização"}
    ).add_to(mapa)

    # GRUPOS PARA FILTRAGEM (Camadas)
    cluster_geral = MarkerCluster(name="Todos os Bancos").add_to(mapa)
    grupo_disponiveis = folium.FeatureGroup(name="✅ Apenas com Dinheiro", show=False).add_to(mapa)

    for atm in atms:
        cor_status = "green" if atm["dinheiro"] else "red"
        status_texto = "COM DINHEIRO" if atm["dinheiro"] else "SEM NOTAS"
        label = f"{atm['banco']} - {atm['zona']} ({atm['muni']})"
        
        # Ícone Profissional com Sigla
        icon_html = f"""<div style="background-color: {cor_status}; border: 2px solid white; border-radius: 50%; width: 34px; height: 34px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 9px; box-shadow: 0 2px 6px rgba(0,0,0,0.4);">{atm['banco']}</div>"""
        
        popup_content = f"""
            <div style='font-family: sans-serif; width: 170px;'>
                <b style='font-size:14px;'>{atm['banco']}</b><br>
                <span style='color:gray;'>{atm['zona']}</span><br><br>
                Status: <b style='color:{cor_status};'>{status_texto}</b><br>
                <small>Atualizado: {atm['hora']}</small><br><hr>
                <a href='/trocar?id={atm['id']}&status={'false' if atm['dinheiro'] else 'true'}' 
                   style='display:block; padding:10px; background:{cor_status}; color:white; text-decoration:none; border-radius:6px; text-align:center; font-weight:bold;'>
                   ATUALIZAR STATUS
                </a>
            </div>
        """
        
        marker = folium.Marker(
            location=[atm["lat"], atm["lng"]],
            popup=folium.Popup(popup_content, max_width=250),
            icon=folium.DivIcon(html=icon_html),
            name=label
        )
        
        # Adiciona ao cluster principal
        marker.add_to(cluster_geral)
        
        # Se tiver dinheiro, adiciona também à camada de filtro
        if atm["dinheiro"]:
            folium.Marker(
                location=[atm["lat"], atm["lng"]],
                popup=folium.Popup(popup_content),
                icon=folium.DivIcon(html=icon_html)
            ).add_to(grupo_disponiveis)

    # CONTROLOS: PESQUISA E CAMADAS
    Search(layer=cluster_geral, geom_type="Point", placeholder="Procurar zona ou banco...",
           collapsed=False, search_label="name").add_to(mapa)
    
    folium.LayerControl(position='topright', collapsed=False).add_to(mapa)

    mapa_html = mapa._repr_html_()
    
    # HTML E CSS PARA ECRÃ TOTAL E DESIGN APP
    full_html = f"""
    <!DOCTYPE html>
    <html style="height: 100%;">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <style>
            body, html {{ height: 100%; width: 100%; margin: 0; padding: 0; overflow: hidden; font-family: -apple-system, sans-serif; }}
            #map-container {{ height: 100vh; width: 100vw; position: absolute; top: 0; left: 0; z-index: 0; }}
            .app-header {{
                position: fixed; top: 15px; left: 50%; transform: translateX(-50%);
                width: 80%; max-width: 350px; z-index