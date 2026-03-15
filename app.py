import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from urllib.parse import quote

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Zion - Dashboard Financeiro", layout="wide")

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
    # Mapeamento conforme sua planilha: 
    # U(20)=Empurrador, V(21)=Previsto, X(23)=Real
    df_fin = pd.DataFrame()
    df_fin['EMPURRADOR'] = df_raw.iloc[:, 20]
    df_fin['PREVISTO'] = df_raw.iloc[:, 21].apply(formatar_moeda)
    df_fin['REAL'] = df_raw.iloc[:, 23].apply(formatar_moeda)
    df_fin['ESTOURO'] = df_fin['REAL'] - df_fin['PREVISTO']
    
    df_fin = df_fin[df_fin['EMPURRADOR'] != "E/M"].reset_index(drop=True)

    # --- GRÁFICO ---
    fig = go.Figure()

    # Barra Orçado
    fig.add_trace(go.Bar(
        x=df_fin['EMPURRADOR'],
        y=df_fin['PREVISTO'],
        name='PREVISTO',
        marker=dict(color='rgba(135, 206, 235, 0.5)', line=dict(color='black', width=1)),
        text=df_fin['PREVISTO'].apply(lambda x: f'<b>R$ {x:,.0f}</b>'),
        textposition='outside'
    ))

    # Barra Real
    fig.add_trace(go.Bar(
        x=df_fin['EMPURRADOR'],
        y=df_fin['REAL'],
        name='REAL',
        marker=dict(color='rgba(0, 102, 204, 0.8)', line=dict(color='black', width=1)),
        text=df_fin['REAL'].apply(lambda x: f'<b>R$ {x:,.0f}</b>'),
        textposition='outside'
    ))

    # Anotações de Estouro/Saldo abaixo do eixo X
    for i, row in df_fin.iterrows():
        cor = "red" if row['ESTOURO'] > 0 else "green"
        txt = "ESTOURO" if row['ESTOURO'] > 0 else "SALDO"
        fig.add_annotation(
            x=row['EMPURRADOR'], y=0,
            text=f"<b>{txt}:</b><br><b>R$ {abs(row['ESTOURO']):,.2f}</b>",
            showarrow=False, yshift=-50,
            font=dict(color=cor, size=12)
        )

    # Ajuste de Layout para Letras Pretas e Negrito
    fig.update_layout(
        template="plotly_white", # Fundo branco para as letras pretas aparecerem bem
        barmode='group',
        height=650,
        margin=dict(b=150),
        xaxis=dict(tickfont=dict(color='black', size=14, family="Arial Black")), # Nomes em preto/negrito
        yaxis=dict(tickfont=dict(color='black', size=12), tickprefix="<b>R$ </b>"),
        legend=dict(font=dict(color='black', size=12)),
        font=dict(color="black") # Cor da fonte global como PRETA
    )

    st.plotly_chart(fig, use_container_width=True)

    # Tabela com Negrito e Letras Pretas
    st.markdown("### **Detalhamento Financeiro (Letras Pretas/Negrito)**")
    st.dataframe(
        df_fin.style.format({
            'PREVISTO': 'R$ {:,.2f}', 
            'REAL': 'R$ {:,.2f}', 
            'ESTOURO': 'R$ {:,.2f}'
        }).set_properties(**{'font-weight': 'bold', 'color': 'black'}),
        use_container_width=True, hide_index=True
    )
