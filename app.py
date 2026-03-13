import streamlit as st
import pandas as pd
from urllib.parse import quote

# 1. CONFIGURAÇÃO DE TELA E CSS AGRESSIVO PARA COMPACTAR
st.set_page_config(page_title="Zion - Dashboard", layout="wide")

st.markdown("""
    <style>
    /* Remove margens e preenchimentos excessivos da página */
    .block-container {padding-top: 0.5rem; padding-bottom: 0rem; padding-left: 1rem; padding-right: 1rem;}
    
    /* Diminui o espaço entre os elementos (widgets) */
    [data-testid="stVerticalBlock"] {gap: 0.5rem;}
    
    /* Títulos mais sóbrios e colados na tabela */
    h3 {margin-top: 0rem; margin-bottom: 0.1rem; font-size: 1.0rem !important; font-weight: bold;}
    
    /* Métricas menores e lado a lado */
    [data-testid="stMetricValue"] {font-size: 1.1rem !important; font-weight: bold;}
    [data-testid="stMetricLabel"] {font-size: 0.75rem !important;}
    
    /* Ajuste para as tabelas ocuparem menos altura */
    .stDataFrame {margin-bottom: 0.5rem;}
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
    bloco_forecast = df_full.iloc[0:20, 20:27].astype(str).apply(lambda x: x.str.strip().str.upper())
    lista_forecast = set(pd.unique(bloco_forecast.values.ravel()))
    
    # --- MAPEAMENTO OPERACIONAL ---
    df_op = df_full.iloc[0:100, 0:15].copy()
    col_emp = df_op.columns[2] # EMPURRADOR
    df_op = df_op.dropna(subset=[col_emp])
    
    # Limpeza e Conversão
    df_op['VALOR_NUM'] = pd.to_numeric(df_op['TOTAL'].astype(str).str.replace('R$', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).str.strip(), errors='coerce').fillna(0)
    df_op['LTS_NUM'] = pd.to_numeric(df_op['COMPRA LITROS'].astype(str).str.upper().str.replace('L', '', regex=False).str.replace('.', '', regex=False).str.strip(), errors='coerce').fillna(0)
    df_op['EMP_KEY'] = df_op[col_emp].astype(str).str.strip().str.upper()

    st.title("🚢 Monitoramento Zion")

    # --- TABELA 1: CONSUMO CONSOLIDADO ---
    resumo = df_op.groupby('EMP_KEY').apply(lambda x: pd.Series({
        'REALIZADO (L)': x[x['STATUS'].astype(str).str.upper().str.contains('REALIZADO', na=False)]['LTS_NUM'].sum(),
        'REALIZADO (R$)': x[x['STATUS'].astype(str).str.upper().str.contains('REALIZADO', na=False)]['VALOR_NUM'].sum(),
        'PROG. (L)': x[x['STATUS'].astype(str).str.upper().str.contains('PROGRAMADO', na=False)]['LTS_NUM'].sum(),
        'PROG. (R$)': x[x['STATUS'].astype(str).str.upper().str.contains('PROGRAMADO', na=False)]['VALOR_NUM'].sum()
    })).reset_index().rename(columns={'EMP_KEY': 'EMPURRADOR'})

    st.markdown("### 📊 Consumo Consolidado")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Realizado (L)", f"{resumo['REALIZADO (L)'].sum():,.0f}L".replace(',', '.'))
    m2.metric("Realizado (R$)", f"R${resumo['REALIZADO (R$)'].sum():,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    m3.metric("Prog. (L)", f"{resumo['PROG. (L)'].sum():,.0f}L".replace(',', '.'))
    m4.metric("Prog. (R$)", f"R${resumo['PROG. (R$)'].sum():,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))

    st.dataframe(
        resumo.style.format({'REALIZADO (L)': '{:,.0f}', 'PROG. (L)': '{:,.0f}', 'REALIZADO (R$)': '{:,.2f}', 'PROG. (R$)': '{:,.2f}'}),
        use_container_width=True, hide_index=True,
        column_config={
            "EMPURRADOR": st.column_config.TextColumn("Ativo", width="medium"),
            "REALIZADO (L)": st.column_config.NumberColumn("Real (L)", width="small"),
            "REALIZADO (R$)": st.column_config.NumberColumn("Real (R$)", width="small"),
            "PROG. (L)": st.column_config.NumberColumn("Prog (L)", width="small"),
            "PROG. (R$)": st.column_config.NumberColumn("Prog (R$)", width="small")
        }
    )

    # --- ALERTAS FORECAST ---
    total_real = resumo['REALIZADO (R$)'].sum()
    alertas = [f"⚠️ **{r['EMPURRADOR']}** extraplano" for _, r in resumo.iterrows() if r['REALIZADO (R$)'] > 0 and r['EMPURRADOR'] not in lista_forecast]

    if alertas:
        cols = st.columns(len(alertas) if len(alertas) < 6 else 6)
        for i, a in enumerate(alertas): cols[i%6].warning(a)

    # --- TABELA 2: DETALHAMENTO REALIZADOS ---
    st.markdown("---")
    st.markdown("### ✅ Detalhes das Entregas")
    df_real = df_op[df_op['STATUS'].astype(str).str.upper().str.contains('REALIZADO', na=False)]
    
    if not df_real.empty:
        st.dataframe(
            df_real[[col_emp, 'COMPRA LITROS', 'SC', 'PEDIDO', 'SLA PC', 'DT ENTREGA']],
            use_container_width=True, hide_index=True,
            column_config={
                col_emp: st.column_config.TextColumn("Ativo", width="medium"),
                "COMPRA LITROS": st.column_config.TextColumn("Lts", width="small"),
                "SC": st.column_config.TextColumn("SC", width="small"),
                "PEDIDO": st.column_config.TextColumn("Pedido", width="small"),
                "SLA PC": st.column_config.TextColumn("SLA", width="small"),
                "DT ENTREGA": st.column_config.TextColumn("Entrega", width="medium")
            }
        )

except Exception as e:
    st.error(f"Erro: {e}")
