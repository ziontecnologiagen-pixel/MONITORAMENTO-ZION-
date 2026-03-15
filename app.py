import streamlit as st
import pandas as pd
from urllib.parse import quote

st.set_page_config(page_title="Zion - Raio X Real", layout="wide")

SHEET_ID = "1izHisQGFCLdqQ7d2OSGkAM7gDJrIsLxW9FY741lJ_Ao"

@st.cache_data(ttl=2)
def carregar(aba):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(aba)}"
    return pd.read_csv(url, dtype=str).fillna("")

def montar_raio_x():
    df_r = carregar("RANCHO")
    df_o = carregar("ODM MARÇO")
    
    # Criamos a base com todos os empurradores únicos das duas tabelas
    empurradores_r = df_r.iloc[:, 10].unique() # Coluna K
    empurradores_o = df_o.iloc[:, 1].unique()  # Coluna B
    todos_empurradores = sorted(list(set(empurradores_r) | set(empurradores_o)))
    
    resumo = []
    
    for emp in todos_empurradores:
        if not emp or emp == "nan" or emp == "EMPURRADOR": continue
        
        # BUSCA NO RANCHO (Tudo que está como PROGRAMADO)
        dados_r = df_r[(df_r.iloc[:, 10] == emp) & (df_r.iloc[:, 1].str.contains("PROGR", na=False))]
        txt_rancho = ""
        if not dados_r.empty:
            # Pega Data(13) e SC(6)
            txt_rancho = " | ".join([f"{r.iloc[13]} (SC {r.iloc[6]})" for _, r in dados_r.iterrows()])
            
        # BUSCA NO ODM (Pega o que estiver lançado para o futuro ou pendente)
        dados_o = df_o[df_o.iloc[:, 1] == emp]
        txt_odm = ""
        if not dados_o.empty:
            # Pega Data(0) e Documento(2)
            txt_odm = " | ".join([f"{o.iloc[0]} (Doc {o.iloc[2]})" for _, o in dados_o.iterrows()])
            
        resumo.append({
            "EMPURRADOR": emp,
            "PENDÊNCIAS RANCHO": txt_rancho,
            "PENDÊNCIAS ODM": txt_odm
        })
        
    return pd.DataFrame(resumo)

st.title("🚢 Raio X Unificado - Zion")
df_final = montar_raio_x()

if not df_final.empty:
    st.dataframe(df_final, use_container_width=True, hide_index=True)
else:
    st.warning("Nenhum dado encontrado para processar.")
