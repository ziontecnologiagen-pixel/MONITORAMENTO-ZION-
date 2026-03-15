import streamlit as st
import pandas as pd
from urllib.parse import quote

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="Zion - Gestão Integrada", layout="wide")

SHEET_ID = "1izHisQGFCLdqQ7d2OSGkAM7gDJrIsLxW9FY741lJ_Ao"

@st.cache_data(ttl=2)
def carregar_dados(nome_aba):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(nome_aba)}"
    # dtype=str evita que números longos de SC desapareçam ou virem float
    df = pd.read_csv(url, dtype=str).fillna("")
    return df

def destacar_meio_rancho(row, col_desc):
    """Aplica fundo laranja apenas se for MEIO RANCHO na descrição"""
    estilo = [''] * len(row)
    if "MEIO RANCHO" in str(row[col_desc]).upper():
        idx = row.index.get_loc(col_desc)
        estilo[idx] = 'background-color: #FFA500; color: black; font-weight: bold'
    return estilo

def renderizar_rancho(df):
    try:
        # MAPEAMENTO DE COLUNAS (Índices baseados na estrutura real da planilha)
        col_prox_ped = df.columns[0]   # A
        col_status   = df.columns[1]   # B
        col_sc       = df.columns[6]   # G
        col_j        = df.columns[9]   # J (Índice 9)
        col_emp      = df.columns[10]  # K
        col_comp     = df.columns[11]  # L
        col_entrega  = df.columns[13]  # N
        col_prox     = df.columns[15]  # P
        col_desc     = df.columns[18]  # S

        hoje = pd.to_datetime("2026-03-15")
        
        # --- TABELA 1: RANCHOS PROGRAMADOS (Sem destaque laranja) ---
        df_prog = df[df[col_status].astype(str).str.upper().str.contains('PROGR', na=False)].copy()
        df_prog['DT_OBJ'] = pd.to_datetime(df_prog[col_entrega], dayfirst=True, errors='coerce')
        df_futuro = df_prog[df_prog['DT_OBJ'] >= hoje].sort_values(by='DT_OBJ')

        st.markdown("### 📅 RANCHOS PROGRAMADOS")
        if not df_futuro.empty:
            st.dataframe(
                df_futuro[[col_emp, col_sc, col_entrega, col_desc]], 
                use_container_width=True, hide_index=True
            )

        st.divider()

        # --- TABELA 2: RANCHO ENTREGUES NO MÊS CORRENTE (Com destaque laranja) ---
        # Filtro: REALIZADO e Competência "03" (conforme imagem image_1ba2be.png)
        df_real = df[
            (df[col_status].astype(str).str.upper() == 'REALIZADO') & 
            (df[col_comp].astype(str).str.contains('03', na=False))
        ].copy()

        st.markdown("### ✅ Rancho Entregues no Mês Corrente")
        
        if not df_real.empty:
            # Colunas solicitadas: K, G, J, N, P, S, A
            colunas_finais = [col_emp, col_sc, col_j, col_entrega, col_prox, col_desc, col_prox_ped]
            
            # Aplicando o estilo somente aqui
            st.dataframe(
                df_real[colunas_finais].style.apply(destilizar_meio_rancho, col_desc=col_desc, axis=1),
                use_container_width=True,
                hide_index=True,
                column_config={
                    col_emp: "EMPURRADOR",
                    col_sc: "SC",
                    col_j: "SETOR/LOCAL",
                    col_entrega: "ENTREGA",
                    col_prox: "PRÓXIMO",
                    col_desc: "DESCRIÇÃO",
                    col_prox_ped: "PRÓXIMO PEDIDO"
                }
            )
        else:
            st.warning("Nenhum rancho 'REALIZADO' encontrado para o período atual.")

    except Exception as e:
        st.error(f"Erro ao processar tabelas: {e}")

# --- EXECUÇÃO ---
st.title("🚢 Sistema de Gestão Zion")
aba = st.radio("Selecione:", ["Combustível (ODM)", "Rancho"], horizontal=True)

if aba == "Rancho":
    df_rancho = carregar_dados("RANCHO")
    renderizar_rancho(df_rancho)
