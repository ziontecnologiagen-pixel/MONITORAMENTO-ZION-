import streamlit as st
import pandas as pd
from urllib.parse import quote

# 1. CONFIGURAÇÃO DE TELA E CSS PARA COMPACTAR TUDO
st.set_page_config(page_title="Zion - Monitoramento", layout="wide")

st.markdown("""
    <style>
    .block-container {padding-top: 0.5rem; padding-bottom: 0rem; padding-left: 1rem; padding-right: 1rem;}
    h3 {margin-top: 0rem; margin-bottom: 0.2rem; font-size: 1.1rem;}
    [data-testid="stMetricValue"] {font-size: 1.2rem !important; color: #1f77b4;}
    [data-testid="stMetricLabel"] {font-size: 0.8rem !important;}
    .stDataFrame {margin-bottom: 1rem;}
    </style>
    """, unsafe_allow_html=True)

SHEET_ID = "1izHisQGFCLdqQ7d2OSGkAM7gDJrIsLxW9FY741lJ_Ao"
NOME_ABA = "ODM MARÇO"
NOME_ABA_URL = quote(NOME_ABA)

@st.cache_data(ttl=30)
def carregar_dados():
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={NOME_ABA_URL}"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip().str.upper()
    return df

try:
    df_full = carregar_dados()
    
    # --- MAPEAMENTO FORECAST (U2 ATÉ AA20) ---
    # Pegamos um bloco maior para não pular ninguém como o BRENO
    bloco_forecast = df_full.iloc[0:20, 20:27].astype(str).apply(lambda x: x.str.strip().str.upper())
    lista_forecast = pd.unique(bloco_forecast.values.ravel())
    lista_forecast = set([n for n in lista_forecast if n not in ['NAN', '', 'NONE', '0']])
    
    # --- MAPEAMENTO OPERACIONAL ---
    df_op = df_full.iloc[0:100, 0:15].copy()
    col_emp = df_op.columns[2] # Coluna EMPURRADOR
    df_op = df_op.dropna(subset=[col_emp])
    
    # Limpeza para cálculos
    df_op['VALOR_NUM'] = pd.to_numeric(df_op['TOTAL'].astype(str).str.replace('R$', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).str.strip(), errors='coerce').fillna(0)
    df_op['LTS_NUM'] = pd.to_numeric(df_op['COMPRA LITROS'].astype(str).str.upper().str.replace('L', '', regex=False).str.replace('.', '', regex=False).str.strip(), errors='coerce').fillna(0)
    df_op['EMP_KEY'] = df_op[col_emp].astype(str).str.strip().str.upper()

    st.title("🚢 Monitoramento Zion Integrado")

    # --- TABELA 1: CONSUMO CONSOLIDADO ---
    resumo = df_op.groupby('EMP_KEY').apply(lambda x: pd.Series({
        'Realizado (L)': x[x['STATUS'].astype(str).str.upper().str.contains('REALIZADO', na=False)]['LTS_NUM'].sum(),
        'Realizado (R$)': x[x['STATUS'].astype(str).str.upper().str.contains('REALIZADO', na=False)]['VALOR_NUM'].sum(),
        'Programado (L)': x[x['STATUS'].astype(str).str.upper().str.contains('PROGRAMADO', na=False)]['LTS_NUM'].sum(),
        'Programado (R$)': x[x['STATUS'].astype(str).str.upper().str.contains('PROGRAMADO', na=False)]['VALOR_NUM'].sum()
    })).reset_index().rename(columns={'EMP_KEY': 'EMPURRADOR'})

    # TOTAIS TOPO TABELA 1
    st.markdown("### 📊 Consumo por Ativo")
    t1, t2, t3, t4 = st.columns(4)
    t1.metric("Total Realizado (L)", f"{resumo['Realizado (L)'].sum():,.0f} L".replace(',', '.'))
    t2.metric("Total Realizado (R$)", f"R$ {resumo['Realizado (R$)'].sum():,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    t3.metric("Total Programado (L)", f"{resumo['Programado (L)'].sum():,.0f} L".replace(',', '.'))
    t4.metric("Total Programado (R$)", f"R$ {resumo['Programado (R$)'].sum():,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))

    st.dataframe(
        resumo.style.format({'Realizado (L)': '{:,.0f} L', 'Programado (L)': '{:,.0f} L', 'Realizado (R$)': 'R$ {:,.2f}', 'Programado (R$)': 'R$ {:,.2f}'}),
        use_container_width=True, hide_index=True
    )

    # --- ALERTAS FORECAST ---
    alertas = []
    total_real = resumo['Realizado (R$)'].sum()
    for _, row in resumo.iterrows():
        if row['Realizado (R$)'] > 0 and row['EMPURRADOR'] not in lista_forecast:
            perc = (row['Realizado (R$)'] / total_real * 100) if total_real > 0 else 0
            alertas.append(f"⚠️ **{row['EMPURRADOR']}** extraplano ({perc:.1f}%)")

    if alertas:
        cols = st.columns(len(alertas) if len(alertas) < 5 else 5)
        for i, a in enumerate(alertas): cols[i%5].warning(a)
    else:
        st.success("✅ Todos os ativos realizados estão no Forecast.")

    # --- TABELA 2: DETALHAMENTO REALIZADOS ---
    st.markdown("---")
    st.markdown("### ✅ Detalhes das Entregas (Realizado)")
    df_real = df_op[df_op['STATUS'].astype(str).str.upper().str.contains('REALIZADO', na=False)]
    
    if not df_real.empty:
        # TOTAIS TOPO TABELA 2
        r1, r2 = st.columns(2)
        r1.metric("Litros Entregues", f"{df_real['LTS_NUM'].sum():,.0f} L".replace(',', '.'))
        r2.metric("Custo Total Entregas", f"R$ {df_real['VALOR_NUM'].sum():,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        
        st.dataframe(
            df_real[[col_emp, 'COMPRA LITROS', 'SC', 'PEDIDO', 'SLA PC', 'DT ENTREGA']],
            use_container_width=True, hide_index=True,
            column_config={col_emp: st.column_config.TextColumn("Empurrador", width="medium"), "COMPRA LITROS": st.column_config.TextColumn("Litros", width="small"), "SC": st.column_config.TextColumn("SC", width="small"), "PEDIDO": st.column_config.TextColumn("Pedido", width="small"), "SLA PC": st.column_config.TextColumn("SLA", width="small"), "DT ENTREGA": st.column_config.TextColumn("Entrega", width="medium")}
        )

except Exception as e:
    st.error(f"Erro no processamento: {e}")
