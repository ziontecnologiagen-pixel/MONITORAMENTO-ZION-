import streamlit as st
import pandas as pd
from urllib.parse import quote
from datetime import datetime

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Zion - Cronograma Futuro", layout="wide")

SHEET_ID = "1izHisQGFCLdqQ7d2OSGkAM7gDJrIsLxW9FY741lJ_Ao"

@st.cache_data(ttl=2)
def carregar_dados(nome_aba):
    """Lê os dados brutos como string para preservar SCs e datas"""
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(nome_aba)}"
    return pd.read_csv(url, dtype=str).fillna("")

def processar_pendencias_unificadas():
    df_rancho = carregar_dados("RANCHO")
    df_odm = carregar_dados("ODM MARÇO")
    
    # Data de referência: 15/03/2026
    hoje = pd.to_datetime("2026-03-15", dayfirst=True)
    lista_pendente = []

    # --- VARREDURA RANCHO (PENDENTES) ---
    if not df_rancho.empty:
        # Colunas: Empurrador(10), SC(6), Entrega(13), Status(1)
        df_r = df_rancho.copy()
        df_r['DT_AUX'] = pd.to_datetime(df_r.iloc[:, 13], dayfirst=True, errors='coerce')
        
        # Filtra Status Programado OU qualquer entrega futura (>= hoje)
        pendentes_r = df_r[df_r['DT_AUX'] >= hoje].sort_values(by='DT_AUX')
        
        for _, row in pendentes_r.iterrows():
            lista_pendente.append({
                "EMPURRADOR": row.iloc[10],
                "TIPO": "🍎 RANCHO",
                "SC / DOCUMENTO": row.iloc[6], # Coluna G
                "DATA PREVISTA": row.iloc[13],
                "DESCRIÇÃO": row.iloc[18] if len(row) > 18 else "N/A"
            })

    # --- VARREDURA ODM (PENDENTES) ---
    if not df_odm.empty:
        # Assume-se que a Coluna 0 é Data e Coluna 1 é Empurrador no seu ODM
        df_o = df_odm.copy()
        df_o['DT_AUX'] = pd.to_datetime(df_o.iloc[:, 0], dayfirst=True, errors='coerce')
        
        pendentes_o = df_o[df_o['DT_AUX'] >= hoje].sort_values(by='DT_AUX')
        
        for _, row in pendentes_o.iterrows():
            lista_pendente.append({
                "EMPURRADOR": row.iloc[1],
                "TIPO": "⛽ COMBUSTÍVEL (ODM)",
                "SC / DOCUMENTO": row.iloc[2] if len(row) > 2 else "ODM-PEND", # Puxa SC se houver
                "DATA PREVISTA": row.iloc[0],
                "DESCRIÇÃO": "Abastecimento Programado"
            })

    return pd.DataFrame(lista_pendente)

# --- INTERFACE DIRETA ---
st.title("🚢 Cronograma Unificado Zion")
st.subheader("Pendências de Hoje (15/03) para o Futuro")

df_futuro = processar_pendencias_unificadas()

if not df_futuro.empty:
    # Exibe tudo em uma única tabela sem necessidade de filtros
    st.dataframe(
        df_futuro.sort_values(by="DATA PREVISTA"),
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("Não existem entregas de Rancho ou ODM programadas de hoje em diante.")

st.divider()
st.info("💡 Esta tela mostra tudo que está 'na agulha' para acontecer, unindo Rancho e Combustível.")
