import streamlit as st
import pandas as pd
from urllib.parse import quote

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Zion - Cronograma Unificado", layout="wide")

SHEET_ID = "1izHisQGFCLdqQ7d2OSGkAM7gDJrIsLxW9FY741lJ_Ao"

@st.cache_data(ttl=2)
def carregar_dados(nome_aba):
    """Carrega dados brutos para garantir que a SC (Índice 6) não suma"""
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(nome_aba)}"
    return pd.read_csv(url, dtype=str).fillna("")

def processar_cronograma_geral():
    df_rancho = carregar_dados("RANCHO")
    df_odm = carregar_dados("ODM MARÇO")
    
    lista_geral = []

    # --- VARREDURA RANCHO (BUSCA TUDO QUE É 'PROGRAMADO') ---
    if not df_rancho.empty:
        # Filtro: Coluna B (Índice 1) contém PROGRAMADO
        df_p = df_rancho[df_rancho.iloc[:, 1].astype(str).str.upper().str.contains('PROGR', na=False)].copy()
        
        for _, row in df_p.iterrows():
            lista_geral.append({
                "EMPURRADOR": row.iloc[10], # Coluna K
                "TIPO": "🍎 RANCHO",
                "SC / DOCUMENTO": row.iloc[6], # Coluna G
                "DATA PREVISTA": row.iloc[13], # Coluna N
                "STATUS": "PROGRAMADO"
            })

    # --- VARREDURA ODM (BUSCA TUDO QUE ESTÁ NA LISTA) ---
    if not df_odm.empty:
        # No ODM, pegamos as linhas preenchidas
        for _, row in df_odm.iterrows():
            if row.iloc[0] != "" and row.iloc[1] != "":
                lista_geral.append({
                    "EMPURRADOR": row.iloc[1],
                    "TIPO": "⛽ COMBUSTÍVEL (ODM)",
                    "SC / DOCUMENTO": row.iloc[2] if len(row) > 2 else "PENDENTE",
                    "DATA PREVISTA": row.iloc[0],
                    "STATUS": "AGENDADO"
                })

    return pd.DataFrame(lista_geral)

# --- INTERFACE ---
st.title("🚢 Cronograma Unificado Zion")
st.subheader("Visão Geral: Tudo que está Programado (Rancho + ODM)")

df_final = processar_cronograma_geral()

if not df_final.empty:
    # Exibe a tabela completa sem filtros de data para não esconder nada
    st.dataframe(
        df_final,
        use_container_width=True,
        hide_index=True
    )
else:
    st.error("Erro: Não foram encontrados dados com status 'PROGRAMADO' nas planilhas.")

st.divider()
st.info("💡 Esta tela agora ignora travas de data e mostra tudo que o robô encontrou como 'Programado'.")
