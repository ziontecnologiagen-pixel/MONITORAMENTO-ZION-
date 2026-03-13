import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. CONFIGURAÇÕES DA PÁGINA
st.set_page_config(page_title="Zion - Torre de Controle", layout="wide")

# Link base da sua planilha
SHEET_ID = "1izHisQGFCLdqQ7d2OSGkAM7gDJrIsLxW9FY741lJ_Ao"

# IDs das abas (GIDs) que vimos no seu vídeo
GID_RANCHO = "1366334206"
GID_ODM = "0" # Geralmente a primeira aba é 0, se não funcionar tentaremos o ID específico

@st.cache_data(ttl=600) # Atualiza a cada 10 minutos
def carregar_dados(gid):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"
    return pd.read_csv(url)

st.title("🚢 Zion Tecnologia - Monitoramento Integrado")
st.markdown("---")

try:
    # Carregando os dados
    df_rancho = carregar_dados(GID_RANCHO)
    df_odm = carregar_dados(GID_ODM)

    # --- SEÇÃO RANCHO ---
    st.subheader("🥪 1. PROGRAMAÇÃO DE RANCHO")
    if not df_rancho.empty:
        # Mostra as colunas que vimos no vídeo
        cols_r = ['EMPURRADOR', 'LIMITE PEDIDO', 'PRÓXIMO']
        # Filtra apenas se as colunas existirem
        disponiveis = [c for c in cols_r if c in df_rancho.columns]
        st.dataframe(df_rancho[disponiveis], use_container_width=True)
    
    st.divider()

    # --- SEÇÃO ODM ---
    st.subheader("⛽ 2. MONITORAMENTO ODM (COM MARÇO)")
    if not df_odm.empty:
        st.dataframe(df_odm, use_container_width=True)

    # --- SEÇÃO GRÁFICOS ---
    st.divider()
    st.subheader("📊 3. EVOLUÇÃO DE CONSUMO")
    
    # Exemplo de gráfico com dados da planilha
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=[100, 150, 130], name='Previsto', line=dict(color='blue', width=3)))
    fig.add_trace(go.Scatter(y=[90, 160, 120], name='Realizado', line=dict(color='red', width=3)))
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Erro ao conectar com a planilha: {e}")
    st.info("Certifique-se de que a planilha está compartilhada como 'Qualquer pessoa com o link'.")

st.caption("Atualizado em tempo real via Google Sheets")
