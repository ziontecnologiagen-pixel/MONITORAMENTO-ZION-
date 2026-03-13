import streamlit as st
import pandas as pd
from urllib.parse import quote
from datetime import datetime

# 1. CONFIGURAÇÃO DE TELA (Centralizado e Compacto)
st.set_page_config(page_title="Zion - Gestão", layout="centered")

st.markdown("""
    <style>
    .main .block-container { max-width: 850px; padding-top: 1rem; }
    [data-testid="stMetricValue"] {font-size: 1.1rem !important;}
    h3 {font-size: 1rem !important; margin-bottom: 0.1rem; font-weight: bold; color: #1f77b4;}
    .stDataFrame {font-size: 11px !important;}
    div[data-testid="stMetricLabel"] {font-size: 0.75rem !important;}
    </style>
    """, unsafe_allow_html=True)

SHEET_ID = "1izHisQGFCLdqQ7d2OSGkAM7gDJrIsLxW9FY741lJ_Ao"
hoje = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

@st.cache_data(ttl=30)
def carregar_dados(nome_aba):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(nome_aba)}"
    df = pd.read_csv(url)
    # Limpeza básica de nomes de colunas
    df.columns = [str(c).strip().upper() for c in df.columns]
    return df

def processar_aba(df, tipo):
    # Identificando colunas por posição conforme sua correção
    if tipo == "RANCHO":
        # Status é a Coluna B (Índice 1 no Python)
        col_status = df.columns[1]   
        # Empurrador é a Coluna K (Índice 10)
        col_emp = df.columns[10]     
        # SC é a Coluna G (Índice 6)
        col_sc = df.columns[6]       
        # Local é a Coluna T (Índice 19)
        col_local = df.columns[19]   
        # Entrega (Data formatada) é a Coluna R (Índice 17)
        col_entrega = df.columns[17] 
        # Data de Referência para o filtro 'Hoje' é a Coluna M (Índice 12)
        col_data_ref = df.columns[12] 
    else:
        # Padrão ODM MARÇO
        col_status = 'STATUS'
        col_sc = 'SC'
        col_emp = df.columns[2]
        col_data_ref = 'DATA SOLIC'
        col_entrega = 'DT ENTREGA'
        col_local = 'LOCAL'

    # Converte data para o filtro do robô (Hoje em diante)
    df['DT_AUX'] = pd.to_datetime(df[col_data_ref], dayfirst=True, errors='coerce')
    
    # --- 1. PROGRAMADO ---
    st.markdown(f"### ⏳ {tipo}: Programado (De Hoje em diante)")
    # Filtro: Status Programado e Data >= Hoje
    df_prog = df[(df[col_status].astype(str).str.upper().str.contains('PROGRAMADO', na=False)) & 
                (df['DT_AUX'] >= hoje)]
    
    if not df_prog.empty:
        st.dataframe(
            df_prog[[col_emp, col_sc, col_local, col_entrega]],
            use_container_width=True, hide_index=True,
            column_config={
                col_emp: st.column_config.TextColumn("Empurrador", width=200),
                col_sc: st.column_config.TextColumn("SC", width=100),
                col_local: st.column_config.TextColumn("Local", width=150),
                col_entrega: st.column_config.TextColumn("Entrega", width=120)
            }
        )
    else:
        st.info(f"Nenhum {tipo} programado encontrado de hoje em diante.")

    st.markdown("---")

    # --- 2. REALIZADO ---
    st.markdown(f"### ✅ {tipo}: Realizado")
    df_real = df[df[col_status].astype(str).str.upper().str.contains('REALIZADO', na=False)]
    
    if not df_real.empty:
        st.dataframe(
            df_real[[col_emp, col_sc, col_local, col_entrega]],
            use_container_width=True, hide_index=True,
            column_config={
                col_emp: st.column_config.TextColumn("Empurrador", width=200),
                col_sc: st.column_config.TextColumn("SC", width=100),
                col_local: st.column_config.TextColumn("Local", width=150),
                col_entrega: st.column_config.TextColumn("Entrega", width=120)
            }
        )

# --- EXECUÇÃO ---
st.title("🚢 Monitoramento Zion")
aba_escolhida = st.radio("Selecione a Categoria:", ["Combustível (ODM)", "Rancho"], horizontal=True)

try:
    if aba_escolhida == "Combustível (ODM)":
        df = carregar_dados("ODM MARÇO")
        processar_aba(df, "ODM")
    else:
        df = carregar_dados("RANCHO")
        processar_aba(df, "RANCHO")
except Exception as e:
    st.error(f"Erro ao processar aba {aba_escolhida}: {e}")
