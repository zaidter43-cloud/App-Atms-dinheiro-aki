from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse
import folium
from folium.plugins import LocateControl, Search
import json
import os
from datetime import datetime

app = FastAPI()
# v4 para carregar a nova estrutura de municípios
FILE_NAME = "dados_v4.json"

def carregar_dados():
    if not os.path.exists(FILE_NAME):
        # 30 LOCALIZAÇÕES REAIS DIVIDIDAS POR MUNICÍPIOS
        dados_municipios = [
            # LUANDA (CENTRO)
            {"id": 0, "banco": "BAI", "municipio": "Luanda", "local": "Sede Marginal", "lat": -8.8105, "lng": 13.2355, "dinheiro": True, "hora": "08:00"},
            {"id": 1, "banco": "BFA", "local": "Maianga", "lat": -8.8315, "lng": 13.2325, "dinheiro": True, "hora": "08:00"},
            {"id": 2, "banco": "BIC", "local": "Mutamba", "lat": -8.8135, "lng": 13.2305, "dinheiro": False, "hora": "09:30"},
            {"id": 3, "banco": "SOL", "local": "Ilha de Luanda", "lat": -8.7940, "lng": 13.2200, "dinheiro": True, "hora": "10:00"},
            {"id": 4, "banco": "BCI", "local": "Alvalade", "lat": -8.8390, "lng": 13.2430, "dinheiro": True, "hora": "07:45"},
            
            # TALATONA
            {"id": 5, "banco": "ATL", "municipio": "Talatona", "local": "Cidade Financeira", "lat": -8.9240, "lng": 13.1850, "dinheiro": True, "hora": "11:00"},
            {"id": 6, "banco": "BIC", "local": "Talatona Shopping", "lat": -8.9185, "lng": 13.1815, "dinheiro": True, "hora": "12:15"},
            {"id": 7, "banco": "STB", "local": "SIAC Talatona", "lat": -8.9350, "lng": 13.1900, "dinheiro": False, "hora": "14:00"},
            {"id": 8, "banco": "BAI", "local": "Kero Ginga Shopping", "lat": -8.9100, "lng": 13.1950, "dinheiro": True, "hora": "08:30"},
            
            # BELAS & BENFICA
            {"id": 9, "banco": "BFA", "municipio": "Belas", "local": "Belas Shopping", "lat": -8.9280, "lng": 13.1780, "dinheiro": True, "hora": "09:00"},
            {"id": 10, "banco": "BAI", "local": "Morro Bento", "lat": -8.8940, "lng": 13.1930, "dinheiro": False, "hora": "13:45"},
            {"id": 11, "banco": "BIC", "local": "Benfica (Estrada Direita)", "lat": -8.9450, "lng": 13.1900, "dinheiro": True, "hora": "10:20"},
            {"id": 12, "banco": "ECON", "local": "Futungo", "lat": -8.9050, "lng": 13.1750, "dinheiro": True, "hora": "15:00"},

            # VIANA
            {"id": 13, "banco": "BIC", "municipio": "Viana", "local": "Ponte de Viana", "lat": -8.9060, "lng": 13.3760, "dinheiro": True, "hora": "09:15"},
            {"id": 14, "banco": "BFA", "local": "Viana Park", "lat": -8.9150, "lng": 13.3600, "dinheiro": False, "hora": "11:30"},
            {"id": 15, "banco": "BAI", "local": "Zango 3 (Multicenter)", "lat": -9.0020, "lng": 13.4550, "dinheiro": True, "hora": "08:15"},
            {"id": 16, "banco": "ATL", "local": "Estalagem", "lat": -8.8900, "lng": 13.3400, "dinheiro": True, "hora": "10:45"},
            
            # KILAMBA & CAMAMA
            {"id": 17, "banco": "STB", "municipio": "Kilamba", "local": "Kilamba (Bloco B)", "lat": -8.9955, "lng": 13.2755, "dinheiro": True, "hora": "09:50"},
            {"id": 18, "banco": "BAI", "local": "Kilamba (Shopping)", "lat": -9.0050, "lng": 13.2800, "dinheiro": False, "hora": "12:00"},
            {"id": 19, "banco": "BFA", "local": "Camama (Jardim do Eden)", "lat": -8.9350, "lng": 13.2650, "dinheiro": True, "hora": "14:20"},
            {"id": 20, "banco": "SOL", "local": "Calemba 2", "lat": -8.9200, "lng": 13.2900, "dinheiro": True, "hora": "11:00"},

            # CAZENGA & SAMBIZANGA
            {"id": 21, "banco": "KEV", "municipio": "Cazenga", "local": "Cuca", "lat": -8.8355, "lng": 13.2865, "dinheiro": True, "hora": "09: