import streamlit as st
import pandas as pd
from urllib.parse import quote
from datetime import datetime

# 1. CONFIGURAÇÃO DE TELA
st.set_page_config(page_title="Zion - Gestão Integrada", layout="wide")

SHEET_ID = "1izHisQGFCLdqQ7d2OSGkAM7gDJrIsLxW9FY741lJ_Ao"

@st.cache_data(ttl=2)
def carregar_dados(nome_aba):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(nome_aba)}"
    return pd.read_csv(url, dtype=str).fillna("")

def renderizar_rancho(df):
    try:
        # MAPEAMENTO DE COLUNAS (Baseado no vídeo e solicitações)
        col_prox_ped = df.columns[0]   # A - PROXIMO PEDIDO
        col_status   = df.columns[1]   # B - STATUS
        col_sc       = df.columns[6]   # G - SC
        col_emp      = df.columns[10]  # K - EMPURRADOR
        col_comp     = df.columns[11]  # L - COMPETÊNCIA
        col_entrega  = df.columns[13]  # N - ENTREGA
        col_prox_ent = df.columns[15]  # P - PROXIMO
        col_desc     = df.columns[18]  # S - DESCRIÇÃO

        # DATA DE HOJE PARA FILTROS
        hoje = pd.Timestamp(2026, 3, 15)
        mes_atual = "03/2026" # Baseado na coluna L (Competência) do vídeo

        # --- TABELA 1: RANCHOS PROGRAMADOS (Lógica conservada) ---
        df_prog = df[df[col_status].astype(str).str.upper().str.contains('PROGR', na=False)].copy()
        df_prog['DT_OBJ'] = pd.to_datetime(df_prog[col_entrega], dayfirst=True, errors='coerce')
        
        # Filtro: Datas futuras (ex: 21/03 e 23/03)
        df_futuro = df_prog[df_prog['DT_OBJ'] >= hoje].sort_values(by='DT_OBJ')

        st.markdown("### 📅 RANCHOS PROGRAMADOS")
        if not df_futuro.empty:
            st.dataframe(
                df_futuro[[col_emp, col_sc, col_entrega, col_desc]],
                use_container_width=True, hide_index=True,
                column_config={col_emp: "EMPURRADOR", col_entrega: "DATA ENTREGA", col_desc: "DESCRIÇÃO"}
            )
        else:
            st.info("Nenhum rancho programado para datas futuras.")

        st.divider()

        # --- TABELA 2: RANCHO ENTREGUES NO MÊS CORRENTE ---
        # Filtro: Status REALIZADO + Mês Corrente na coluna L
        df_real = df[
            (df[col_status].astype(str).str.upper().str.contains('REALI', na=False)) & 
            (df[col_comp].astype(str).str.contains(mes_atual, na=False))
        ].copy()

        st.markdown(f"### ✅ Rancho Entregues no Mês Corrente ({mes_atual})")
        if not df_real.empty:
            # Colunas solicitadas: K, G, N, P, S, A
            st.dataframe(
                df_real[[col_emp, col_sc, col_entrega, col_prox_ent, col_desc, col_prox_ped]],
                use_container_width=True,
                hide_index=True,
                column_config={
                    col_emp: "EMPURRADOR",
                    col_sc: "SC",
                    col_entrega: "ENTREGA",
                    col_prox_ent: "PRÓXIMO",
                    col_desc: "DESCRIÇÃO",
                    col_prox_ped: "PRÓXIMO PEDIDO"
                }
            )
        else:
            st.info(f"Nenhuma entrega registrada para o período {mes_atual}.")

    except Exception as e:
        st.error(f"Erro no processamento das tabelas: {e}")

# --- EXECUÇÃO ---
st.title("🚢 Sistema de Gestão Zion")
aba = st.radio("Selecione:", ["Combustível (ODM)", "Rancho"], horizontal=True)

if aba == "Rancho":
    df_rancho = carregar_dados("RANCHO")
    renderizar_rancho(df_rancho)
else:
    df_odm = carregar_dados("ODM MARÇO")
    # Lógica de Combustível mantida...
    st.markdown("### ⛽ Combustível Programado")
    st.dataframe(df_odm[df_odm['STATUS'].str.contains('PROGR', na=False)], use_container_width=True)
