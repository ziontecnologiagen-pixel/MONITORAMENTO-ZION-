import streamlit as st
import pandas as pd
from urllib.parse import quote

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="Zion - Gestão Integrada", layout="wide")

SHEET_ID = "1izHisQGFCLdqQ7d2OSGkAM7gDJrIsLxW9FY741lJ_Ao"

@st.cache_data(ttl=2)
def carregar_dados(nome_aba):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(nome_aba)}"
    # Forçamos todas as colunas como string para a SC não sumir
    df = pd.read_csv(url, dtype=str).fillna("")
    return df

def destacar_meio_rancho(row, col_desc):
    """Aplica o fundo laranja na célula da descrição"""
    estilo = [''] * len(row)
    if "MEIO RANCHO" in str(row[col_desc]).upper():
        try:
            idx = row.index.get_loc(col_desc)
            estilo[idx] = 'background-color: #FFA500; color: black; font-weight: bold'
        except: pass
    return estilo

def exibir_rancho():
    df = carregar_dados("RANCHO")
    if df.empty: return

    # MAPEAMENTO SEGURO PELOS ÍNDICES REAIS
    # A=0, B=1, G=6, J=9, K=10, L=11, N=13, P=15, S=18
    col_prox_ped = df.columns[0]   # A
    col_status   = df.columns[1]   # B
    col_sc       = df.columns[6]   # G (Onde estão 20864, 20866)
    col_local    = df.columns[9]   # J
    col_emp      = df.columns[10]  # K
    col_comp     = df.columns[11]  # L
    col_entrega  = df.columns[13]  # N
    col_prox_ent = df.columns[15]  # P
    col_desc     = df.columns[18]  # S

    hoje = pd.to_datetime("2026-03-15")

    # --- TABELA 1: PROGRAMADOS ---
    # Somente Status "PROGRAMADO" e Data >= Hoje
    df_prog = df[df[col_status].astype(str).str.upper().str.contains('PROGR', na=False)].copy()
    df_prog['DT_FORMAT'] = pd.to_datetime(df_prog[col_entrega], dayfirst=True, errors='coerce')
    df_futuro = df_prog[df_prog['DT_FORMAT'] >= hoje].sort_values(by='DT_FORMAT')

    st.markdown("### 📅 RANCHOS PROGRAMADOS")
    if not df_futuro.empty:
        # Colunas: Empurrador, SC, Local, Entrega
        st.dataframe(
            df_futuro[[col_emp, col_sc, col_local, col_entrega]], 
            use_container_width=True, hide_index=True,
            column_config={col_sc: "SC", col_local: "LOCAL", col_entrega: "DATA ENTREGA"}
        )

    st.divider()

    # --- TABELA 2: REALIZADOS (ENTREGUES) ---
    # Filtro: Status "REALIZADO" e Competência "03"
    df_real = df[
        (df[col_status].astype(str).str.upper() == 'REALIZADO') & 
        (df[col_comp].astype(str).str.contains('03', na=False))
    ].copy()

    st.markdown("### ✅ Rancho Entregues no Mês Corrente")
    if not df_real.empty:
        cols_entregues = [col_emp, col_sc, col_local, col_entrega, col_prox_ent, col_desc, col_prox_ped]
        
        # Criamos uma cópia limpa para evitar erro de exibição da SC
        df_final = df_real[cols_entregues].copy()
        df_final.columns = ["EMPURRADOR", "SC", "LOCAL", "ENTREGA", "PRÓXIMO", "DESCRIÇÃO", "PRÓXIMO PEDIDO"]
        
        # Aplicamos o estilo usando o novo nome da coluna
        st.dataframe(
            df_final.style.apply(destacar_meio_rancho, col_desc="DESCRIÇÃO", axis=1),
            use_container_width=True, hide_index=True
        )
    else:
        st.info("Nenhuma entrega 'REALIZADO' em Março/2026.")

def exibir_combustivel():
    # RESTAURAÇÃO TOTAL DO ODM
    df_odm = carregar_dados("ODM MARÇO")
    if not df_odm.empty:
        st.markdown("### ⛽ Gestão de Combustível (ODM)")
        # Exibe a tabela completa como estava antes das falhas
        st.dataframe(df_odm, use_container_width=True, hide_index=True)

# --- NAVEGAÇÃO ---
st.title("🚢 Sistema de Gestão Zion")
aba = st.radio("Selecione:", ["Combustível (ODM)", "Rancho"], horizontal=True)

if aba == "Rancho":
    exibir_rancho()
else:
    exibir_combustivel()
