import streamlit as st
import pandas as pd
import plotly.express as px
from urllib.parse import quote

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Zion - Dashboard Unificado", layout="wide")

SHEET_ID = "1izHisQGFCLdqQ7d2OSGkAM7gDJrIsLxW9FY741lJ_Ao"

@st.cache_data(ttl=2)
def carregar_dados(aba):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(aba)}"
    return pd.read_csv(url, dtype=str).fillna("")

def definir_semaforo(descricao):
    desc = str(descricao).upper()
    if "1 E MEIO" in desc or "1 RANCHO E MEIO" in desc:
        return "🔴"
    elif "MEIO RANCHO" in desc:
        return "🟡"
    return "🟢"

# --- PROCESSAMENTO PARA O GRÁFICO ---
df_rancho_raw = carregar_dados("RANCHO")
df_odm_raw = carregar_dados("ODM MARÇO")

# Criando contagem para o Gráfico de Raio X
resumo_grafico = []

if not df_rancho_raw.empty:
    # Conta quantos Ranchos cada empurrador tem (Realizados em Março)
    contagem_r = df_rancho_raw[df_rancho_raw.iloc[:, 11].str.contains("03", na=False)].iloc[:, 10].value_counts().reset_index()
    contagem_r.columns = ['EMPURRADOR', 'QTD']
    contagem_r['TIPO'] = 'Rancho'
    resumo_grafico.append(contagem_r)

if not df_odm_raw.empty:
    # Conta quantos abastecimentos no ODM
    contagem_o = df_odm_raw.iloc[:, 1].value_counts().reset_index()
    contagem_o.columns = ['EMPURRADOR', 'QTD']
    contagem_o['TIPO'] = 'ODM (Combustível)'
    resumo_grafico.append(contagem_o)

df_grafico = pd.concat(resumo_grafico) if resumo_grafico else pd.DataFrame()

# --- INTERFACE ---
st.title("📊 Dashboard Zion - Raio X Operacional")

# EXIBIÇÃO DO GRÁFICO (Estilo Tactium)
if not df_grafico.empty:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig = px.bar(df_grafico, x='EMPURRADOR', y='QTD', color='TIPO', 
                     title="Volume de Operações por Empurrador (Março/2026)",
                     barmode='group', text_auto=True)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Gráfico de Pizza com a divisão geral da frota
        fig_pizza = px.pie(df_grafico, values='QTD', names='TIPO', title="Divisão Rancho vs Combustível")
        st.plotly_chart(fig_pizza, use_container_width=True)

st.divider()

# --- TABELAS UNIFICADAS ABAIXO DOS GRÁFICOS ---

# 1. RANCHOS PROGRAMADOS
st.markdown("### 📅 RANCHOS PROGRAMADOS")
df_p = df_rancho_raw[df_rancho_raw.iloc[:, 1].astype(str).str.upper().str.contains('PROGR', na=False)].copy()
if not df_p.empty:
    t1 = df_p.iloc[:, [10, 6, 13, 18]].copy()
    t1.columns = ["EMPURRADOR", "SC", "DATA ENTREGA", "DESCRIÇÃO"]
    st.dataframe(t1, use_container_width=True, hide_index=True)

# 2. RANCHOS ENTREGUES (Com Semáforo e SC visível)
st.markdown("### ✅ Rancho Entregues no Mês Corrente")
df_real = df_rancho_raw[(df_rancho_raw.iloc[:, 1].str.upper() == 'REALIZADO') & (df_rancho_raw.iloc[:, 11].str.contains('03', na=False))].copy()
if not df_real.empty:
    t2 = df_real.iloc[:, [10, 6, 9, 13, 15, 18]].copy()
    t2.columns = ["EMPURRADOR", "SC", "SETOR/LOCAL", "ENTREGA", "PRÓXIMO", "DESCRIÇÃO"]
    t2.insert(0, "SEMÁFORO", t2["DESCRIÇÃO"].apply(definir_semaforo))
    st.dataframe(t2, use_container_width=True, hide_index=True)

# 3. ODM
st.markdown("### ⛽ Gestão de Combustível (ODM)")
if not df_odm_raw.empty:
    st.dataframe(df_odm_raw, use_container_width=True, hide_index=True)
