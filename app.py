import streamlit as st
import pandas as pd
import plotly.express as px
from urllib.parse import quote

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Zion - Ciclo de Consumo", layout="wide")

# Substitua pela URL correta se necessário, garantindo que o Sheets esteja público
SHEET_ID = "1izHisQGFCLdqQ7d2OSGkAM7gDJrIsLxW9FY741lJ_Ao"

@st.cache_data(ttl=5)
def carregar_dados_seguro(aba):
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(aba)}"
        return pd.read_csv(url, dtype=str).fillna("0")
    except Exception as e:
        st.error(f"Erro ao conectar com a planilha: {e}")
        return pd.DataFrame()

def converter(valor):
    if not valor or valor == "0": return 0.0
    try:
        return float(str(valor).replace('R$', '').replace('.', '').replace(',', '.').strip())
    except:
        return 0.0

# --- PROCESSAMENTO DOS DADOS ---
df_raw = carregar_dados_seguro("ODM MARÇO")

if not df_raw.empty:
    # Mapeamento: U(20)=Empurrador, V(21)=PREVISTO, W(22)=FORECAST L, X(23)=REAL RS, Z(25)=REAL L
    df_analise = pd.DataFrame()
    df_analise['EMPURRADOR'] = df_raw.iloc[:, 20].str.strip().str.upper()
    df_analise['PREVISTO_RS'] = df_raw.iloc[:, 21].apply(converter)
    df_analise['FORECAST_L'] = df_raw.iloc[:, 22].apply(converter)
    df_analise['REAL_RS'] = df_raw.iloc[:, 23].apply(converter)
    df_analise['REAL_L'] = df_raw.iloc[:, 25].apply(converter)
    
    # Filtro da Frota Zion
    frota = ['CUMARU', 'AROEIRA', 'IPE', 'JACARANDA', 'ANGICO', 'CANJERANA', 'LUIZ FELIPE', 'BRENO']
    df_analise = df_analise[df_analise['EMPURRADOR'].isin(frota)].reset_index(drop=True)

    st.markdown("<h2 style='text-align: center; color: black;'><b>DISTRIBUIÇÃO POR CICLO (EMPURRADOR)</b></h2>", unsafe_allow_html=True)

    # --- GRÁFICOS DE PIZZA LADO A LADO ---
    col1, col2 = st.columns(2)

    with col1:
        # Pizza de Litros (Realizado Z)
        fig_l = px.pie(df_analise, values='REAL_L', names='EMPURRADOR', 
                       title='<b>CONSUMO TOTAL EM LITROS (Z)</b>',
                       color_discrete_sequence=px.colors.qualitative.Prism)
        fig_l.update_traces(textfont_size=14, textfont_color="black", textinfo='percent+label', marker=dict(line=dict(color='black', width=1)))
        fig_l.update_layout(font=dict(family="Arial Black", color="black"))
        st.plotly_chart(fig_l, use_container_width=True)

    with col2:
        # Pizza Contábil (Realizado X)
        fig_rs = px.pie(df_analise, values='REAL_RS', names='EMPURRADOR', 
                        title='<b>GASTO TOTAL CONTÁBIL (X)</b>',
                        color_discrete_sequence=px.colors.qualitative.Safe)
        fig_rs.update_traces(textfont_size=14, textfont_color="black", textinfo='percent+label', marker=dict(line=dict(color='black', width=1)))
        fig_rs.update_layout(font=dict(family="Arial Black", color="black"))
        st.plotly_chart(fig_rs, use_container_width=True)

    st.divider()

    # --- ANÁLISE DE CONSUMO NÃO PREVISTO ---
    st.markdown("### ⚠️ **CONSUMO NÃO PREVISTO (RECEBEU SEM PROGRAMAÇÃO)**")
    
    # Identifica quem tem Forecast/Previsto 0 mas Realizado > 0
    sem_previsao = df_analise[
        ((df_analise['PREVISTO_RS'] == 0) & (df_analise['REAL_RS'] > 0)) | 
        ((df_analise['FORECAST_L'] == 0) & (df_analise['REAL_L'] > 0))
    ]

    if not sem_previsao.empty:
        for _, row in sem_previsao.iterrows():
            st.error(f"**{row['EMPURRADOR']}**: Recebeu consumo **NÃO PREVISTO** (Real: R$ {row['REAL_RS']:,.2f} | {row['REAL_L']:,.0f} Litros)")
    else:
        st.success("**Nenhum empurrador recebeu consumo fora do previsto.**")

    # Exibe a tabela para conferência
    st.dataframe(df_analise.style.set_properties(**{'font-weight': 'bold', 'color': 'black'}), use_container_width=True, hide_index=True)
