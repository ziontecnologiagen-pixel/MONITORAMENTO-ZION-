import streamlit as st
import pandas as pd
from urllib.parse import quote
from datetime import datetime

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="Zion - Gestão Integrada", layout="centered")

# Estilo para melhorar a visualização
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
    # Carrega como string para não perder informação
    df = pd.read_csv(url, dtype=str).fillna("")
    return df

def renderizar_rancho(df):
    try:
        # Mapeamento exato pelos índices da sua planilha (conforme image_1d5ca1.png)
        col_status = df.columns[1]   # B (STATUS)
        col_sc = df.columns[6]       # G (SC)
        col_emp = df.columns[10]     # K (EMPURRADOR)
        col_entrega = df.columns[17] # R (DATA ENTREGA - Índice 17/Coluna 18)
        col_local = df.columns[19]   # T (LOCAL)

        # 1. Filtramos apenas o que é PROGRAMADO
        df_prog = df[df[col_status].astype(str).str.upper().str.contains('PROGR', na=False)].copy()

        # 2. FILTRO DE DATAS FUTURAS (Ajustado para ler 21/03 e 23/03)
        # Convertemos para data real. Hoje é 15/03/2026.
        df_prog['DT_LIMPA'] = pd.to_datetime(df_prog[col_entrega], dayfirst=True, errors='coerce')
        hoje = pd.Timestamp(2026, 3, 15)

        # MANTEMOS: Tudo que for hoje ou futuro (21/03, 22/03, 23/03...)
        # Eliminamos o passado (como o erro de 2024)
        df_final = df_prog[df_prog['DT_LIMPA'] >= hoje].copy()
        
        # Ordenar por data próxima
        df_final = df_final.sort_values(by='DT_LIMPA', ascending=True)

        st.markdown("### 📅 RANCHOS PROGRAMADOS")
        
        if not df_final.empty:
            # Exibe EMPURRADOR, SC, LOCAL e DATA ENTREGA
            st.dataframe(
                df_final[[col_emp, col_sc, col_local, col_entrega]],
                use_container_width=True, 
                hide_index=True
            )
        else:
            st.info("Nenhum rancho programado para datas futuras (21/03, 23/03, etc).")

        st.divider()
        st.markdown("### ✅ Rancho: Realizado")
        df_real = df[df[col_status].astype(str).str.upper().str.contains('REALI', na=False)]
        if not df_real.empty:
            st.dataframe(df_real[[col_emp, col_sc, col_local, col_entrega]], use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Erro ao processar Rancho: {e}")

# --- EXECUÇÃO ---
st.title("🚢 Sistema de Gestão Zion")
aba = st.radio("Selecione:", ["Combustível (ODM)", "Rancho"], horizontal=True)

try:
    if aba == "Combustível (ODM)":
        df_odm = carregar_dados("ODM MARÇO")
        df_odm.columns = [str(c).strip().upper() for c in df_odm.columns]
        st.markdown("### ⛽ Combustível: Programado")
        prog_odm = df_odm[df_odm['STATUS'].str.contains('PROGR', na=False)]
        st.dataframe(prog_odm[['EMPURRADOR', 'SC', 'LOCAL', 'DT ENTREGA']], use_container_width=True, hide_index=True)
    else:
        df_rancho = carregar_dados("RANCHO")
        renderizar_rancho(df_rancho)
except Exception as e:
    st.error(f"Erro: {e}")
