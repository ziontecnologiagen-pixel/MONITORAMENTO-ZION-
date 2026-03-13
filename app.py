import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import plotly.graph_objects as go

# 1. CONFIGURAÇÕES E CONEXÃO
st.set_page_config(page_title="Zion - Torre de Controle", layout="wide")

def carregar_dados():
    # Escopo para as planilhas do Google
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    
    # PEGAR AS CREDENCIAIS DOS SECRETS DO STREAMLIT
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    
    # ID da sua planilha (peguei do vídeo)
    spreadsheet_id = "1O3o9B5uE2v-k9P-m_T_P_D_D_D_D_D_D_D" # Vamos ajustar isso
    sh = client.open_by_key(st.secrets["spreadsheet_id"])
    
    # Lendo as abas conforme o vídeo
    df_rancho = pd.DataFrame(sh.worksheet("RANCHO").get_all_records())
    df_odm = pd.DataFrame(sh.worksheet("COM MARÇO").get_all_records())
    
    return df_rancho, df_odm

# Interface Visual
st.title("🚢 Monitoramento Zion em Tempo Real")

try:
    df_r, df_o = carregar_dados()

    # --- SEÇÃO 1: RANCHO (Conforme o vídeo 0:05) ---
    st.subheader("🥪 PROXIMOS RESSUPRIMENTOS (RANCHO)")
    # Filtrando apenas as colunas que você mostrou no vídeo
    colunas_rancho = ['EMPURRADOR', 'LIMITE PEDIDO', 'PRÓXIMO']
    st.dataframe(df_r[colunas_rancho], use_container_width=True)

    # --- SEÇÃO 2: ODM (Conforme o vídeo 0:00) ---
    st.subheader("⛽ PROGRAMAÇÃO E REALIZADOS ODM")
    # Mostra a tabela de ODM (COM MARÇO)
    st.dataframe(df_o, use_container_width=True)

except Exception as e:
    st.error("Aguardando configuração das chaves de acesso da Planilha...")
    st.info("Alex, precisamos colocar as 'Secrets' no painel do Streamlit para o gráfico aparecer.")
