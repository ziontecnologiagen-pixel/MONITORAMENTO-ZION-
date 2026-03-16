import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from urllib.parse import quote

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Zion - Dashboard Performance", layout="wide")

SHEET_ID = "1izHisQGFCLdqQ7d2OSGkAM7gDJrIsLxW9FY741lJ_Ao"

@st.cache_data(ttl=2)
def carregar_dados(aba):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(aba)}"
    return pd.read_csv(url, dtype=str).fillna("0")

def limpar_valor(valor):
    if not valor or valor == "0": return 0.0
    try:
        # Remove R$, pontos de milhar e troca vírgula por ponto
        s = str(valor).replace('R$', '').replace('.', '').replace(',', '.').replace(' ', '').strip()
        return float(s)
    except:
        return 0.0

# --- PROCESSAMENTO ---
df_raw = carregar_dados("ODM MARÇO")

if not df_raw.empty:
    # --- DADOS DOS CICLOS (LINHAS DA TABELA) ---
    ciclos = ["Ciclo 1", "Ciclo 2", "Ciclo 3", "Ciclo 4", "Ciclo 5"]
    cols = range(31, 36) # Colunas AF até AJ

    # Captura exata conforme sua última imagem
    v_real = [limpar_valor(df_raw.iloc[1, c]) for c in cols]      # Linha 'Realizado'
    v_fore = [limpar_valor(df_raw.iloc[2, c]) for c in cols]      # Linha 'Forecast'
    v_diff = [limpar_valor(df_raw.iloc[3, c]) for c in cols]      # Linha 'Diferença'

    st.markdown("<h2 style='text-align: center; color: black;'><b>PAINEL DE PERFORMANCE ZION</b></h2>", unsafe_allow_html=True)

    # --- GRÁFICO DE BARRAS DE CICLOS ---
    st.divider()
    st.markdown("<h3 style='text-align: center; color: black;'><b>ANÁLISE FINANCEIRA POR CICLO (R$)</b></h3>", unsafe_allow_html=True)

    fig = go.Figure()

    # Barra 1: Realizado
    fig.add_trace(go.Bar(
        x=ciclos, y=v_real, name='REALIZADO',
        marker_color='rgba(0, 102, 204, 0.9)', # Azul Escuro
        text=[f"<b>R$ {v:,.0f}</b>" for v in v_real], textposition='outside'
    ))

    # Barra 2: Forecast
    fig.add_trace(go.Bar(
        x=ciclos, y=v_fore, name='FORECAST',
        marker_color='rgba(135, 206, 235, 0.7)', # Azul Claro
        text=[f"<b>R$ {v:,.0f}</b>" for v in v_fore], textposition='outside'
    ))

    # Barra 3: Diferença com Cor Condicional
    cores_diff = ['red' if v < 0 else 'blue' for v in v_diff]
    fig.add_trace(go.Bar(
        x=ciclos, y=v_diff, name='DIFERENÇA',
        marker_color=cores_diff,
        text=[f"<b>R$ {v:,.0f}</b>" for v in v_diff], textposition='outside'
    ))

    # Ajustes de Layout para evitar o erro anterior
    fig.update_layout(
        template="plotly_white",
        barmode='group',
        height=600,
        font=dict(color="black", family="Arial Black"),
        margin=dict(t=50, b=100),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        yaxis=dict(title="Valores em R$", tickformat=",.0f")
    )

    st.plotly_chart(fig, use_container_width=True)

    # Exibe a tabela para conferência rápida
    df_resumo = pd.DataFrame({
        'Métrica': ['Realizado', 'Forecast', 'Diferença'],
        'Ciclo 1': [f"R$ {v_real[0]:,.2f}", f"R$ {v_fore[0]:,.2f}", f"R$ {v_diff[0]:,.2f}"],
        'Ciclo 2': [f"R$ {v_real[1]:,.2f}", f"R$ {v_fore[1]:,.2f}", f"R$ {v_diff[1]:,.2f}"],
        'Ciclo 3': [f"R$ {v_real[2]:,.2f}", f"R$ {v_fore[2]:,.2f}", f"R$ {v_diff[2]:,.2f}"],
        'Ciclo 4': [f"R$ {v_real[3]:,.2f}", f"R$ {v_fore[3]:,.2f}", f"R$ {v_diff[3]:,.2f}"],
        'Ciclo 5': [f"R$ {v_real[4]:,.2f}", f"R$ {v_fore[4]:,.2f}", f"R$ {v_diff[4]:,.2f}"]
    })
    st.table(df_resumo)
