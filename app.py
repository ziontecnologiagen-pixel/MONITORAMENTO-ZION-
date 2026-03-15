import streamlit as st
import pandas as pd
import plotly.express as px
from urllib.parse import quote

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Zion - Análise por Empurrador/Ciclo", layout="wide")

SHEET_ID = "1izHisQGFCLdqQ7d2OSGkAM7gDJrIsLxW9FY741lJ_Ao"

@st.cache_data(ttl=2)
def carregar_dados(aba):
    url = f"https://docs.google.com/sheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(aba)}"
    return pd.read_csv(url, dtype=str).fillna("0")

def formatar_valor(valor):
    if not valor or valor == "0": return 0.0
    try:
        s = str(valor).replace('R$', '').replace('.', '').replace(',', '.').strip()
        return float(s)
    except:
        return 0.0

# --- PROCESSAMENTO DOS DADOS ---
df_raw = carregar_dados("ODM MARÇO")

if not df_raw.empty:
    df_pizza = pd.DataFrame()
    df_pizza['EMPURRADOR'] = df_raw.iloc[:, 20].str.strip().str.upper() # Coluna U
    df_pizza['PREVISTO_RS'] = df_raw.iloc[:, 21].apply(formatar_valor) # Coluna V
    df_pizza['REAL_RS'] = df_raw.iloc[:, 23].apply(formatar_valor)     # Coluna X
    df_pizza['FORECAST_L'] = df_raw.iloc[:, 22].apply(formatar_valor)  # Coluna W
    df_pizza['REAL_L'] = df_raw.iloc[:, 25].apply(formatar_valor)      # Coluna Z
    
    # Filtro da frota ativa
    validos = ['CUMARU', 'AROEIRA', 'IPE', 'JACARANDA', 'ANGICO', 'CANJERANA', 'LUIZ FELIPE', 'BRENO']
    df_pizza = df_pizza[df_pizza['EMPURRADOR'].isin(validos)].reset_index(drop=True)

    # Remover empurradores com 0 em ambos (Real_L e Real_RS) para não aparecer no gráfico de pizza
    df_pizza_filtrado = df_pizza[(df_pizza['REAL_L'] > 0) | (df_pizza['REAL_RS'] > 0)].copy()

    st.markdown("<h2 style='text-align: center; color: black;'><b>ANÁLISE POR EMPURRADOR (CICLO)</b></h2>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        # --- GRÁFICO DE PIZZA: GASTO EM LITROS POR EMPURRADOR ---
        fig_litros = px.pie(
            df_pizza_filtrado,
            values='REAL_L',
            names='EMPURRADOR',
            title='<b>Consumo de ODM por Empurrador (Litros)</b>',
            hole=0.4, # Deixa o gráfico vazado
            color_discrete_sequence=px.colors.qualitative.Pastel,
            labels={'REAL_L': 'Litros'}
        )
        fig_litros.update_traces(textinfo='percent+label', marker=dict(line=dict(color='#000000', width=1)))
        fig_litros.update_layout(
            font=dict(color='black', size=14),
            title_font_color='black',
            legend_font_color='black',
            template="plotly_white"
        )
        st.plotly_chart(fig_litros, use_container_width=True)

    with col2:
        # --- GRÁFICO DE PIZZA: GASTO CONTÁBIL POR EMPURRADOR ---
        fig_contabil = px.pie(
            df_pizza_filtrado,
            values='REAL_RS',
            names='EMPURRADOR',
            title='<b>Gasto Contábil por Empurrador (R$)</b>',
            hole=0.4, # Deixa o gráfico vazado
            color_discrete_sequence=px.colors.qualitative.Pastel,
            labels={'REAL_RS': 'Valor (R$)'}
        )
        fig_contabil.update_traces(textinfo='percent+label', marker=dict(line=dict(color='#000000', width=1)))
        fig_contabil.update_layout(
            font=dict(color='black', size=14),
            title_font_color='black',
            legend_font_color='black',
            template="plotly_white"
        )
        st.plotly_chart(fig_contabil, use_container_width=True)

    st.divider()

    # --- ANÁLISE: QUEM NÃO ESTAVA PREVISTO, MAS CONSUMIU ---
    st.markdown("### 🚨 **ALERTAS: Consumo sem Previsão (Litros ou R$)**")
    
    # Condições para "não previsto mas consumiu"
    nao_previsto_consumo = df_pizza[
        ((df_pizza['PREVISTO_RS'] == 0) & (df_pizza['REAL_RS'] > 0)) |
        ((df_pizza['FORECAST_L'] == 0) & (df_pizza['REAL_L'] > 0))
    ]

    if not nao_previsto_consumo.empty:
        for idx, row in nao_previsto_consumo.iterrows():
            st.warning(f"**{row['EMPURRADOR']}**: Teve consumo real mas não estava previsto para gastar. (R$ Real: **R$ {row['REAL_RS']:,.2f}** | Litros Real: **{row['REAL_L']:,.0f} L**)")
    else:
        st.info("Todos os empurradores com consumo real tinham alguma previsão.")

    st.dataframe(df_pizza.style.set_properties(**{'font-weight': 'bold', 'color': 'black'}), use_container_width=True, hide_index=True)
