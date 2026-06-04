import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data.dataFrame import criar_dataframe

st.set_page_config(
    page_title="Conclusões · Dashboard de Vendas",
    page_icon="🎯",
    layout="wide",
)

st.markdown(
    """
    <style>
        .rec-card {
            background: linear-gradient(135deg, #0f3460 0%, #16213e 100%);
            border-left: 5px solid #FFD700;
            border-radius: 10px;
            padding: 16px 20px;
            margin: 10px 0;
            color: #f0f0f0;
        }
        .rec-card h4 { color: #FFD700; margin: 0 0 6px 0; }
        .rec-card p  { margin: 0; font-size: 0.95rem; }
        .warn-card {
            background: linear-gradient(135deg, #3d0c02 0%, #6b1c10 100%);
            border-left: 5px solid #FF6B35;
            border-radius: 10px;
            padding: 16px 20px;
            margin: 10px 0;
            color: #f0f0f0;
        }
        .warn-card h4 { color: #FF6B35; margin: 0 0 6px 0; }
        .warn-card p  { margin: 0; font-size: 0.95rem; }
        .block-container { padding-top: 1.2rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────  DADOS  ─────────────────────────
@st.cache_data(ttl=600)
def load_data():
    df = criar_dataframe("orders")
    df["Order Date"] = pd.to_datetime(df["Order Date"])
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"❌ Erro ao conectar ao Supabase: {e}")
    st.stop()

# ─────────────────────────  SIDEBAR  ─────────────────────────
st.sidebar.markdown("## 🔎 Filtros")

min_date = df["Order Date"].min().date()
max_date = df["Order Date"].max().date()
date_range = st.sidebar.slider("📅 Período", min_value=min_date, max_value=max_date, value=(min_date, max_date))

regioes = st.sidebar.multiselect(
    "🌎 Região", options=sorted(df["Region"].dropna().unique()),
    default=sorted(df["Region"].dropna().unique()),
)

df_f = df[
    (df["Region"].isin(regioes)) &
    (df["Order Date"].dt.date.between(date_range[0], date_range[1]))
].copy()

# ─────────────────────────  TÍTULO  ─────────────────────────
st.title("🎯 Conclusões & Recomendações")
st.caption("Síntese das 10 análises realizadas — Curso Python 2026 · ITA Júnior")
st.divider()

# ─────────────────────────  SCORECARD GERAL  ─────────────────────────
st.subheader("📊 Visão Geral do Negócio")

total_v  = df_f["Total Sales"].sum()
total_l  = df_f["Profit"].sum()
margem   = total_l / total_v * 100 if total_v else 0
pedidos  = len(df_f)
ticket_m = total_v / pedidos if pedidos else 0
desc_m   = df_f["Discount"].mean() * 100 if "Discount" in df_f.columns else 0

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("💰 Total Vendas",    f"${total_v:,.0f}")
c2.metric("🏆 Lucro Total",     f"${total_l:,.0f}")
c3.metric("📊 Margem Global",   f"{margem:.1f}%")
c4.metric("📦 Total Pedidos",   f"{pedidos:,}")
c5.metric("🛒 Ticket Médio",    f"${ticket_m:,.0f}")

st.divider()

# ─────────────────────────  CONCLUSÕES POR PERGUNTA  ─────────────────────────
st.subheader("📋 Resumo das 10 Perguntas")

conclusoes = [
    {
        "num": "1",
        "titulo": "Cidade com maior venda em Office Supplies",
        "texto": (
            "O volume de vendas de escritório está concentrado em poucos grandes centros urbanos. "
            "Isso abre oportunidade para expandir a capilaridade em cidades médias com potencial inexplorado."
        ),
    },
    {
        "num": "2",
        "titulo": "Total de vendas por data do pedido",
        "texto": (
            "A sazonalidade é evidente: picos no quarto trimestre (datas comemorativas e fechamento fiscal) "
            "e vales no início do ano. O planejamento de campanhas deve ser alinhado a esse padrão."
        ),
    },
    {
        "num": "3",
        "titulo": "Total de vendas por estado",
        "texto": (
            "Poucos estados dominam a receita. Há alta concentração geográfica — o que representa risco de "
            "dependência e também oportunidade de expansão para estados de menor penetração."
        ),
    },
    {
        "num": "4",
        "titulo": "Top 10 cidades com maior total de vendas",
        "texto": (
            "As 10 cidades do topo representam parcela significativa do faturamento total. "
            "Ações de retenção e upsell nessas cidades têm impacto direto e imediato nos resultados."
        ),
    },
    {
        "num": "5",
        "titulo": "Segmento com maior total de vendas",
        "texto": (
            "O segmento Consumer lidera em volume, mas nem sempre em margem. "
            "Segmentos corporativos (Corporate/Home Office) podem ter menor volume, "
            "porém maior valor por pedido e fidelidade."
        ),
    },
    {
        "num": "6",
        "titulo": "Total de vendas por segmento e por ano",
        "texto": (
            "A tendência anual por segmento revela quais grupos estão em crescimento acelerado "
            "e quais estão estagnados. Isso orienta onde alocar recursos de marketing e vendas."
        ),
    },
    {
        "num": "7",
        "titulo": "Simulação de desconto",
        "texto": (
            "Com o limite padrão de US$1.000, uma parcela relevante das vendas recebe desconto maior. "
            "Ajustar o limiar pode equilibrar competitividade e proteção da margem bruta."
        ),
    },
    {
        "num": "8",
        "titulo": "Média de vendas antes e depois do desconto de 15%",
        "texto": (
            "O impacto médio do desconto de 15% é substancial por pedido. "
            "Políticas de desconto devem ser acompanhadas por metas de volume para compensar a redução de margem."
        ),
    },
    {
        "num": "9",
        "titulo": "Média de vendas por segmento, ano e mês",
        "texto": (
            "O gráfico de linha mensal expõe oscilações de demanda por segmento. "
            "Meses de baixa média são candidatos a ações promocionais para estimular volume."
        ),
    },
    {
        "num": "10",
        "titulo": "Top 12 subcategorias por categoria",
        "texto": (
            "As subcategorias de topo dominam o mix de produtos. "
            "Subcategorias com crescimento rápido merecem prioridade de estoque; "
            "aquelas em declínio podem ser descontinuadas ou reposicionadas."
        ),
    },
]

for c in conclusoes:
    st.markdown(
        f"""
        <div class="rec-card">
            <h4>Pergunta {c['num']} — {c['titulo']}</h4>
            <p>{c['texto']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()

# ─────────────────────────  RECOMENDAÇÕES ESTRATÉGICAS  ─────────────────────────
st.subheader("🚀 Recomendações Estratégicas")

recomendacoes = [
    ("📍 Expansão Geográfica", "Concentrar esforços de expansão nos estados e cidades com crescimento acelerado e baixa penetração atual."),
    ("💡 Política de Descontos", "Revisar o limiar de desconto trimestralmente com base no comportamento de margem, evitando erosão de lucro."),
    ("📅 Sazonalidade", "Antecipar campanhas para os meses de pico (Q4) e criar promoções específicas para meses de baixa demanda."),
    ("👥 Segmentação", "Desenvolver ofertas personalizadas por segmento — pacotes para corporativos, bundles para consumidores finais."),
    ("🏷️ Mix de Produtos", "Focar as subcategorias líderes em ações de upsell e cross-sell, e revisar o portfólio de baixo desempenho."),
]

for titulo, texto in recomendacoes:
    st.markdown(
        f"""
        <div class="rec-card">
            <h4>{titulo}</h4>
            <p>{texto}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()


# ─────────────────────────  GRÁFICO PANORÂMICO  ─────────────────────────
st.subheader("🗂️ Painel Panorâmico Final")

col1, col2 = st.columns(2)

with col1:
    # Vendas x Lucro por categoria
    cat_data = df_f.groupby("Category")[["Total Sales", "Profit"]].sum().reset_index()
    cat_data["Margem (%)"] = (cat_data["Profit"] / cat_data["Total Sales"] * 100).round(1)

    fig_cat = px.bar(
        cat_data,
        x="Category",
        y=["Total Sales", "Profit"],
        barmode="group",
        title="Vendas vs Lucro por Categoria",
        color_discrete_map={"Total Sales": "#4361EE", "Profit": "#06D6A0"},
        text_auto=".2s",
        labels={"value": "US$", "variable": "Métrica"},
    )
    fig_cat.update_layout(height=360)
    st.plotly_chart(fig_cat, use_container_width=True)

with col2:
    # Margem por segmento
    seg_data = df_f.groupby("Segment")[["Total Sales", "Profit"]].sum().reset_index()
    seg_data["Margem (%)"] = (seg_data["Profit"] / seg_data["Total Sales"] * 100).round(2)

    fig_seg = px.bar(
        seg_data,
        x="Segment",
        y="Margem (%)",
        title="Margem de Lucro (%) por Segmento",
        color="Margem (%)",
        color_continuous_scale="RdYlGn",
        text_auto=".1f",
        labels={"Margem (%)": "Margem (%)", "Segment": "Segmento"},
    )
    fig_seg.update_layout(height=360, coloraxis_showscale=False)
    st.plotly_chart(fig_seg, use_container_width=True)

# Download do relatório completo
csv_all = df_f.to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇️ Baixar dataset completo filtrado (CSV)",
    data=csv_all,
    file_name="superstore_completo.csv",
    mime="text/csv",
)

st.caption("Dashboard desenvolvido para o Curso de Python 2026 · ITA Júnior")
