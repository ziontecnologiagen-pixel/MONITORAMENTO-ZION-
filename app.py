import streamlit as st
import pandas as pd
from urllib.parse import quote

# 1. CONFIGURAÇÃO DE TELA
st.set_page_config(page_title="Zion - Gestão Integrada", layout="wide")

SHEET_ID = "1izHisQGFCLdqQ7d2OSGkAM7gDJrIsLxW9FY741lJ_Ao"

@st.cache_data(ttl=2)
def carregar_dados(nome_aba):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(nome_aba)}"
    # Forçamos a leitura de todas as colunas como string para evitar perdas
    df = pd.read_csv(url, dtype=str).fillna("")
    return df

def renderizar_rancho(df):
    try:
        # MAPEAMENTO DE COLUNAS (Baseado fielmente no seu vídeo)
        col_prox_ped = df.columns[0]   # A - PROXIMO PEDIDO
        col_status   = df.columns[1]   # B - STATUS
        col_sc       = df.columns[6]   # G - SC
        col_emp      = df.columns[10]  # K - EMPURRADOR
        col_comp     = df.columns[11]  # L - COMPETÊNCIA
        col_entrega  = df.columns[13]  # N - ENTREGA
        col_prox     = df.columns[15]  # P - PROXIMO
        col_desc     = df.columns[18]  # S - DESCRIÇÃO

        # DATA DE REFERÊNCIA: 15/03/2026
        hoje = pd.to_datetime("2026-03-15")

        # --- TABELA 1: RANCHOS PROGRAMADOS ---
        # Mantendo a lógica: Status "PROGRAMADO" e data >= hoje
        df_prog = df[df[col_status].astype(str).str.upper().str.contains('PROGR', na=False)].copy()
        df_prog['DT_OBJ'] = pd.to_datetime(df_prog[col_entrega], dayfirst=True, errors='coerce')
        df_futuro = df_prog[df_prog['DT_OBJ'] >= hoje].sort_values(by='DT_OBJ')

        st.markdown("### 📅 RANCHOS PROGRAMADOS")
        if not df_futuro.empty:
            st.dataframe(
                df_futuro[[col_emp, col_sc, col_entrega, col_desc]],
                use_container_width=True, hide_index=True,
                column_config={col_emp: "EMPURRADOR", col_sc: "SC", col_entrega: "DATA ENTREGA", col_desc: "DESCRIÇÃO"}
            )
        else:
            st.info("Nenhum rancho programado de hoje em diante.")

        st.divider()

        # --- TABELA 2: RANCHO ENTREGUES NO MÊS CORRENTE ---
        # LÓGICA DE FILTRO MELHORADA: Procuramos o mês 3 e ano 2026 na coluna L (Competência)
        # Primeiro, filtramos por Status REALIZADO
        df_real = df[df[col_status].astype(str).str.upper().str.contains('REALI', na=False)].copy()
        
        # Agora filtramos a coluna L para garantir que pegue março de 2026
        df_mes = df_real[
            df_real[col_comp].astype(str).str.contains('03', na=False) & 
            df_mes[col_comp].astype(str).str.contains('2026', na=False)
        ].copy()

        st.markdown("### ✅ Rancho Entregues no Mês Corrente (03/2026)")
        
        # Colunas Solicitadas: K, G, N, P, S, A
        colunas_exibir = [col_emp, col_sc, col_entrega, col_prox, col_desc, col_prox_ped]
        
        if not df_mes.empty:
            st.dataframe(
                df_mes[colunas_exibir],
                use_container_width=True,
                hide_index=True,
                column_config={
                    col_emp: "EMPURRADOR",
                    col_sc: "SC",
                    col_entrega: "ENTREGA",
                    col_prox: "PRÓXIMO",
                    col_desc: "DESCRIÇÃO",
                    col_prox_ped: "PRÓXIMO PEDIDO"
                }
            )
        else:
            st.warning("Nenhuma entrega realizada encontrada na coluna L para o período 03/2026.")

    except Exception as e:
        st.error(f"Erro ao processar tabelas: {e}")

# --- EXECUÇÃO ---
st.title("🚢 Sistema de Gestão Zion")
aba = st.radio("Selecione:", ["Combustível (ODM)", "Rancho"], horizontal=True)

if aba == "Rancho":
    df_rancho = carregar_dados("RANCHO")
    renderizar_rancho(df_rancho)
else:
    # Lógica de Combustível mantida
    df_odm = carregar_dados("ODM MARÇO")
    st.markdown("### ⛽ Combustível Programado")
    st.dataframe(df_odm, use_container_width=True)
