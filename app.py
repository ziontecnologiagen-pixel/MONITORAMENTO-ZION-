import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from urllib.parse import quote

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Zion - Financeiro", layout="wide")

SHEET_ID = "1izHisQGFCLdqQ7d2OSGkAM7gDJrIsLxW9FY741lJ_Ao"

@st.cache_data(ttl=2)
def carregar_dados(aba):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(aba)}"
    return pd.read_csv(url, dtype=str).fillna("0")

def formatar_moeda(valor):
    if not valor or valor == "0": return 0.0
    try:
        # Conversão baseada na sua planilha
        s = str(valor).replace('R$', '').replace('.', '').replace(',', '.').strip()
        return float(s)
    except:
        return 0.0

# --- PROCESSAMENTO DOS DADOS ---
df_raw = carregar_dados("ODM MARÇO")

if not df_raw.empty:
    # Colunas: U(20)=Empurrador, V(21)=Previsto, X(23)=Real
    df_fin = pd.DataFrame()
    df_fin['EMPURRADOR'] = df_raw.iloc[:, 20]
    df_fin['PREVISTO'] = df_raw.iloc[:, 21].apply(formatar_moeda)
    df_fin['REAL'] = df_raw.iloc[:, 23].apply(formatar_moeda)
    df_fin['DIFERENCA'] = df_fin['REAL'] - df_fin['PREVISTO']
    
    df_fin = df_fin[df_fin['EMPURRADOR'] != "E/M"].reset_index(drop=True)

    # --- GRÁFICO ---
    fig = go.Figure()

    # Barra Previsto (Orçado)
    fig.add_trace(go.Bar(
        x=df_fin['EMPURRADOR'],
        y=df_fin['PREVISTO'],
        name='<b>ORÇADO</b>',
        marker=dict(color='rgba(135, 206, 235, 0.6)', line=dict(color='black', width=1.5)),
        text=df_fin['PREVISTO'].apply(lambda x: f'<b>R$ {x:,.0f}</b>'),
        textposition='outside',
        textfont=dict(color='black', size=12)
    ))

    # Barra Real (Realizado)
    fig.add_trace(go.Bar(
        x=df_fin['EMPURRADOR'],
        y=df_fin['REAL'],
        name='<b>REALIZADO</b>',
        marker=dict(color='rgba(0, 102, 204, 0.9)', line=dict(color='black', width=1.5)),
        text=df_fin['REAL'].apply(lambda x: f'<b>R$ {x:,.0f}</b>'),
        textposition='outside',
        textfont=dict(color='black', size=12)
    ))

    # Anotações de Saldo/Estouro (Apenas uma por empurrador para não encavalar)
    for i, row in df_fin.iterrows():
        if row['EMPURRADOR'] == "0": continue
        
        cor_label = "red" if row['DIFERENCA'] > 0 else "green"
        txt_label = "ESTOURO" if row['DIFERENCA'] > 0 else "SALDO"
        
        fig.add_annotation(
            x=row['EMPURRADOR'], y=0,
            text=f"<b>{txt_label}:</b><br><b>R$ {abs(row['DIFERENCA']):,.2f}</b>",
            showarrow=False, yshift=-70,
            font=dict(color=cor_label, size=13)
        )

    # AJUSTES DE TÍTULO E CORES PRETAS
    fig.update_layout(
        title={
            'text': "<b>REALIZADO VS ORÇADO</b>",
            'y': 0.95, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top',
            'font': {'size': 24, 'color': 'black', 'family': 'Arial Black'}
        },
        template="plotly_white",
        barmode='group',
        height=700,
        margin=dict(b=200, t=120),
        xaxis=dict(
            tickfont=dict(color='black', size=14, family="Arial Black"),
            title=""
        ),
        yaxis=dict(
            tickfont=dict(color='black', size=12),
            tickprefix="<b>R$ </b>",
            gridcolor='lightgrey'
        ),
        legend=dict(
            font=dict(color='black', size=14, family="Arial Black"),
            orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5
        )
    )

    st.plotly_chart(fig, use_container_width=True)

    # Tabela consolidada
    st.markdown("### **TABELA DE CONFERÊNCIA: REALIZADO VS ORÇADO**")
    st.dataframe(
        df_fin[['EMPURRADOR', 'PREVISTO', 'REAL', 'DIFERENCA']].style.format({
            'PREVISTO': 'R$ {:,.2f}',
            'REAL': 'R$ {:,.2f}',
            'DIFERENCA': 'R$ {:,.2f}'
        }).set_properties(**{'font-weight': 'bold', 'color': 'black'}),
        use_container_width=True, hide_index=True
    )
