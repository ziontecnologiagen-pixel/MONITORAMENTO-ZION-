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
    df = pd.read_csv(url, dtype=str).fillna("")
    return df

def renderizar_rancho(df):
    try:
        # ÍNDICES FIXOS DO RANCHO (Baseado na tua imagem: B=1, G=6, K=10, R=17, T=19)
        col_status = df.columns[1]   
        col_sc = df.columns[6]       
        col_emp = df.columns[10]     
        col_entrega = df.columns[17] 
        col_local = df.columns[19]   

        # Filtro: PROGRAMADO
        df_prog = df[df[col_status].astype(str).str.upper().str.contains('PROGR', na=False)].copy()

        # Lógica de Data: Hoje (14/03/2026) em diante
        df_prog['DT_LIMPEZA'] = pd.to_datetime(df_prog[col_entrega], dayfirst=True, errors='coerce')
        hoje = pd.Timestamp(2026, 3, 14)
        
        # Filtramos para mostrar apenas futuro, mas mantemos o que der erro de conversão para segurança
        df_prog = df_prog[(df_prog['DT_LIMPEZA'] >= hoje) | (df_prog['DT_LIMPEZA'].isna())]
        df_prog = df_prog.sort_values(by='DT_LIMPEZA', ascending=True)

        st.markdown("### 📅 RANCHOS PROGRAMADOS")
        if not df_prog.empty:
            st.dataframe(
                df_prog[[col_emp, col_sc, col_local, col_entrega]],
                use_container_width=True, hide_index=True,
                column_config={col_emp: "EMPURRADOR", col_sc: "SC", col_local: "LOCAL", col_entrega: "DATA ENTREGA"}
            )
        else:
            st.info("Nenhum rancho programado de hoje em diante.")

        st.divider()
        st.markdown("### ✅ Rancho: Realizado")
        df_real = df[df[col_status].astype(str).str.upper().str.contains('REALI', na=False)]
        if not df_real.empty:
            st.dataframe(df_real[[col_emp, col_sc, col_local, col_entrega]], use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Erro no Rancho: {e}")

# --- EXECUÇÃO DO APP ---
st.title("🚢 Sistema de Gestão Zion")
aba = st.radio("Selecione:", ["Combustível (ODM)", "Rancho"], horizontal=True)

try:
    if aba == "Combustível (ODM)":
        df_odm = carregar_dados("ODM MARÇO")
        # Voltando à lógica que funcionava no Combustível (procurando pelos nomes exatos)
        df_odm.columns = [str(c).strip().upper() for c in df_odm.columns]
        
        # Filtros para o ODM
        st.markdown("### ⛽ Combustível: Programado")
        prog_odm = df_odm[df_odm['STATUS'].str.contains('PROGR', na=False)]
        st.dataframe(prog_odm[['EMPURRADOR', 'SC', 'LOCAL', 'DT ENTREGA']], use_container_width=True, hide_index=True)
        
        st.markdown("### ✅ Combustível: Realizado")
        real_odm = df_odm[df_odm['STATUS'].str.contains('REALI', na=False)]
        st.dataframe(real_odm[['EMPURRADOR', 'SC', 'LOCAL', 'DT ENTREGA']], use_container_width=True, hide_index=True)

    else:
        df_rancho = carregar_dados("RANCHO")
        renderizar_rancho(df_rancho)

except Exception as e:
    st.error(f"Erro Geral: {e}")
    st.info("Verifica se as abas 'ODM MARÇO' e 'RANCHO' mantêm os mesmos nomes na planilha.")
