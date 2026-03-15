import streamlit as st
import pandas as pd
from urllib.parse import quote

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="Zion - Gestão Integrada", layout="wide")

SHEET_ID = "1izHisQGFCLdqQ7d2OSGkAM7gDJrIsLxW9FY741lJ_Ao"

@st.cache_data(ttl=2)
def carregar_dados(nome_aba):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(nome_aba)}"
    # Forçamos tudo como string na leitura para não perder zeros à esquerda
    df = pd.read_csv(url, dtype=str).fillna("")
    return df

def definir_semaforo(descricao):
    """Regra das bolinhas solicitada"""
    desc = str(descricao).upper()
    # 🔴 Vermelha: 1 Rancho e meio
    if "1 RANCHO E MEIO" in desc or "1 E MEIO RANCHO" in desc:
        return "🔴"
    # 🟡 Amarela: Meio rancho
    elif "MEIO RANCHO" in desc:
        return "🟡"
    # 🟢 Verde: 1 Rancho (pode ter 20, 30 águas, etc.)
    return "🟢"

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
        
        # --- TABELA 1: PROGRAMADOS (A que já funciona) ---
        df_prog = df[df.iloc[:, 1].astype(str).str.upper().str.contains('PROGR', na=False)].copy()
        df_prog['DT_FORMAT'] = pd.to_datetime(df_prog.iloc[:, 13], dayfirst=True, errors='coerce')
        df_futuro = df_prog[df_prog['DT_FORMAT'] >= hoje].sort_values(by='DT_FORMAT')

        st.markdown("### 📅 RANCHOS PROGRAMADOS")
        if not df_futuro.empty:
            t1 = df_futuro.iloc[:, [10, 6, 9, 13]].copy()
            t1.columns = ["EMPURRADOR", "SC", "LOCAL", "DATA ENTREGA"]
            st.dataframe(t1, use_container_width=True, hide_index=True)

        st.divider()

        # --- TABELA 2: REALIZADOS (Ajustada com Semáforo e SC Fixa) ---
        df_real = df[
            (df.iloc[:, 1].astype(str).str.upper() == 'REALIZADO') & 
            (df.iloc[:, 11].astype(str).str.contains('03', na=False))
        ].copy()

        st.markdown("### ✅ Rancho Entregues no Mês Corrente")
        if not df_real.empty:
            # Pegamos os dados brutos primeiro para não ter erro de índice
            indices = [10, 6, 9, 13, 15, 18, 0] # K, G, J, N, P, S, A
            t2 = df_real.iloc[:, indices].copy()
            t2.columns = ["EMPURRADOR", "SC", "SETOR/LOCAL", "ENTREGA", "PRÓXIMO", "DESCRIÇÃO", "PRÓXIMO PEDIDO"]
            
            # Criamos a coluna Semáforo baseada na descrição
            t2.insert(0, "SEMÁFORO", t2["DESCRIÇÃO"].apply(definir_semaforo))
            
            # FORÇANDO A COLUNA SC A SER TEXTO PURO (Para garantir que apareça)
            t2["SC"] = t2["SC"].astype(str)
            
            # Exibimos sem usar o comando .style (que era o que estava escondendo a SC)
            st.dataframe(
                t2,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Nenhum 'REALIZADO' em Março/2026.")

    except Exception as e:
        st.error(f"Erro: {e}")

# --- NAVEGAÇÃO ---
st.title("🚢 Sistema de Gestão Zion")
aba = st.radio("Selecione:", ["Combustível (ODM)", "Rancho"], horizontal=True)

if aba == "Rancho":
    exibir_rancho()
else:
    exibir_combustivel()
