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

@st.cache_data(ttl=5)
def carregar_dados(nome_aba):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(nome_aba)}"
    # Carrega tudo como STRING para evitar que o Pandas transforme datas em "None"
    df = pd.read_csv(url, dtype=str)
    df.columns = [str(c).strip().upper() for c in df.columns]
    return df

def renderizar_rancho(df):
    # Mapeamento por posição (índices fixos para não depender do nome da coluna)
    # Coluna B=1, G=6, K=10, R=17, T=19
    col_status = df.columns[1]   
    col_sc = df.columns[6]       
    col_emp = df.columns[10]     
    col_entrega = df.columns[17] 
    col_local = df.columns[19]   

    # Criar uma cópia para trabalhar
    df_prog = df.copy()

    # 1. Filtro de Status (Apenas PROGRAMADO)
    df_prog = df_prog[df_prog[col_status].str.contains('PROGR', na=False, case=False)]

    # 2. Lógica de Data "Olhando para frente"
    # Convertemos para data de forma segura. O que não for data vira NaT.
    datas_convertidas = pd.to_datetime(df_prog[col_entrega], dayfirst=True, errors='coerce')
    hoje = pd.Timestamp(datetime.now().date())

    # Mantemos apenas linhas onde a data é hoje/futura OU onde não foi possível converter (para não perder dados)
    df_prog = df_prog[(datas_convertidas >= hoje) | (datas_convertidas.isna())]

    # Ordenação opcional (apenas nas que têm data válida)
    df_prog['temp_sort'] = datas_convertidas
    df_prog = df_prog.sort_values(by='temp_sort', ascending=True).drop(columns=['temp_sort'])

    st.markdown("### 📅 RANCHOS PROGRAMADOS")
    
    if not df_prog.empty:
        # Selecionamos as colunas na ordem correta
        dados_finais = df_prog[[col_emp, col_sc, col_local, col_entrega]]
        
        # Exibição do DataFrame
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
        st.info("Nenhum rancho programado encontrado para datas futuras.")

    st.divider()
    st.markdown("### ✅ Rancho: Realizado")
    df_real = df[df[col_status].str.contains('REALI', na=False, case=False)]
    if not df_real.empty:
        st.dataframe(df_real[[col_emp, col_sc, col_local, col_entrega]], use_container_width=True, hide_index=True)

# --- EXECUÇÃO DO APP ---
st.title("🚢 Sistema de Gestão Zion")
aba = st.radio("Selecione:", ["Combustível (ODM)", "Rancho"], horizontal=True)

try:
    if aba == "Combustível (ODM)":
        # Lógica original de ODM preservada
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
    st.error(f"Erro no sistema: {e}")
