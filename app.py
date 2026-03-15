import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from urllib.parse import quote

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Zion - Dashboard de Consumo (Litros)", layout="wide")

SHEET_ID = "1izHisQGFCLdqQ7d2OSGkAM7gDJrIsLxW9FY741lJ_Ao"

@st.cache_data(ttl=2)
def carregar_dados(aba):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(aba)}"
    return pd.read_csv(url, dtype=str).fillna("0")

def converter_litros(valor):
    if not valor or valor == "0": return 0.0
    try:
        # Remove pontos de milhar e converte para float
        s = str(valor).replace('.', '').replace(',', '.').strip()
        return float(s)
    except:
        return 0.0

# --- PROCESSAMENTO DOS DADOS ---
df_raw = carregar_dados("ODM MARÇO")

if not df_raw.empty:
    # U(20)=Empurrador, W(22)=Forecast, Z(25)=ODM/Real
    df_litros = pd.DataFrame()
    df_litros['EMPURRADOR'] = df_raw.iloc[:, 20].str.strip().str.upper()
    df_litros['FORECAST'] = df_raw.iloc[:, 22].apply(converter_litros)
    df_litros['REAL_LITROS'] = df_raw.iloc[:, 25].apply(converter_litros)
    df_litros['DIFERENCA'] = df_litros['REAL_LITROS'] - df_litros['FORECAST']
    
    # Filtro da frota ativa
    lista_validos = ['CUMARU', 'AROEIRA', 'IPE', 'JACARANDA', 'ANGICO', 'CANJERANA', 'LUIZ FELIPE', 'BRENO']
    df_litros = df_litros[df_litros['EMPURRADOR'].isin(lista_validos)].reset_index(drop=True)

    # --- GRÁFICO DE CONSUMO (LITROS) ---
    fig = go.Figure()

    # Barra Forecast (W)
    fig.add_trace(go.Bar(
        x=df_litros['EMPURRADOR'],
        y=df_litros['FORECAST'],
        name='<b>ORÇADO (LITROS)</b>',
        marker=dict(color='rgba(135, 206, 235, 0.6)', line=dict(color='black', width=2)),
        text=df_litros['FORECAST'].apply(lambda x: f'<b>{x:,.0f} L</b>'),
        textposition='outside',
        textfont=dict(color='black')
    ))

    # Barra Real (Z)
    fig.add_trace(go.Bar(
        x=df_litros['EMPURRADOR'],
        y=df_litros['REAL_LITROS'],
        name='<b>REALIZADO (LITROS)</b>',
        marker=dict(color='rgba(0, 102, 204, 0.9)', line=dict(color='black', width=2)),
        text=df_litros['REAL_LITROS'].apply(lambda x: f'<b>{x:,.0f} L</b>'),
        textposition='outside',
        textfont=dict(color='black')
    ))

    # Anotações de Saldo/Estouro de Litragem
    for i, row in df_litros.iterrows():
        cor_label = "red" if row['DIFERENCA'] > 0 else "green"
        txt_label = "ESTOURO" if row['DIFERENCA'] > 0 else "SALDO"
        
        fig.add_annotation(
            x=row['EMPURRADOR'], y=0,
            text=f"<b>{txt_label}:</b><br><b>{abs(row['DIFERENCA']):,.0f} L</b>",
            showarrow=False, yshift=-75,
            font=dict(color=cor_label, size=12)
        )

    fig.update_layout(
        title={'text': "<b>REALIZADO VS ORÇADO (LITROS)</b>", 'y':0.95, 'x':0.5, 'xanchor':'center', 'font':{'size': 24, 'color':'black'}},
        template="plotly_white",
        barmode='group',
        height=700,
        margin=dict(b=200, t=120),
        xaxis=dict(tickfont=dict(color='black', size=13, family="Arial Black")),
        yaxis=dict(tickfont=dict(color='black'), title="<b>Volume (Litros)</b>", gridcolor='lightgrey'),
        legend=dict(font=dict(color='black', size=13, family="Arial Black"), orientation="h", y=1.02, x=0.5, xanchor="center")
    )

    st.plotly_chart(fig, use_container_width=True)

    # Tabela de Conferência
    st.markdown("### **DETALHAMENTO DE CONSUMO (LITROS)**")
    st.dataframe(
        df_litros.style.format({
            'FORECAST': '{:,.0f} L', 'REAL_LITROS': '{:,.0f} L', 'DIFERENCA': '{:,.0f} L'
        }).set_properties(**{'font-weight': 'bold', 'color': 'black'}),
        use_container_width=True, hide_index=True
    )
