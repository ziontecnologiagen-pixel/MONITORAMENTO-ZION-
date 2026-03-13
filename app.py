import streamlit as st
import pandas as pd
from urllib.parse import quote

# 1. CONFIGURAÇÃO (Centralizado e Compacto)
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

@st.cache_data(ttl=10) # TTL menor para atualizar rápido enquanto você mexe na planilha
def carregar_dados(nome_aba):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(nome_aba)}"
    df = pd.read_csv(url)
    df.columns = [str(c).strip().upper() for c in df.columns]
    return df

def renderizar_rancho(df):
    # Mapeamento rigoroso por posição conforme a imagem
    col_status = df.columns[1]   # Coluna B (Status)
    col_sc = df.columns[6]       # Coluna G (SC)
    col_emp = df.columns[10]     # Coluna K (Empurrador)
    col_entrega = df.columns[17] # Coluna R (Entrega)
    col_local = df.columns[19]   # Coluna T (Local)

    # --- SEÇÃO PROGRAMADO ---
    st.markdown("### ⏳ Rancho: Programado")
    df_prog = df[df[col_status].astype(str).str.upper().str.contains('PROGRAMADO', na=False)]
    
    if not df_prog.empty:
        st.metric("Total de Entregas Programadas", len(df_prog))
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
        st.info("Nenhum rancho programado encontrado.")

    st.divider()

    # --- SEÇÃO REALIZADO ---
    st.markdown("### ✅ Rancho: Realizado")
    df_real = df[df[col_status].astype(str).str.upper().str.contains('REALIZADO', na=False)]
    
    if not df_real.empty:
        st.metric("Total de Entregas Realizadas", len(df_real))
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

# --- EXECUÇÃO DO APP ---
st.title("🚢 Sistema de Gestão Zion")
aba = st.radio("Selecione:", ["Combustível (ODM)", "Rancho"], horizontal=True)

try:
    if aba == "Combustível (ODM)":
        df_odm = carregar_dados("ODM MARÇO")
        # Reaproveita a lógica anterior para ODM
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
