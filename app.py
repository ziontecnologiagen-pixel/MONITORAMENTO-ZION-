import streamlit as st
import pandas as pd
from urllib.parse import quote

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Zion - Raio X", layout="wide")

SHEET_ID = "1izHisQGFCLdqQ7d2OSGkAM7gDJrIsLxW9FY741lJ_Ao"

@st.cache_data(ttl=2)
def carregar_dados(nome_aba):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(nome_aba)}"
    return pd.read_csv(url, dtype=str).fillna("")

def processar_raio_x():
    df_rancho = carregar_dados("RANCHO")
    df_odm = carregar_dados("ODM MARÇO")
    
    # Criamos um dicionário para organizar por empurrador sem misturar
    raio_x = {}

    # --- 1. VARREDURA RANCHO (Programados) ---
    if not df_rancho.empty:
        # Filtro: Status (Índice 1) contém "PROGR"
        df_p = df_rancho[df_rancho.iloc[:, 1].astype(str).str.upper().str.contains('PROGR', na=False)].copy()
        
        for _, row in df_p.iterrows():
            nome = str(row.iloc[10]).strip().upper() # Coluna K: Empurrador
            if nome and nome != "NAN":
                if nome not in raio_x:
                    raio_x[nome] = {"RANCHO": "", "ODM": ""}
                # Salva Data + SC (Índice 6)
                info = f"{row.iloc[13]} (SC: {row.iloc[6]})"
                raio_x[nome]["RANCHO"] = info

    # --- 2. VARREDURA ODM (Programados) ---
    if not df_odm.empty:
        for _, row in df_odm.iterrows():
            # ODM: Índice 0 é Data, Índice 1 é Empurrador, Índice 2 é SC
            nome_odm = str(row.iloc[1]).strip().upper()
            if nome_odm and nome_odm != "NAN":
                if nome_odm not in raio_x:
                    raio_x[nome_odm] = {"RANCHO": "", "ODM": ""}
                # Salva Data + Documento
                info_odm = f"{row.iloc[0]} (Doc: {row.iloc[2]})"
                raio_x[nome_odm]["ODM"] = info_odm

    # Converte para DataFrame para exibir
    dados_finais = []
    for emp, info in raio_x.items():
        dados_finais.append({
            "EMPURRADOR": emp,
            "PROGRAMAÇÃO RANCHO": info["RANCHO"],
            "PROGRAMAÇÃO ODM": info["ODM"]
        })
    
    return pd.DataFrame(dados_finais)

# --- INTERFACE ---
st.title("🚢 Raio X Zion - Programação Unificada")
st.subheader("Visão por Empurrador: Rancho vs ODM")

df_resultado = processar_raio_x()

if not df_resultado.empty:
    # Exibe a tabela com colunas separadas para não misturar
    st.dataframe(
        df_resultado.sort_values(by="EMPURRADOR"),
        use_container_width=True,
        hide_index=True
    )
else:
    st.warning("Nenhuma programação encontrada para os empurradores.")

st.divider()
st.info("✅ Agora cada operação tem sua própria coluna. Se estiver em branco, não há programação para aquele item.")
