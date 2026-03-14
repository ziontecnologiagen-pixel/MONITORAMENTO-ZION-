import streamlit as st
import pandas as pd
from urllib.parse import quote
from datetime import datetime

# 1. CONFIGURAÇÃO (Mantida)
st.set_page_config(page_title="Zion - Gestão Integrada", layout="centered")

st.markdown("""
    <style>
    .main .block-container { max-width: 850px; padding-top: 1rem; }
    [data-testid="stMetricValue"] {font-size: 1.2rem !important; font-weight: bold;}
    h3 {font-size: 1.1rem !important; margin-bottom: 0.2rem; font-weight: bold; color: #1f77b4;}
    .stDataFrame {font-size: 11px !important;}
    </style>
    """, unsafe_allow_html=True)

SHEET_ID = "1izHisQGFCLdqQ7d2OSGkAM7gDJrIsLxW9FY741lJ_Ao"

@st.cache_data(ttl=5) # Reduzi o cache para atualizar quase instantâneo
def carregar_dados(nome_aba):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(nome_aba)}"
    df = pd.read_csv(url)
    # Limpeza básica de nomes de colunas
    df.columns = [str(c).strip().upper() for c in df.columns]
    return df

def renderizar_rancho(df):
    # Ajuste manual dos nomes das colunas conforme sua planilha para evitar o erro de "11, 7, 20"
    # Se a planilha não tiver cabeçalho na linha 1, o pandas usa números. 
    # Vou usar a posição física para garantir:
    col_status = df.columns[1]   # Coluna B
    col_sc = df.columns[6]       # Coluna G
    col_emp = df.columns[10]     # Coluna K
    col_entrega = df.columns[17] # Coluna R
    col_local = df.columns[19]   # Coluna T

    # --- TRATAMENTO DE DATA CRÍTICO ---
    # Convertendo para datetime garantindo o formato dia/mês/ano
    df[col_entrega] = pd.to_datetime(df[col_entrega], errors='coerce', dayfirst=True)
    
    # IMPORTANTE: Definimos "hoje" como o início do dia para não excluir entregas de hoje
    hoje = pd.Timestamp(datetime.now().date())

    # --- FILTRAGEM ---
    # 1. Filtramos apenas quem tem STATUS contendo "PROGR"
    # 2. Filtramos apenas datas >= hoje OU datas que deram erro na conversão (para não sumir dado)
    df_prog = df[
        (df[col_status].astype(str).str.upper().str.contains('PROGR', na=False)) &
        ((df[col_entrega] >= hoje) | (df[col_entrega].isna()))
    ].copy()

    # Ordenação
    df_prog = df_prog.sort_values(by=col_entrega, ascending=True)

    # Formatação da data para o padrão brasileiro de exibição
    df_prog['DATA_FORMATADA'] = df_prog[col_entrega].dt.strftime('%d/%m/%y')
    # Se a data era inválida/vazia, mantém o que estava escrito originalmente na planilha
    df_prog.loc[df_prog[col_entrega].isna(), 'DATA_FORMATADA'] = df[col_entrega]

    st.markdown("### 📅 RANCHOS PROGRAMADOS")
    
    if not df_prog.empty:
        # Exibimos as colunas solicitadas (SC incluída)
        # Usamos a coluna formatada para a data
        df_exibir = df_prog[[col_emp, col_sc, col_local, 'DATA_FORMATADA']]
        
        st.dataframe(
            df_exibir,
            use_container_width=True, 
            hide_index=True,
            column_config={
                col_emp: "EMPURRADOR",
                col_sc: "SC",
                col_local: "LOCAL",
                "DATA_FORMATADA": "DATA ENTREGA"
            }
        )
    else:
        st.warning("Nenhum rancho programado encontrado com data futura.")
        # Debug para você ver o que o sistema está lendo (pode apagar depois)
        with st.expander("Clique para ver os dados brutos da planilha"):
            st.write(df[[col_status, col_entrega]].head())

    st.divider()
    st.markdown("### ✅ Rancho: Realizado")
    df_real = df[df[col_status].astype(str).str.upper().str.contains('REALI', na=False)]
    if not df_real.empty:
        st.dataframe(df_real[[col_emp, col_sc, col_local, col_entrega]], use_container_width=True, hide_index=True)

# --- EXECUÇÃO DO APP ---
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
    st.error(f"Erro na análise: {e}")
