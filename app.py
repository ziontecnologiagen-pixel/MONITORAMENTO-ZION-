import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from urllib.parse import quote

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Zion - Raio X de Linhas", layout="wide")

SHEET_ID = "1izHisQGFCLdqQ7d2OSGkAM7gDJrIsLxW9FY741lJ_Ao"

@st.cache_data(ttl=2)
def carregar_dados(aba):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(aba)}"
    return pd.read_csv(url, dtype=str).fillna("0")

def formatar_moeda(valor):
    if not valor or valor == "0": return 0.0
    try:
        # Limpeza para garantir conversão numérica
        s = str(valor).replace('R$', '').replace('.', '').replace(',', '.').strip()
        return float(s)
    except:
        return 0.0

# --- PROCESSAMENTO ---
df_raw = carregar_dados("ODM MARÇO")

if not df_raw.empty:
    # U=20 (Empurrador), V=21 (Previsto), X=23 (Contabil/Real)
    df_fin = pd.DataFrame()
    df_fin['EMPURRADOR'] = df_raw.iloc[:, 20]
    df_fin['PREVISTO'] = df_raw.iloc[:, 21].apply(formatar_moeda)
    df_fin['REAL'] = df_raw.iloc[:, 23].apply(formatar_moeda)
    
    # Remove cabeçalhos
    df_fin = df_fin[df_fin['EMPURRADOR'] != "E/M"].reset_index(drop=True)

    st.title("📈 Performance Blue Metal - Visão em Linhas")
    st.markdown("### Cruzamento: Previsto (V) vs Real (X)")

    # --- GRÁFICO DE LINHAS ELEGANTE ---
    fig = go.Figure()

    # Linha do Previsto (Azul Claro)
    fig.add_trace(go.Scatter(
        x=df_fin['EMPURRADOR'],
        y=df_fin['PREVISTO'],
        mode='lines+markers+text',
        name='Previsto (V)',
        line=dict(color='rgb(135, 206, 235)', width=3),
        marker=dict(size=10, symbol='circle'),
        text=df_fin['PREVISTO'].apply(lambda x: f'R$ {x/1000:.0f}k' if x != 0 else ""),
        textposition="top center",
        hoverinfo='x+y+name'
    ))

    # Linha do Real (Azul Cobalto)
    fig.add_trace(go.Scatter(
        x=df_fin['EMPURRADOR'],
        y=df_fin['REAL'],
        mode='lines+markers+text',
        name='Real (X)',
        line=dict(color='rgb(0, 102, 204)', width=4, dash='solid'),
        marker=dict(size=12, symbol='diamond'),
        text=df_fin['REAL'].apply(lambda x: f'R$ {x/1000:.1f}k' if x != 0 else ""),
        textposition="bottom center",
        hoverinfo='x+y+name'
    ))

    # Estilização do Dashboard
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=600,
        xaxis=dict(showgrid=False, title="Frota (Empurradores)"),
        yaxis=dict(
            showgrid=True, 
            gridcolor='rgba(255,255,255,0.1)', 
            tickprefix="R$ ",
            title="Valor Financeiro"
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        margin=dict(l=50, r=50, t=100, b=50)
    )

    st.plotly_chart(fig, use_container_width=True)

    # --- DETALHAMENTO ABAIXO ---
    st.divider()
    st.markdown("#### Tabela de Conferência (U, V, X)")
    st.dataframe(
        df_fin.style.format({'PREVISTO': 'R$ {:,.2f}', 'REAL': 'R$ {:,.2f}'}),
        use_container_width=True,
        hide_index=True
    )
