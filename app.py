import streamlit as st
import pandas as pd
from urllib.parse import quote

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="Zion - Gestão Integrada", layout="wide")

SHEET_ID = "1izHisQGFCLdqQ7d2OSGkAM7gDJrIsLxW9FY741lJ_Ao"

@st.cache_data(ttl=2)
def carregar_dados(nome_aba):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(nome_aba)}"
    # Leitura rigorosa como string para não sumir com os dados da SC
    df = pd.read_csv(url, dtype=str).fillna("")
    return df

def definir_semaforo(descricao):
    """Define a bolinha colorida com base no texto da descrição"""
    desc_upper = str(descricao).upper()
    if "MEIO RANCHO" in desc_upper and "1 RANCHO" not in desc_upper:
        return "🟡"  # Amarela para Meio Rancho
    elif "1 RANCHO E MEIO" in desc_upper or "1 E MEIO RANCHO" in desc_upper:
        return "🔴"  # Vermelha para 1 Rancho e Meio
    return "🟢"      # Verde para os demais (1 Rancho comum)

def exibir_combustivel():
    # ODM MARÇO INTEGRAL E SEM ALTERAÇÕES
    df_odm = carregar_dados("ODM MARÇO")
    if not df_odm.empty:
        st.markdown("### ⛽ Gestão de Combustível (ODM)")
        st.dataframe(df_odm, use_container_width=True, hide_index=True)

def exibir_rancho():
    df = carregar_dados("RANCHO")
    if df.empty: return

    try:
        hoje = pd.to_datetime("2026-03-15")
        
        # --- TABELA 1: PROGRAMADOS (Sem cores, direto ao ponto) ---
        df_prog = df[df.iloc[:, 1].astype(str).str.upper().str.contains('PROGR', na=False)].copy()
        df_prog['DT_FILTRO'] = pd.to_datetime(df_prog.iloc[:, 13], dayfirst=True, errors='coerce')
        df_futuro = df_prog[df_prog['DT_FILTRO'] >= hoje].sort_values(by='DT_FILTRO')

        st.markdown("### 📅 RANCHOS PROGRAMADOS")
        if not df_futuro.empty:
            # Seleção: Empurrador(10), SC(6), Local(9), Entrega(13)
            t1 = df_futuro.iloc[:, [10, 6, 9, 13]].copy()
            t1.columns = ["EMPURRADOR", "SC", "LOCAL", "DATA ENTREGA"]
            st.dataframe(t1, use_container_width=True, hide_index=True)

        st.divider()

        # --- TABELA 2: REALIZADOS COM SEMÁFORO ---
        df_real = df[
            (df.iloc[:, 1].astype(str).str.upper() == 'REALIZADO') & 
            (df.iloc[:, 11].astype(str).str.contains('03', na=False))
        ].copy()

        st.markdown("### ✅ Rancho Entregues no Mês Corrente")
        if not df_real.empty:
            # Puxando: K(10), G(6), J(9), N(13), P(15), S(18), A(0)
            t2 = df_real.iloc[:, [10, 6, 9, 13, 15, 18, 0]].copy()
            t2.columns = ["EMPURRADOR", "SC", "SETOR/LOCAL", "ENTREGA", "PRÓXIMO", "DESCRIÇÃO", "PRÓXIMO PEDIDO"]
            
            # CRIAÇÃO DA COLUNA SEMÁFORO
            t2["SEMÁFORO"] = t2["DESCRIÇÃO"].apply(definir_semaforo)
            
            # Reorganizando para o Semáforo ser a primeira coluna
            cols = ["SEMÁFORO", "EMPURRADOR", "SC", "SETOR/LOCAL", "ENTREGA", "PRÓXIMO", "DESCRIÇÃO", "PRÓXIMO PEDIDO"]
            
            st.dataframe(
                t2[cols],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Nenhuma entrega realizada em Março/2026.")

    except Exception as e:
        st.error(f"Erro no processamento: {e}")

# --- INTERFACE ---
st.title("🚢 Sistema de Gestão Zion")
aba = st.radio("Selecione:", ["Combustível (ODM)", "Rancho"], horizontal=True)

if aba == "Rancho":
    exibir_rancho()
else:
    exibir_combustivel()
