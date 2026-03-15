import streamlit as st
import pandas as pd
from urllib.parse import quote

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="Zion - Gestão Integrada", layout="wide")

SHEET_ID = "1izHisQGFCLdqQ7d2OSGkAM7gDJrIsLxW9FY741lJ_Ao"

@st.cache_data(ttl=2)
def carregar_dados(nome_aba):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(nome_aba)}"
    # Forçamos tudo como string para garantir que zeros à esquerda (como na SC 004385) apareçam
    df = pd.read_csv(url, dtype=str).fillna("")
    return df

def destacar_laranja(val):
    """Aplica cor laranja apenas se o texto for MEIO RANCHO"""
    if "MEIO RANCHO" in str(val).upper():
        return 'background-color: #FFA500; color: black; font-weight: bold'
    return ''

def exibir_combustivel():
    # RESTAURAÇÃO DO ODM ORIGINAL
    df_odm = carregar_dados("ODM MARÇO")
    if not df_odm.empty:
        st.markdown("### ⛽ Gestão de Combustível (ODM)")
        st.dataframe(df_odm, use_container_width=True, hide_index=True)

def exibir_rancho():
    df = carregar_dados("RANCHO")
    if df.empty: return

    try:
        hoje = pd.to_datetime("2026-03-15")
        
        # --- TABELA 1: PROGRAMADOS ---
        # Filtro: Coluna B (índice 1) contém "PROGR"
        df_prog = df[df.iloc[:, 1].astype(str).str.upper().str.contains('PROGR', na=False)].copy()
        df_prog['DT_FORMAT'] = pd.to_datetime(df_prog.iloc[:, 13], dayfirst=True, errors='coerce')
        df_futuro = df_prog[df_prog['DT_FORMAT'] >= hoje].sort_values(by='DT_FORMAT')

        st.markdown("### 📅 RANCHOS PROGRAMADOS")
        if not df_futuro.empty:
            # Seleção: Empurrador(10), SC(6), Local(9), Entrega(13)
            t1 = df_futuro.iloc[:, [10, 6, 9, 13]].copy()
            t1.columns = ["EMPURRADOR", "SC", "LOCAL", "DATA ENTREGA"]
            st.dataframe(t1, use_container_width=True, hide_index=True)

        st.divider()

        # --- TABELA 2: REALIZADOS (AQUI ESTAVA O ERRO DA SC) ---
        # Filtro: Status(1) == REALIZADO e Competência(11) == 03
        df_real = df[
            (df.iloc[:, 1].astype(str).str.upper() == 'REALIZADO') & 
            (df.iloc[:, 11].astype(str).str.contains('03', na=False))
        ].copy()

        st.markdown("### ✅ Rancho Entregues no Mês Corrente")
        if not df_real.empty:
            # Puxando exatamente os índices solicitados: K(10), G(6), J(9), N(13), P(15), S(18), A(0)
            t2 = df_real.iloc[:, [10, 6, 9, 13, 15, 18, 0]].copy()
            t2.columns = ["EMPURRADOR", "SC", "SETOR/LOCAL", "ENTREGA", "PRÓXIMO", "DESCRIÇÃO", "PRÓXIMO PEDIDO"]
            
            # APLICANDO ESTILO APENAS NA COLUNA DESCRIÇÃO (Para não apagar a SC)
            st.dataframe(
                t2.style.applymap(destacar_laranja, subset=['DESCRIÇÃO']),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Nenhum rancho 'REALIZADO' encontrado para Março/2026.")

    except Exception as e:
        st.error(f"Erro ao carregar Rancho: {e}")

# --- NAVEGAÇÃO ---
st.title("🚢 Sistema de Gestão Zion")
aba = st.radio("Selecione:", ["Combustível (ODM)", "Rancho"], horizontal=True)

if aba == "Rancho":
    exibir_rancho()
else:
    exibir_combustivel()
