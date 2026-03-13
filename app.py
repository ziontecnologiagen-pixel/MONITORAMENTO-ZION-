import streamlit as st
import pandas as pd
from urllib.parse import quote
from datetime import datetime

# 1. CONFIGURAÇÃO DE TELA (Centralizado e Compacto)
st.set_page_config(page_title="Zion - Dashboard", layout="centered")

st.markdown("""
    <style>
    .main .block-container { max-width: 850px; padding-top: 1rem; }
    [data-testid="stMetricValue"] {font-size: 1.1rem !important;}
    h3 {font-size: 1rem !important; margin-bottom: 0.2rem; font-weight: bold; color: #1f77b4;}
    .stDataFrame {font-size: 11px !important;}
    div[data-testid="stMetricLabel"] {font-size: 0.8rem !important;}
    </style>
    """, unsafe_allow_html=True)

SHEET_ID = "1izHisQGFCLdqQ7d2OSGkAM7gDJrIsLxW9FY741lJ_Ao"
hoje = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

@st.cache_data(ttl=30)
def carregar_dados(nome_aba):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(nome_aba)}"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip().str.upper()
    return df

def tratar_e_renderizar(df, tipo):
    # --- MAPEAMENTO DINÂMICO DE COLUNAS ---
    if tipo == "RANCHO":
        # Mapeamento baseado na imagem image_4d69c2.png
        col_emp = 'EMPURRADOR' if 'EMPURRADOR' in df.columns else df.columns[10] # Coluna K
        col_sc = 'SC' if 'SC' in df.columns else df.columns[6] # Coluna G
        col_local = 'LOCAL' if 'LOCAL' in df.columns else df.columns[19] # Coluna T
        col_entrega = 'DT ENTREGA' if 'DT ENTREGA' in df.columns else df.columns[17] # Coluna R
        col_data_solic = df.columns[12] # Coluna M (Data que usaremos para o filtro de hoje)
    else:
        # Mapeamento ODM MARÇO
        col_emp = df.columns[2]
        col_sc = 'SC'
        col_local = 'LOCAL'
        col_entrega = 'DT ENTREGA'
        col_data_solic = 'DATA SOLIC'

    # Converte data para o filtro do robô
    df['DATA_REF_DT'] = pd.to_datetime(df[col_data_solic], dayfirst=True, errors='coerce')
    
    # Identifica valor financeiro para o cabeçalho (sem travar se não achar 'TOTAL')
    col_valor = next((c for c in df.columns if 'TOTAL' in c or 'VALOR' in c or 'PREVISTO' in c), None)
    df['VLR_LIMPO'] = pd.to_numeric(df[col_valor].astype(str).str.replace('R$', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).str.strip(), errors='coerce').fillna(0) if col_valor else 0

    # --- 1. PROGRAMADOS (De hoje para frente) ---
    st.markdown(f"### ⏳ {tipo}: Programado (A realizar)")
    df_prog = df[(df['STATUS'].astype(str).str.upper().str.contains('PROGRAMADO', na=False)) & (df['DATA_REF_DT'] >= hoje)]
    
    if not df_prog.empty:
        st.metric("Subtotal Programado", f"R$ {df_prog['VLR_LIMPO'].sum():,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        st.dataframe(
            df_prog[[col_emp, col_sc, col_local, col_entrega]],
            use_container_width=True, hide_index=True,
            column_config={col_emp: "Empurrador", col_sc: "SC", col_local: "Local", col_entrega: "Entrega"}
        )
    else:
        st.info("Nada programado para datas futuras.")

    # --- 2. REALIZADOS (Histórico do período) ---
    st.markdown(f"### ✅ {tipo}: Realizado (Concluído)")
    df_real = df[df['STATUS'].astype(str).str.upper().str.contains('REALIZADO', na=False)]
    
    if not df_real.empty:
        st.metric("Subtotal Realizado", f"R$ {df_real['VLR_LIMPO'].sum():,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        st.dataframe(
            df_real[[col_emp, col_sc, col_local, col_entrega]],
            use_container_width=True, hide_index=True,
            column_config={col_emp: "Empurrador", col_sc: "SC", col_local: "Local", col_entrega: "Entrega"}
        )

# --- EXECUÇÃO ---
st.title("🚢 Sistema de Gestão Zion")
escolha = st.radio("Selecione:", ["Combustível (ODM)", "Rancho"], horizontal=True)

try:
    if escolha == "Combustível (ODM)":
        df_odm = carregar_dados("ODM MARÇO")
        tratar_e_renderizar(df_odm, "ODM")
    else:
        df_rancho = carregar_dados("RANCHO")
        tratar_e_renderizar(df_rancho, "RANCHO")
except Exception as e:
    st.error(f"Erro ao processar aba {escolha}: {e}")
