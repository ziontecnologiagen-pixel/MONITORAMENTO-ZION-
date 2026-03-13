import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import plotly.graph_objects as go

# 1. CONFIGURAÇÕES DA PÁGINA
st.set_page_config(page_title="Zion - Monitoramento Real-Time", layout="wide")

# Estilo para as tabelas e fundo
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    div[data-testid="stMetricValue"] { font-size: 25px; }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNÇÃO PARA CONECTAR AO GOOGLE SHEETS
def carregar_dados():
    # ID da sua planilha fornecido
    sheet_id = "1izHisQGFCLdqQ7d2OSGkAM7gDJrIsLxW9FY741lJ_Ao"
    
    # Escopos necessários
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    
    # Carrega as credenciais das 'Secrets' do Streamlit
    creds_info = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_info, scopes=scope)
    client = gspread.authorize(creds)
    
    # Abre a planilha
    sh = client.open_by_key(sheet_id)
    
    # Lendo as abas conforme o seu vídeo
    # Usamos try/except caso o nome da aba mude levemente
    try:
        df_rancho = pd.DataFrame(sh.worksheet("RANCHO").get_all_records())
        df_odm = pd.DataFrame(sh.worksheet("COM MARÇO").get_all_records())
    except:
        # Fallback caso os nomes das abas sejam diferentes
        st.error("Erro: Verifique se os nomes das abas são exatamente 'RANCHO' e 'COM MARÇO'.")
        return pd.DataFrame(), pd.DataFrame()
        
    return df_rancho, df_odm

# --- INTERFACE ---
st.title("🚢 Zion Tecnologia - Monitoramento Integrado")

try:
    df_r, df_o = carregar_dados()

    if not df_r.empty and not df_o.empty:
        # ABA 1: RANCHO (Conforme o vídeo 0:05)
        st.subheader("🥪 PROXIMOS RESSUPRIMENTOS (RANCHO)")
        # Selecionando colunas baseadas no vídeo
        colunas_r = ['EMPURRADOR', 'LIMITE PEDIDO', 'PRÓXIMO']
        # Filtramos apenas as colunas que existem no seu importrange
        cols_presentes = [c for c in colunas_r if c in df_r.columns]
        st.dataframe(df_r[cols_presentes], use_container_width=True)

        st.divider()

        # ABA 2: ODM (Conforme o vídeo 0:00)
        st.subheader("⛽ PROGRAMAÇÃO E REALIZADOS ODM")
        st.dataframe(df_o, use_container_width=True)

        st.divider()

        # ABA 3: DASHBOARDS (Gráficos de Linha)
        st.subheader("📊 CONSUMO E SALDO POR EMPURRADOR")
        empurrador = st.selectbox("Selecione o Empurrador para o Gráfico:", df_o['EMPURRADOR'].unique() if 'EMPURRADOR' in df_o.columns else ["Nenhum"])
        
        # Gráfico Exemplo de Linha (Pode ser adaptado para colunas de Litros/Valor)
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=[10, 20, 15, 25], name='Forecast', line=dict(color='blue', width=3)))
        fig.add_trace(go.Scatter(y=[8, 22, 18, 20], name='Realizado', line=dict(color='red', width=3)))
        st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.warning("⚠️ Sistema aguardando conexão com a Planilha.")
    st.info("Alex, o código está pronto! Agora você precisa criar a chave (JSON) no Google Cloud e colar nas Secrets do Streamlit.")
