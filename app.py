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
    df = pd.read_csv(url, dtype=str).fillna("")
    return df

def renderizar_rancho(df):
    try:
        # Mapeamento por índice baseado na sua planilha
        col_status = df.columns[1]   
        col_sc = df.columns[6]       
        col_emp = df.columns[10]     
        col_entrega = df.columns[17] # Coluna de data
        col_local = df.columns[19]   

        # 1. Filtro inicial por Status "PROGRAMADO"
        df_prog = df[df[col_status].astype(str).str.upper().str.contains('PROGR', na=False)].copy()

        # 2. CONVERSÃO E FILTRO DE DATA (O PONTO CRÍTICO)
        # Convertemos a coluna para data real. Hoje é 15/03/2026.
        df_prog['DT_OBJ'] = pd.to_datetime(df_prog[col_entrega], dayfirst=True, errors='coerce')
        hoje = pd.Timestamp(2026, 3, 15)

        # FILTRO: Somente datas MAIORES OU IGUAIS a hoje (remove o passado de 2024 e outros)
        df_prog = df_prog[df_prog['DT_OBJ'] >= hoje]

        # Ordenar para o que está mais perto aparecer primeiro
        df_prog = df_prog.sort_values(by='DT_OBJ', ascending=True)

        st.markdown("### 📅 RANCHOS PROGRAMADOS")
        
        if not df_prog.empty:
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
            st.info("Nenhuma entrega programada para datas futuras.")

        st.divider()
        st.markdown("### ✅ Rancho: Realizado")
        # No realizado, mostramos o que já passou
        df_real = df[df[col_status].astype(str).str.upper().str.contains('REALI', na=False)]
        if not df_real.empty:
            st.dataframe(df_real[[col_emp, col_sc, col_local, col_entrega]], use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Erro no processamento do Rancho: {e}")

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
        
        st.markdown("### ✅ Combustível: Realizado")
        real_odm = df_odm[df_odm['STATUS'].str.contains('REALI', na=False)]
        st.dataframe(real_odm[['EMPURRADOR', 'SC', 'LOCAL', 'DT ENTREGA']], use_container_width=True, hide_index=True)
    else:
        df_rancho = carregar_dados("RANCHO")
        renderizar_rancho(df_rancho)
except Exception as e:
    st.error(f"Erro Geral: {e}")
