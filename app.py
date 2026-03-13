import streamlit as st
import pandas as pd
from urllib.parse import quote

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="Zion - Análise de Forecast", layout="wide")

SHEET_ID = "1izHisQGFCLdqQ7d2OSGkAM7gDJrIsLxW9FY741lJ_Ao"
NOME_ABA = "ODM MARÇO"
NOME_ABA_URL = quote(NOME_ABA)

@st.cache_data(ttl=60)
def carregar_dados():
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={NOME_ABA_URL}"
    # Lemos até a coluna O (índice 14) para o operacional e buscamos a coluna U (índice 20) para o Forecast
    df_completo = pd.read_csv(url)
    df_completo.columns = df_completo.columns.str.strip().str.upper()
    return df_completo

try:
    df_full = carregar_dados()
    
    # --- PROCESSAMENTO DOS DADOS ---
    # 1. Lista de Forecast (Coluna U - Baseada na imagem image_4ec31d.png)
    # Nota: Como o CSV traz nomes genéricos para colunas distantes, mapeamos a coluna 'U' que é o 21º índice
    lista_forecast = df_full.iloc[:, 20].dropna().unique().tolist()
    
    # 2. Dados Operacionais (B2 até O50)
    df_operacional = df_full.iloc[0:50, 0:15].copy()
    df_operacional = df_operacional.dropna(subset=['EMPURRADOR'])
    
    # Limpeza de valores para cálculo
    df_operacional['VALOR_NUM'] = pd.to_numeric(df_operacional['TOTAL'].astype(str).str.replace('R$', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '.', regex=False), errors='coerce').fillna(0)
    df_operacional['LTS_NUM'] = pd.to_numeric(df_operacional['COMPRA LITROS'].astype(str).str.upper().str.replace('L', '', regex=False).str.replace('.', '', regex=False), errors='coerce').fillna(0)

    st.title("🚢 Análise de Forecast vs Realizado - Zion")

    # --- TABELA 1: RESUMO POR EMPURRADOR ---
    st.subheader("📊 Comparativo Mensal por Ativo")
    
    resumo = df_operacional.groupby('EMPURRADOR').apply(lambda x: pd.Series({
        'LTS REALIZADO': x[x['STATUS'].str.contains('REALIZADO', na=False, case=False)]['LTS_NUM'].sum(),
        'VALOR REALIZADO': x[x['STATUS'].str.contains('REALIZADO', na=False, case=False)]['VALOR_NUM'].sum(),
        'LTS PROGRAMADO': x[x['STATUS'].str.contains('PROGRAMADO', na=False, case=False)]['LTS_NUM'].sum(),
        'VALOR PROGRAMADO': x[x['STATUS'].str.contains('PROGRAMADO', na=False, case=False)]['VALOR_NUM'].sum()
    })).reset_index()

    st.table(resumo.style.format({
        'LTS REALIZADO': '{:,.0f} L', 'LTS PROGRAMADO': '{:,.0f} L',
        'VALOR REALIZADO': 'R$ {:,.2f}', 'VALOR PROGRAMADO': 'R$ {:,.2f}'
    }))

    # --- ANÁLISE DE IMPACTO (EXTRAPLANO) ---
    total_realizado_geral = resumo['VALOR REALIZADO'].sum()
    empurradores_operacionais = resumo['EMPURRADOR'].unique()
    
    st.markdown("### ⚠️ Alertas de Forecast")
    fora_do_plano = [em for em in empurradores_operacionais if em not in lista_forecast]
    
    if fora_do_plano:
        for em in fora_do_plano:
            valor_em = resumo[resumo['EMPURRADOR'] == em]['VALOR REALIZADO'].sum()
            percentual = (valor_em / total_realizado_geral * 100) if total_realizado_geral > 0 else 0
            st.warning(f"O E/M **{em}** não estava no forecast de Março. Impacto: **{percentual:.2f}%** da representatividade do total realizado.")
    else:
        st.success("Todos os empurradores estão dentro do planejado (Forecast).")

    st.divider()

    # --- TABELA 2: REALIZADOS DETALHADO (COMPACTO) ---
    st.subheader("✅ Detalhamento de Cargas Realizadas")
    df_real = df_operacional[df_operacional['STATUS'].str.contains('REALIZADO', na=False, case=False)]
    
    if not df_real.empty:
        # Colunas pedidas: Empurrador | Compra Litros | SC | Pedido | SLA | Entrega
        # Ajustamos para os nomes exatos que estão na sua planilha
        colunas_finais = ['EMPURRADOR', 'COMPRA LITROS', 'SC', 'PEDIDO', 'SLA PC', 'DT ENTREGA']
        st.dataframe(df_real[colunas_finais], use_container_width=True, hide_index=True)
    else:
        st.info("Nenhuma carga realizada para exibir.")

except Exception as e:
    st.error(f"Erro na análise: {e}")
