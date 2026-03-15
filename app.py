import streamlit as st
import pandas as pd
from urllib.parse import quote
from datetime import datetime

# 1. CONFIGURAÇÃO (Mantida)
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
    # Carregamos sem converter nada para evitar o erro de "None"
    df = pd.read_csv(url, dtype=str).fillna("")
    return df

def renderizar_rancho(df):
    # MAPEAMENTO SEGURO POR ÍNDICE (Baseado na sua foto da planilha)
    # No Python: A=0, B=1, C=2, D=3, E=4, F=5, G=6, H=7, I=8, J=9, K=10, L=11...
    
    try:
        col_status = df.columns[1]   # Coluna B (Onde está escrito STATUS)
        col_sc = df.columns[6]       # Coluna G (Onde está escrito SC)
        col_emp = df.columns[10]     # Coluna K (Onde está escrito EMPURRADOR)
        col_entrega = df.columns[17] # Coluna R (Onde está escrito DATA ENTREGA)
        col_local = df.columns[19]   # Coluna T (Onde está escrito LOCAL)

        # 1. Filtro de Status: Procurar "PROGR" na Coluna B
        df_prog = df[df[col_status].astype(str).str.upper().str.contains('PROGR', na=False)].copy()

        # 2. Lógica de Data (14/03/2026 em diante)
        # Convertemos para data para poder filtrar
        df_prog['DT_LIMPEZA'] = pd.to_datetime(df_prog[col_entrega], dayfirst=True, errors='coerce')
        
        # Filtro: Hoje (14/03/26) ou datas futuras (ou se a data estiver vazia para não sumir)
        hoje = pd.Timestamp(2026, 3, 14)
        df_prog = df_prog[(df_prog['DT_LIMPEZA'] >= hoje) | (df_prog['DT_LIMPEZA'].isna())]

        # Ordenar pela data mais próxima
        df_prog = df_prog.sort_values(by='DT_LIMPEZA', ascending=True)

        st.markdown("### 📅 RANCHOS PROGRAMADOS")
        
        if not df_prog.empty:
            # Exibir apenas o que interessa
            st.dataframe(
                df_prog[[col_emp, col_sc, col_local, col_entrega]],
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
            st.info("Nenhum rancho programado encontrado para hoje ou datas futuras.")

        st.divider()
        st.markdown("### ✅ Rancho: Realizado")
        df_real = df[df[col_status].astype(str).str.upper().str.contains('REALI', na=False)]
        if not df_real.empty:
            st.dataframe(df_real[[col_emp, col_sc, col_local, col_entrega]], use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Erro ao mapear colunas: {e}")
        st.write("Colunas detectadas:", list(df.columns))

# --- EXECUÇÃO DO APP ---
st.title("🚢 Sistema de Gestão Zion")
aba = st.radio("Selecione:", ["Combustível (ODM)", "Rancho"], horizontal=True)

try:
    if aba == "Combustível (ODM)":
        df_odm = carregar_dados("ODM MARÇO")
        # Mantendo sua lógica original de ODM
        c_status = df_odm.columns[1] # STATUS
        c_emp = df_odm.columns[2]    # EMPURRADOR
        st.markdown("### ⛽ Combustível: Programado")
        st.dataframe(df_odm[df_odm[c_status].str.contains('PROGR', na=False)][[c_emp, 'SC', 'LOCAL', 'DT ENTREGA']], use_container_width=True, hide_index=True)
    else:
        df_rancho = carregar_dados("RANCHO")
        renderizar_rancho(df_rancho)
except Exception as e:
    st.error(f"Erro geral: {e}")
