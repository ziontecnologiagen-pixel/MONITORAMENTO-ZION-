import streamlit as st
import pandas as pd
from urllib.parse import quote
from datetime import datetime

# 1. CONFIGURAÇÃO DE TELA (Centralizado e Compacto)
st.set_page_config(page_title="Zion - Gestão Integrada", layout="centered")

st.markdown("""
    <style>
    .main .block-container { max-width: 850px; padding-top: 1rem; }
    [data-testid="stMetricValue"] {font-size: 1.1rem !important;}
    h3 {font-size: 1.1rem !important; margin-top: 1rem; margin-bottom: 0.2rem; font-weight: bold; color: #1f77b4;}
    [data-testid="stVerticalBlock"] {gap: 0.4rem !important;}
    .stDataFrame {font-size: 12px !important;}
    hr {margin: 1rem 0rem;}
    </style>
    """, unsafe_allow_html=True)

SHEET_ID = "1izHisQGFCLdqQ7d2OSGkAM7gDJrIsLxW9FY741lJ_Ao"
hoje = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

@st.cache_data(ttl=30)
def carregar_dados(nome_aba):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(nome_aba)}"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip().str.upper()
    if 'DATA SOLIC' in df.columns:
        df['DATA_DT'] = pd.to_datetime(df['DATA SOLIC'], dayfirst=True, errors='coerce')
    return df

def renderizar_secao(df, titulo_prefixo):
    # Processamento de valores
    df_op = df.iloc[0:100, 0:15].copy()
    col_emp = df_op.columns[2] # EMPURRADOR
    df_op['VALOR_NUM'] = pd.to_numeric(df_op['TOTAL'].astype(str).str.replace('R$', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).str.strip(), errors='coerce').fillna(0)
    df_op['LTS_NUM'] = pd.to_numeric(df_op['COMPRA LITROS'].astype(str).str.upper().str.replace('L', '', regex=False).str.replace('.', '', regex=False).str.strip(), errors='coerce').fillna(0) if 'COMPRA LITROS' in df_op.columns else pd.Series([0]*len(df_op))

    # --- PROGRAMADO (HOJE PARA FRENTE) ---
    st.markdown(f"### ⏳ {titulo_prefixo}: Programado (Futuro)")
    df_prog = df_op[(df_op['STATUS'].astype(str).str.upper().str.contains('PROGRAMADO', na=False)) & (df['DATA_DT'] >= hoje)]
    
    if not df_prog.empty:
        p1, p2 = st.columns(2)
        p1.metric("Volume/Qtd", f"{df_prog['LTS_NUM'].sum():,.0f}".replace(',', '.'))
        p2.metric("Valor Total", f"R${df_prog['VALOR_NUM'].sum():,.0f}".replace(',', '.'))
        st.dataframe(df_prog[[col_emp, 'SC', 'LOCAL', 'DT ENTREGA']], use_container_width=True, hide_index=True)
    else:
        st.info("Sem programações futuras.")

    # --- REALIZADO ---
    st.markdown(f"### ✅ {titulo_prefixo}: Realizado")
    df_real = df_op[df_op['STATUS'].astype(str).str.upper().str.contains('REALIZADO', na=False)]
    
    if not df_real.empty:
        r1, r2 = st.columns(2)
        r1.metric("Volume/Qtd", f"{df_real['LTS_NUM'].sum():,.0f}".replace(',', '.'))
        r2.metric("Valor Total", f"R${df_real['VALOR_NUM'].sum():,.0f}".replace(',', '.'))
        st.dataframe(df_real[[col_emp, 'SC', 'LOCAL', 'DT ENTREGA']], use_container_width=True, hide_index=True)

# --- INÍCIO DO APP ---
st.title("🚢 Sistema de Gestão Zion")

# Menu para alternar entre as abas
aba_selecionada = st.radio("Selecione a Categoria:", ["Combustível (ODM)", "Rancho"], horizontal=True)

try:
    if aba_selecionada == "Combustível (ODM)":
        df_odm = carregar_dados("ODM MARÇO")
        renderizar_secao(df_odm, "ODM")
    else:
        df_rancho = carregar_dados("RANCHO") # Certifique-se que o nome na planilha é exatamente RANCHO
        renderizar_secao(df_rancho, "RANCHO")

except Exception as e:
    st.error(f"Erro ao carregar aba {aba_selecionada}: {e}")
    st.info("Verifique se o nome da aba na planilha está correto.")
