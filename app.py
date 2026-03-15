import streamlit as st
import pandas as pd
from urllib.parse import quote

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="Zion - Gestão Integrada", layout="centered")

SHEET_ID = "1izHisQGFCLdqQ7d2OSGkAM7gDJrIsLxW9FY741lJ_Ao"

@st.cache_data(ttl=2)
def carregar_dados(nome_aba):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(nome_aba)}"
    df = pd.read_csv(url, dtype=str).fillna("")
    return df

def renderizar_rancho(df):
    try:
        # MAPEAMENTO EXATO PELO VÍDEO
        # Coluna B (2) = STATUS (Índice 1)
        # Coluna K (11) = EMPURRADOR (Índice 10)
        # Coluna N (14) = DATA ENTREGA (Índice 13)
        # Coluna S (19) = DESCRIÇÃO (Índice 18)
        # Coluna T (20) = LOCAL (Índice 19)
        
        col_status = df.columns[1]   
        col_emp = df.columns[10]     
        col_entrega = df.columns[13] 
        col_desc = df.columns[18] # COLUNA 19 (S) PEDIDA
        col_local = df.columns[19]   

        # 1. Filtro: PROGRAMADO
        df_prog = df[df[col_status].astype(str).str.upper().str.contains('PROGR', na=False)].copy()

        # 2. Filtro de Data: Hoje (15/03/2026) em diante
        df_prog['DT_OBJ'] = pd.to_datetime(df_prog[col_entrega], dayfirst=True, errors='coerce')
        hoje = pd.Timestamp(2026, 3, 15)
        
        # Filtramos para garantir que 21/03 e 23/03 apareçam
        df_final = df_prog[df_prog['DT_OBJ'] >= hoje].copy()
        df_final = df_final.sort_values(by='DT_OBJ', ascending=True)

        st.markdown("### 📅 RANCHOS PROGRAMADOS")
        
        if not df_final.empty:
            st.dataframe(
                df_final[[col_emp, col_entrega, col_desc, col_local]],
                use_container_width=True, 
                hide_index=True,
                column_config={
                    col_emp: "EMPURRADOR",
                    col_entrega: "DATA ENTREGA",
                    col_desc: "DESCRIÇÃO / OBS",
                    col_local: "LOCAL"
                }
            )
        else:
            st.info("Nenhum rancho programado para datas futuras.")

    except Exception as e:
        st.error(f"Erro ao processar: {e}")

# --- INTERFACE ---
st.title("🚢 Sistema de Gestão Zion")
aba = st.radio("Selecione:", ["Combustível (ODM)", "Rancho"], horizontal=True)

if aba == "Rancho":
    df_rancho = carregar_dados("RANCHO")
    renderizar_rancho(df_rancho)
else:
    # Mantendo lógica original do Combustível
    df_odm = carregar_dados("ODM MARÇO")
    df_odm.columns = [str(c).strip().upper() for c in df_odm.columns]
    st.markdown("### ⛽ Combustível: Programado")
    prog_odm = df_odm[df_odm['STATUS'].str.contains('PROGR', na=False)]
    st.dataframe(prog_odm[['EMPURRADOR', 'SC', 'LOCAL', 'DT ENTREGA']], use_container_width=True, hide_index=True)
