import streamlit as st
import pandas as pd
from urllib.parse import quote
from datetime import datetime

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="Zion - Gestão Integrada", layout="centered")

st.markdown("""
    <style>
    .main .block-container { max-width: 850px; padding-top: 1rem; }
    h3 {font-size: 1.1rem !important; margin-bottom: 0.5rem; font-weight: bold; color: #1f77b4;}
    .stDataFrame {font-size: 12px !important;}
    </style>
    """, unsafe_allow_html=True)

SHEET_ID = "1izHisQGFCLdqQ7d2OSGkAM7gDJrIsLxW9FY741lJ_Ao"

@st.cache_data(ttl=2)
def carregar_dados(nome_aba):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(nome_aba)}"
    # Lemos tudo como string e limpamos valores nulos imediatamente
    df = pd.read_csv(url, dtype=str).fillna("")
    df.columns = [str(c).strip().upper() for c in df.columns]
    return df

def renderizar_rancho(df):
    # Mapeamento por posição (B=1, G=6, K=10, R=17, T=19)
    col_status = df.columns[2]   
    col_sc = df.columns[6]       
    col_emp = df.columns[10]     
    col_entrega = df.columns[14] 
    col_local = df.columns[19]   

    # Criar cópia para filtrar
    df_prog = df[df[col_status].str.contains('PROGR', na=False, case=False)].copy()

    # --- LÓGICA DE DATA CORRIGIDA ---
    # Converter para datetime (se o ano for 24, ele vai identificar como passado)
    df_prog['DATA_DT'] = pd.to_datetime(df_prog[col_entrega], dayfirst=True, errors='coerce')
    
    # Data de hoje: 14/03/2026
    hoje = pd.Timestamp(2026, 3, 14) 

    # FILTRO: Apenas datas de HOJE em diante
    df_prog = df_prog[df_prog['DATA_DT'] >= hoje]

    # Ordenar por data
    df_prog = df_prog.sort_values(by='DATA_DT', ascending=True)

    # Limpar "None" ou "nan" visualmente da coluna SC
    df_prog[col_sc] = df_prog[col_sc].apply(lambda x: "" if str(x).lower() in ["none", "nan", ""] else x)

    st.markdown("### 📅 RANCHOS PROGRAMADOS")
    
    if not df_prog.empty:
        # Selecionar e renomear para exibição
        dados_finais = df_prog[[col_emp, col_sc, col_local, col_entrega]]
        
        st.dataframe(
            dados_finais,
            use_container_width=True, 
            hide_index=True,
            column_config={
                col_emp: "EMPURRADOR",
                col_sc: "SC",
                col_local: "LOCAL",
                col_entrega: "DATA ENTREGA"
            }
        )
    else:
        st.info("Nenhum rancho programado para 14/03/2026 em diante.")

    st.divider()
    # Seção de Realizados (simplificada)
    st.markdown("### ✅ Rancho: Realizado")
    df_real = df[df[col_status].str.contains('REALI', na=False, case=False)]
    if not df_real.empty:
        st.dataframe(df_real[[col_emp, col_sc, col_local, col_entrega]], use_container_width=True, hide_index=True)

# --- EXECUÇÃO (MANTENDO ODM INTACTO) ---
st.title("🚢 Sistema de Gestão Zion")
aba = st.radio("Selecione:", ["Combustível (ODM)", "Rancho"], horizontal=True)

try:
    if aba == "Combustível (ODM)":
        df_odm = carregar_dados("ODM MARÇO")
        c_status = 'STATUS'
        c_emp = df_odm.columns[2]
        st.markdown("### ⛽ Combustível: Programado")
        st.dataframe(df_odm[df_odm[c_status].str.contains('PROGR', na=False)][[c_emp, 'SC', 'LOCAL', 'DT ENTREGA']], use_container_width=True, hide_index=True)
        st.markdown("### ✅ Combustível: Realizado")
        st.dataframe(df_odm[df_odm[c_status].str.contains('REALI', na=False)][[c_emp, 'SC', 'LOCAL', 'DT ENTREGA']], use_container_width=True, hide_index=True)
    else:
        df_rancho = carregar_dados("RANCHO")
        renderizar_rancho(df_rancho)
except Exception as e:
    st.error(f"Erro: {e}")
