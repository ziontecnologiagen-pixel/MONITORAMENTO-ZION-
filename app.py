import streamlit as st
import pandas as pd
from urllib.parse import quote

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="Zion - Gestão Integrada", layout="wide")

SHEET_ID = "1izHisQGFCLdqQ7d2OSGkAM7gDJrIsLxW9FY741lJ_Ao"

@st.cache_data(ttl=2)
def carregar_dados(nome_aba):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(nome_aba)}"
    # dtype=str garante que números como 004385 não percam os zeros
    df = pd.read_csv(url, dtype=str).fillna("")
    return df

def definir_semaforo(descricao):
    desc = str(descricao).upper()
    # 🔴 1 RANCHO E MEIO
    if "1 E MEIO" in desc or "1 RANCHO E MEIO" in desc:
        return "🔴"
    # 🟡 MEIO RANCHO
    if "MEIO RANCHO" in desc:
        return "🟡"
    # 🟢 RANCHOS NORMAIS
    return "🟢"

def exibir_combustivel():
    st.markdown("### ⛽ Gestão de Combustível (ODM)")
    df_odm = carregar_dados("ODM MARÇO")
    if not df_odm.empty:
        st.dataframe(df_odm, use_container_width=True, hide_index=True)

def exibir_rancho():
    df = carregar_dados("RANCHO")
    if df.empty: return

    # --- TABELA 1: PROGRAMADOS ---
    st.markdown("### 📅 RANCHOS PROGRAMADOS")
    df_prog = df[df.iloc[:, 1].astype(str).str.upper().str.contains('PROGR', na=False)].copy()
    # K(10), G(6), J(9), N(13)
    t1 = df_prog.iloc[:, [10, 6, 9, 13]].copy()
    t1.columns = ["EMPURRADOR", "SC", "LOCAL", "DATA ENTREGA"]
    st.dataframe(t1, use_container_width=True, hide_index=True)

    st.divider()

    # --- TABELA 2: REALIZADOS ---
    st.markdown("### ✅ Rancho Entregues no Mês Corrente")
    # Filtro: Status(1) == REALIZADO e Competência(11) == 03
    df_real = df[
        (df.iloc[:, 1].astype(str).str.upper() == 'REALIZADO') & 
        (df.iloc[:, 11].astype(str).str.contains('03', na=False))
    ].copy()

    if not df_real.empty:
        # Colunas: K(10), G(6), J(9), N(13), P(15), S(18), A(0)
        t2 = df_real.iloc[:, [10, 6, 9, 13, 15, 18, 0]].copy()
        t2.columns = ["EMPURRADOR", "SC", "SETOR/LOCAL", "ENTREGA", "PRÓXIMO", "DESCRIÇÃO", "PRÓXIMO PEDIDO"]
        
        # Inserindo o semáforo na primeira posição
        t2.insert(0, "SEMÁFORO", t2["DESCRIÇÃO"].apply(definir_semaforo))
        
        # Garante que a SC seja tratada como texto para aparecer o número
        t2["SC"] = t2["SC"].astype(str)
        
        st.dataframe(t2, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhuma entrega encontrada para o período.")

# --- NAVEGAÇÃO ---
st.title("🚢 Sistema de Gestão Zion")
aba = st.radio("Selecione:", ["Combustível (ODM)", "Rancho"], horizontal=True)

if aba == "Rancho":
    exibir_rancho()
else:
    exibir_combustivel()
