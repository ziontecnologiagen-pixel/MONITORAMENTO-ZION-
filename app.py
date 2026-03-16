import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from urllib.parse import quote

# Configuração da Página
st.set_page_config(page_title="Zion Dashboard", layout="wide")

SHEET_ID = "1izHisQGFCLdqQ7d2OSGkAM7gDJrIsLxW9FY741lJ_Ao"

@st.cache_data(ttl=2)
def carregar_dados(aba):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(aba)}"
    return pd.read_csv(url, dtype=str).fillna("0")

def limpar_valor(valor):
    if not valor or str(valor).strip() in ["0", "", "R$ 0,00"]: return 0.0
    try:
        # Remove R$, pontos de milhar e ajusta a vírgula decimal
        s = str(valor).replace('R$', '').replace('.', '').replace(',', '.').replace(' ', '').strip()
        # Trata valores negativos representados por parênteses ou sinal de menos
        if '(' in s or '-' in s:
            s = s.replace('(', '').replace(')', '').replace('-', '')
            return float(s) * -1
        return float(s)
    except:
        return 0.0

# Processamento dos Dados
df_raw = carregar_dados("ODM MARÇO")

if not df_raw.empty:
    st.markdown("<h2 style='text-align: center; font-family: Arial Black;'>PAINEL DE PERFORMANCE ZION</h2>", unsafe_allow_html=True)

    # --- BLOCO SUPERIOR: PERFORMANCE POR EMPURRADOR ---
    df_emp = pd.DataFrame()
    df_emp['EMPURRADOR'] = df_raw.iloc[:, 20].str.strip().str.upper()
    df_emp['PREV_RS'] = df_raw.iloc[:, 21].apply(limpar_valor)
    df_emp['REAL_RS'] = df_raw.iloc[:, 23].apply(limpar_valor)
    
    frota = ['CUMARU', 'AROEIRA', 'IPE', 'JACARANDA', 'ANGICO', 'CANJERANA', 'LUIZ FELIPE', 'BRENO']
    df_emp = df_emp[df_emp['EMPURRADOR'].isin(frota)].reset_index(drop=True)

    col1, col2 = st.columns(2)
    # Gráfico Financeiro (Mantendo a estrutura que funcionava)
    with col1:
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(x=df_emp['EMPURRADOR'], y=df_emp['PREV_RS'], name='ORÇADO', marker_color='#ADD8E6', text=[f"R$ {v:,.0f}" for v in df_emp['PREV_RS']], textposition='outside'))
        fig1.add_trace(go.Bar(x=df_emp['EMPURRADOR'], y=df_emp['REAL_RS'], name='REALIZADO', marker_color='#00008B', text=[f"R$ {v:,.0f}" for v in df_emp['REAL_RS']], textposition='outside'))
        fig1.update_layout(title="<b>FINANCEIRO POR EMPURRADOR (R$)</b>", barmode='group', font=dict(family="Arial Black"))
        st.plotly_chart(fig1, use_container_width=True)

    # --- BLOCO INFERIOR: DESEMPENHO POR CICLO (AE2:AJ7) ---
    st.divider()
    st.markdown("<h3 style='text-align: center; font-family: Arial Black;'>DESEMPENHO POR CICLO (AF:AJ)</h3>", unsafe_allow_html=True)
    
    # Colunas AF(31) até AJ(35)
    cols_idx = [31, 32, 33, 34, 35]
    labels_ciclos = ["Ciclo 1", "Ciclo 2", "Ciclo 3", "Ciclo 4", "Ciclo 5"]

    # Extração precisa baseada nas linhas da sua planilha
    v_real = [limpar_valor(df_raw.iloc[1, c]) for c in cols_idx]  # Linha Realizado (Azul)
    v_fore = [limpar_valor(df_raw.iloc[2, c]) for c in cols_idx]  # Linha Forecast (Laranja)
    v_diff = [limpar_valor(df_raw.iloc[3, c]) for c in cols_idx]  # Linha Diferença (Amarela)

    fig_ciclo = go.Figure()

    # Barra REALIZADO - Azul
    fig_ciclo.add_trace(go.Bar(x=labels_ciclos, y=v_real, name='REALIZADO', marker_color='#0047AB', 
                             text=[f"<b>R$ {v:,.0f}</b>" for v in v_real], textposition='outside'))

    # Barra FORECAST - Laranja (Agora puxando os valores como R$ 422.042)
    fig_ciclo.add_trace(go.Bar(x=labels_ciclos, y=v_fore, name='FORECAST', marker_color='#FF8C00', 
                             text=[f"<b>R$ {v:,.0f}</b>" for v in v_fore], textposition='outside'))

    # Barra DIFERENÇA - Cor condicional (Verde se positivo, Vermelho se negativo)
    cores_diff = ['#D21F3C' if v < 0 else '#228B22' for v in v_diff]
    fig_ciclo.add_trace(go.Bar(x=labels_ciclos, y=v_diff, name='DIFERENÇA', marker_color=cores_diff, 
                             text=[f"<b>R$ {v:,.0f}</b>" for v in v_diff], textposition='outside'))

    fig_ciclo.update_layout(
        template="plotly_white", 
        barmode='group', 
        height=600,
        font=dict(color="black", family="Arial Black"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
    )

    st.plotly_chart(fig_ciclo, use_container_width=True)
