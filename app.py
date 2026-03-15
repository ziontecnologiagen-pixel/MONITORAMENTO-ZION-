import streamlit as st
import pandas as pd
from urllib.parse import quote

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Zion - Gestão Unificada", layout="wide")

SHEET_ID = "1izHisQGFCLdqQ7d2OSGkAM7gDJrIsLxW9FY741lJ_Ao"

@st.cache_data(ttl=2)
def carregar_dados(aba):
    """Carrega os dados como string para não sumir com os zeros da SC"""
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(aba)}"
    return pd.read_csv(url, dtype=str).fillna("")

def definir_semaforo(descricao):
    """Lógica visual conforme as imagens"""
    desc = str(descricao).upper()
    if "1 E MEIO" in desc or "1 RANCHO E MEIO" in desc:
        return "🔴"
    elif "MEIO RANCHO" in desc:
        return "🟡"
    return "🟢"

# --- INTERFACE PRINCIPAL ---
st.title("🚢 Sistema de Gestão Unificado Zion")

# 1. BLOCO DE RANCHOS PROGRAMADOS
st.markdown("### 📅 RANCHOS PROGRAMADOS")
df_rancho = carregar_dados("RANCHO")

if not df_rancho.empty:
    # Filtro: Status (Índice 1) contém PROGRAMADO
    df_prog = df_rancho[df_rancho.iloc[:, 1].astype(str).str.upper().str.contains('PROGR', na=False)].copy()
    
    # Colunas conforme imagem: Empurrador(10), SC(6), Data Entrega(13), Descrição(18)
    t1 = df_prog.iloc[:, [10, 6, 13, 18]].copy()
    t1.columns = ["EMPURRADOR", "SC", "DATA ENTREGA", "DESCRIÇÃO"]
    
    # Forçar SC a aparecer como texto
    t1["SC"] = t1["SC"].astype(str)
    
    st.dataframe(t1, use_container_width=True, hide_index=True)

st.divider()

# 2. BLOCO DE RANCHO ENTREGUES (REALIZADOS)
st.markdown("### ✅ Rancho Entregues no Mês Corrente")
# Filtro: Status(1) == REALIZADO e Competência(11) == 03
df_real = df_rancho[
    (df_rancho.iloc[:, 1].astype(str).str.upper() == 'REALIZADO') & 
    (df_rancho.iloc[:, 11].astype(str).str.contains('03', na=False))
].copy()

if not df_real.empty:
    # Colunas: K(10), G(6), J(9), N(13), P(15), S(18), A(0)
    t2 = df_real.iloc[:, [10, 6, 9, 13, 15, 18, 0]].copy()
    t2.columns = ["EMPURRADOR", "SC", "SETOR/LOCAL", "ENTREGA", "PRÓXIMO", "DESCRIÇÃO", "PRÓXIMO PEDIDO"]
    
    # Adiciona Semáforo conforme solicitado
    t2.insert(0, "SEMÁFORO", t2["DESCRIÇÃO"].apply(definir_semaforo))
    
    # GARANTIA: SC como texto puro
    t2["SC"] = t2["SC"].astype(str)
    
    st.dataframe(t2, use_container_width=True, hide_index=True)

st.divider()

# 3. BLOCO DE COMBUSTÍVEL (ODM)
st.markdown("### ⛽ Gestão de Combustível (ODM)")
df_odm = carregar_dados("ODM MARÇO")
if not df_odm.empty:
    # Mostra a tabela de ODM na mesma tela
    st.dataframe(df_odm, use_container_width=True, hide_index=True)
