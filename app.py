import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from urllib.parse import quote

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Zion Dashboard", layout="wide")

SHEET_ID = "1izHisQGFCLdqQ7d2OSGkAM7gDJrIsLxW9FY741lJ_Ao"

@st.cache_data(ttl=2)
def carregar_dados(aba):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(aba)}"
    return pd.read_csv(url, dtype=str).fillna("0")

def limpar_valor(valor):
    if not valor or str(valor).strip() in ["0", "", "R$ 0,00"]: return 0.0
    try:
        # Remove R$, pontos de milhar e trata vírgula decimal
        s = str(valor).replace('R$', '').replace('.', '').replace(',', '.').replace(' ', '').strip()
        # Trata parênteses ou sinal de menos para valores negativos
        if '(' in s and ')' in s:
            s = s.replace('(', '').replace(')', '')
            return float(s) * -1
        return float(s)
    except:
        return 0.0

# --- PROCESSAMENTO ---
df_raw = carregar_dados("ODM MARÇO")

if not df_raw.empty:
    # --- GRÁFICOS DA FROTA (PARTE SUPERIOR) ---
    df_emp = pd.DataFrame()
    df_emp['EMPURRADOR'] = df_raw.iloc[:, 20].str.strip().str.upper()
    df_emp['PREV_RS'] = df_raw.iloc[:, 21].apply(limpar_valor)
    df_emp['REAL_RS'] = df_raw.iloc[:, 23].apply(limpar_valor)
    df_emp['FORE_L'] = df_raw.iloc[:, 22].apply(limpar_valor)
    df_emp['REAL_L'] = df_raw.iloc[:, 25].apply(limpar_valor)
    
    frota = ['CUMARU', 'AROEIRA', 'IPE', 'JACARANDA', 'ANGICO', 'CANJERANA', 'LUIZ FELIPE', 'BRENO']
    df_emp = df_emp[df_emp['EMPURRADOR'].isin(frota)].reset_index(drop=True)

    st.markdown("<h2 style='text-align: center;'>PAINEL DE PERFORMANCE ZION</h2>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(x=df_emp['EMPURRADOR'], y=df_emp['PREV_RS'], name='ORÇADO', marker_color='#ADD8E6', text=[f"R$ {v:,.0f}" for v in df_emp['PREV_RS']], textposition='outside'))
        fig1.add_trace(go.Bar(x=df_emp['EMPURRADOR'], y=df_emp['REAL_RS'], name='REALIZADO', marker_color='#00008B', text=[f"R$ {v:,.0f}" for v in df_emp['REAL_RS']], textposition='outside'))
        fig1.update_layout(title="FINANCEIRO (R$)", barmode='group', font=dict(family="Arial Black"))
        st.plotly_chart(fig1, use_container_width=True)

    # --- GRÁFICO DE CICLOS (INTERVALO AE2:AJ7) ---
    st.divider()
    st.markdown("<h3 style='text-align: center;'>DESEMPENHO POR CICLO (COMPARATIVO REAL VS FORECAST)</h3>", unsafe_allow_html=True)
    
    # Colunas AF (31) até AJ (35)
    cols_ciclos = [31, 32, 33, 34, 35] 
    labels_ciclos = ["Ciclo 1", "Ciclo 2", "Ciclo 3", "Ciclo 4", "Ciclo 5"]

    # Localização exata baseada na imagem das linhas coloridas
    # Linha do "Realizado" (Azul) = Index 1
    # Linha do "Forecast" (Laranja) = Index 2
    # Linha da "Diferença" (Amarelo) = Index 3
    v_real = [limpar_valor(df_raw.iloc[1, c]) for c in cols_ciclos]
    v_fore = [limpar_valor(df_raw.iloc[2, c]) for c in cols_ciclos]
    v_diff = [limpar_valor(df_raw.iloc[3, c]) for c in cols_ciclos]

    fig_ciclo = go.Figure()
    
    # Barra REALIZADO (Azul)
    fig_ciclo.add_trace(go.Bar(x=labels_ciclos, y=v_real, name='REALIZADO', marker_color='#1E90FF', 
                             text=[f"<b>R$ {v:,.0f}</b>" for v in v_real], textposition='outside'))
    
    # Barra FORECAST (Laranja) - PEGANDO VALOR DA LINHA AE:3
    fig_ciclo.add_trace(go.Bar(x=labels_ciclos, y=v_fore, name='FORECAST', marker_color='#FF8C00', 
                             text=[f"<b>R$ {v:,.0f}</b>" for v in v_fore], textposition='outside'))
    
    # Barra DIFERENÇA (Cor condicional: Verde para positivo, Vermelho para negativo)
    cores_diff = ['#D21F3C' if v < 0 else '#228B22' for v in v_diff]
    fig_ciclo.add_trace(go.Bar(x=labels_ciclos, y=v_diff, name='DIFERENÇA', marker_color=cores_diff, 
                             text=[f"<b>R$ {v:,.0f}</b>" for v in v_diff], textposition='outside'))

    fig_ciclo.update_layout(template="plotly_white", barmode='group', height=600, 
                            font=dict(color="black", family="Arial Black"),
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5))
    
    st.plotly_chart(fig_ciclo, use_container_width=True)
