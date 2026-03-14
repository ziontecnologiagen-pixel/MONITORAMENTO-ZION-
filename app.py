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

@st.cache_data(ttl=10)
def carregar_dados(nome_aba):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(nome_aba)}"
    df = pd.read_csv(url)
    df.columns = [str(c).strip().upper() for c in df.columns]
    return df

def renderizar_rancho(df):
    # Mapeamento rigoroso por posição
    col_status = df.columns[1]   # Coluna B (Status)
    col_sc = df.columns[6]       # Coluna G (SC)
    col_emp = df.columns[10]     # Coluna K (Empurrador)
    col_entrega = df.columns[17] # Coluna R (Entrega)
    col_local = df.columns[19]   # Coluna T (Local)

    # --- LÓGICA DE FILTRO "OLHANDO PARA FRENTE" ---
    # Converte a coluna de entrega para data (formato BR)
    df[col_entrega] = pd.to_datetime(df[col_entrega], errors='coerce', dayfirst=True)
    hoje = pd.Timestamp(datetime.now().date())

    # --- SEÇÃO PROGRAMADO ---
    st.markdown("### 📅 RANCHOS PROGRAMADOS")
    
    # Filtro: Contém "PROGRAMADO" E data é hoje ou futura
    df_prog = df[
        (df[col_status].astype(str).str.upper().str.contains('PROGRAMADO', na=False)) &
        (df[col_entrega] >= hoje)
    ].copy()
    
    # Ordena para mostrar o mais próximo primeiro
    df_prog = df_prog.sort_values(by=col_entrega)
    
    # Formata a data para exibição ficar limpa (dd/mm/yy)
    df_prog[col_entrega] = df_prog[col_entrega].dt.strftime('%d/%m/%y')

    if not df_prog.empty:
        st.dataframe(
            df_prog[[col_emp, col_sc, col_local, col_entrega]],
            use_container_width=True, hide_index=True,
            column_config={
                col_emp: st.column_config.TextColumn("EMPURRADOR", width=200),
                col_sc: st.column_config.TextColumn("SC", width=80),
                col_local: st.column_config.TextColumn("LOCAL", width=120),
                col_entrega: st.column_config.TextColumn("DATA ENTREGA", width=120)
            }
        )
    else:
        st.info("Nenhum rancho programado de hoje em diante.")

    st.divider()

    # --- SEÇÃO REALIZADO (Mantida conforme pedido anterior) ---
    st.markdown("### ✅ Rancho: Realizado")
    df_real = df[df[col_status].astype(str).str.upper().str.contains('REALIZADO', na=False)]
    
    if not df_real.empty:
        st.dataframe(
            df_real[[col_emp, col_sc, col_local, col_entrega]],
            use_container_width=True, hide_index=True
        )

# --- EXECUÇÃO DO APP ---
st.title("🚢 Sistema de Gestão Zion")
aba = st.radio("Selecione:", ["Combustível (ODM)", "Rancho"], horizontal=True)

try:
    if aba == "Combustível (ODM)":
        # MANTIDO EXATAMENTE COMO ESTAVA
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
