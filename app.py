import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from urllib.parse import quote

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Zion - Dashboard de Estouro", layout="wide")

SHEET_ID = "1izHisQGFCLdqQ7d2OSGkAM7gDJrIsLxW9FY741lJ_Ao"

@st.cache_data(ttl=2)
def carregar_dados(aba):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(aba)}"
    return pd.read_csv(url, dtype=str).fillna("0")

def formatar_moeda(valor):
    if not valor or valor == "0": return 0.0
    try:
        s = str(valor).replace('R$', '').replace('.', '').replace(',', '.').strip()
        return float(s)
    except:
        return 0.0

# --- PROCESSAMENTO ---
df_raw = carregar_dados("ODM MARÇO")

if not df_raw.empty:
    # Mapeamento: U(20)=Empurrador, V(21)=Previsto, X(23)=Real
    df_fin = pd.DataFrame()
    df_fin['EMPURRADOR'] = df_raw.iloc[:, 20]
    df_fin['PREVISTO'] = df_raw.iloc[:, 21].apply(formatar_moeda)
    df_fin['REAL'] = df_raw.iloc[:, 23].apply(formatar_moeda)
    
    # Cálculo do Estouro: Real - Previsto
    df_fin['ESTOURO'] = df_fin['REAL'] - df_fin['PREVISTO']
    
    df_fin = df_fin[df_fin['EMPURRADOR'] != "E/M"].reset_index(drop=True)

    st.title("📊 Raio X Financeiro: Orçado vs Estouro")
    
    # --- GRÁFICO DE BARRAS COM ANÁLISE DE ESTOURO ---
    fig = go.Figure()

    # Barra do Orçado (V) - Azul Metalizado Vazado
    fig.add_trace(go.Bar(
        x=df_fin['EMPURRADOR'],
        y=df_fin['PREVISTO'],
        name='Orçado (Previsto)',
        marker=dict(color='rgba(0, 102, 204, 0.3)', line=dict(color='rgb(0, 102, 204)', width=2)),
        text=df_fin['PREVISTO'].apply(lambda x: f'R$ {x:,.0f}'),
        textposition='inside'
    ))

    # Barra do Gasto Real (X) - Azul Sólido
    fig.add_trace(go.Bar(
        x=df_fin['EMPURRADOR'],
        y=df_fin['REAL'],
        name='Gasto Real (Contábil)',
        marker=dict(color='rgba(0, 102, 204, 0.8)'),
        text=df_fin['REAL'].apply(lambda x: f'R$ {x:,.0f}'),
        textposition='outside'
    ))

    # Adicionando a "Anotação de Estouro" abaixo do eixo X
    for i, row in df_fin.iterrows():
        if row['ESTOURO'] > 0:
            fig.add_annotation(
                x=row['EMPURRADOR'],
                y=0,
                text=f"🔴 ESTOURO:<br>R$ {row['ESTOURO']:,.2f}",
                showarrow=False,
                yshift=-50, # Joga para baixo do eixo X
                font=dict(color="red", size=10),
                bgcolor="rgba(255,0,0,0.1)"
            )
        elif row['ESTOURO'] < 0:
             fig.add_annotation(
                x=row['EMPURRADOR'],
                y=0,
                text=f"🟢 SALDO:<br>R$ {abs(row['ESTOURO']):,.2f}",
                showarrow=False,
                yshift=-50,
                font=dict(color="#00FF00", size=10)
            )

    fig.update_layout(
        template="plotly_dark",
        barmode='group',
        height=700,
        margin=dict(b=150), # Espaço maior embaixo para os valores de estouro
        xaxis_title="Frota Zion",
        yaxis_title="Valores em R$",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
    )

    st.plotly_chart(fig, use_container_width=True)

    # --- TABELA DE APOIO ---
    st.divider()
    st.dataframe(
        df_fin.style.format({
            'PREVISTO': 'R$ {:,.2f}', 
            'REAL': 'R$ {:,.2f}', 
            'ESTOURO': 'R$ {:,.2f}'
        }),
        use_container_width=True, hide_index=True
    )
