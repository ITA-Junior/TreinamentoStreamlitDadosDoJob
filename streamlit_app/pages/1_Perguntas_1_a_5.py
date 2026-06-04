import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data.dataFrame import criar_dataframe

st.set_page_config(
    page_title="Perguntas 1–5 · Dashboard de Vendas",
    page_icon="📋",
    layout="wide",
)

# ─────────────────────────  ESTILO  ─────────────────────────
st.markdown(
    """
    <style>
        .insight-box {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            border-left: 4px solid #FFD700;
            border-radius: 8px;
            padding: 14px 18px;
            margin: 10px 0 20px 0;
            color: #f0f0f0;
        }
        .insight-box strong { color: #FFD700; }
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
    df_full = load_data()
except Exception as e:
    st.error(f"❌ Erro ao conectar ao Supabase: {e}")
    st.stop()

# ─────────────────────────  SIDEBAR  ─────────────────────────
st.sidebar.markdown("## 🔎 Filtros")

min_date = df_full["Order Date"].min().date()
max_date = df_full["Order Date"].max().date()
date_range = st.sidebar.slider("📅 Período", min_value=min_date, max_value=max_date, value=(min_date, max_date))

regioes = st.sidebar.multiselect(
    "🌎 Região", options=sorted(df_full["Region"].dropna().unique()),
    default=sorted(df_full["Region"].dropna().unique()),
)
segmentos = st.sidebar.multiselect(
    "👥 Segmento", options=sorted(df_full["Segment"].dropna().unique()),
    default=sorted(df_full["Segment"].dropna().unique()),
)

df = df_full[
    (df_full["Region"].isin(regioes)) &
    (df_full["Segment"].isin(segmentos)) &
    (df_full["Order Date"].dt.date.between(date_range[0], date_range[1]))
].copy()

if df.empty:
    st.warning("⚠️ Nenhum dado para os filtros selecionados.")
    st.stop()

# ─────────────────────────  TÍTULO  ─────────────────────────
st.title("📋 Perguntas de Negócio — 1 a 5")
st.caption("Análises baseadas no dataset Superstore filtrado pela sidebar")
st.divider()


# ══════════════════════════════════════════════════════
#  PERGUNTA 1
# ══════════════════════════════════════════════════════
st.header("🥇 Pergunta 1 — Cidade com maior venda em Office Supplies")

df_os = df[df["Category"] == "Office Supplies"]

if df_os.empty:
    st.warning("Nenhum dado de 'Office Supplies' para os filtros selecionados.")
else:
    cidade_os = (
        df_os.groupby("City")["Total Sales"]
        .sum()
        .reset_index()
        .sort_values("Total Sales", ascending=False)
    )

    top_cidade = cidade_os.iloc[0]

    col1, col2 = st.columns([1, 2])

    with col1:
        st.metric("🏆 Cidade Líder", top_cidade["City"])
        st.metric("💰 Total de Vendas", f"${top_cidade['Total Sales']:,.2f}")
        st.markdown(f"**Top 5 cidades — Office Supplies**")
        st.dataframe(
            cidade_os.head(5).rename(columns={"City": "Cidade", "Total Sales": "Vendas (US$)"})
            .assign(**{"Vendas (US$)": lambda x: x["Vendas (US$)"].map("${:,.2f}".format)})
            .reset_index(drop=True),
            hide_index=True,
            use_container_width=True,
        )

    with col2:
        fig = px.bar(
            cidade_os.head(15),
            x="Total Sales",
            y="City",
            orientation="h",
            text_auto=".2s",
            title="Top 15 Cidades — Vendas de Office Supplies",
            color="Total Sales",
            color_continuous_scale="Blues",
            labels={"Total Sales": "Vendas (US$)", "City": "Cidade"},
        )
        fig.update_layout(height=420, yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        f"""
        <div class="insight-box">
        💡 <strong>Insight:</strong> A cidade de <strong>{top_cidade['City']}</strong> lidera as vendas
        em Office Supplies com <strong>${top_cidade['Total Sales']:,.2f}</strong>. Isso sugere alta concentração
        de clientes corporativos ou forte demanda por material de escritório nessa localidade —
        um ponto estratégico para campanhas regionais e gestão de estoque.
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()


# ══════════════════════════════════════════════════════
#  PERGUNTA 2
# ══════════════════════════════════════════════════════
st.header("📅 Pergunta 2 — Total de Vendas por Data do Pedido")

agregacao = st.radio(
    "Agregar por:",
    ["Dia", "Mês", "Trimestre", "Ano"],
    horizontal=True,
    index=1,
    key="p2_agr",
)

df2 = df.copy()

if agregacao == "Dia":
    df2["Periodo"] = df2["Order Date"].dt.date.astype(str)
elif agregacao == "Mês":
    df2["Periodo"] = df2["Order Date"].dt.to_period("M").astype(str)
elif agregacao == "Trimestre":
    df2["Periodo"] = df2["Order Date"].dt.to_period("Q").astype(str)
else:
    df2["Periodo"] = df2["Order Date"].dt.year.astype(str)

vendas_data = (
    df2.groupby("Periodo")["Total Sales"]
    .sum()
    .reset_index()
    .sort_values("Periodo")
)

fig2 = px.bar(
    vendas_data,
    x="Periodo",
    y="Total Sales",
    title=f"Total de Vendas por {agregacao}",
    text_auto=".2s",
    color="Total Sales",
    color_continuous_scale="Viridis",
    labels={"Total Sales": "Vendas (US$)", "Periodo": agregacao},
)
fig2.update_layout(height=420, xaxis_tickangle=-45, coloraxis_showscale=False)
st.plotly_chart(fig2, use_container_width=True)

col_a, col_b = st.columns(2)
col_a.metric("📈 Período com mais vendas", vendas_data.loc[vendas_data["Total Sales"].idxmax(), "Periodo"])
col_a.metric("💰 Valor máximo",  f"${vendas_data['Total Sales'].max():,.2f}")
col_b.metric("📉 Período com menos vendas", vendas_data.loc[vendas_data["Total Sales"].idxmin(), "Periodo"])
col_b.metric("💸 Valor mínimo", f"${vendas_data['Total Sales'].min():,.2f}")

st.markdown(
    f"""
    <div class="insight-box">
    💡 <strong>Insight:</strong> A análise temporal revela a sazonalidade das vendas ao longo do tempo.
    O período <strong>{vendas_data.loc[vendas_data['Total Sales'].idxmax(), 'Periodo']}</strong>
    foi o mais lucrativo, com <strong>${vendas_data['Total Sales'].max():,.2f}</strong> em vendas.
    Identificar esses padrões sazonais é fundamental para planejar campanhas promocionais e
    ajustar o nível de estoque nos períodos de pico.
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()


# ══════════════════════════════════════════════════════
#  PERGUNTA 3
# ══════════════════════════════════════════════════════
st.header("🗺️ Pergunta 3 — Total de Vendas por Estado")

if "State" not in df.columns:
    st.warning("Coluna 'State' não encontrada no dataset.")
else:
    vendas_estado = (
        df.groupby("State")["Total Sales"]
        .sum()
        .reset_index()
        .sort_values("Total Sales", ascending=False)
    )

    top_n_estados = st.slider("Exibir Top N estados", min_value=5, max_value=len(vendas_estado), value=20, key="p3_topn")

    col1, col2 = st.columns([2, 1])

    with col1:
        fig3 = px.bar(
            vendas_estado.head(top_n_estados),
            x="State",
            y="Total Sales",
            title=f"Top {top_n_estados} Estados por Total de Vendas",
            text_auto=".2s",
            color="Total Sales",
            color_continuous_scale="RdYlGn",
            labels={"Total Sales": "Vendas (US$)", "State": "Estado"},
        )
        fig3.update_layout(height=420, xaxis_tickangle=-45, coloraxis_showscale=False)
        st.plotly_chart(fig3, use_container_width=True)

    with col2:
        st.markdown(f"**Ranking completo ({len(vendas_estado)} estados)**")
        st.dataframe(
            vendas_estado.assign(**{"Total Sales": vendas_estado["Total Sales"].map("${:,.2f}".format)})
            .rename(columns={"State": "Estado", "Total Sales": "Vendas (US$)"})
            .reset_index(drop=True),
            hide_index=True,
            use_container_width=True,
            height=400,
        )

    top_estado = vendas_estado.iloc[0]
    st.markdown(
        f"""
        <div class="insight-box">
        💡 <strong>Insight:</strong> <strong>{top_estado['State']}</strong> lidera as vendas entre todos os estados
        com <strong>${top_estado['Total Sales']:,.2f}</strong>. A concentração das vendas nos estados de topo
        indica que esforços de expansão devem focar em estados intermediários com potencial de crescimento,
        enquanto os líderes precisam de estratégias de retenção e fidelização.
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()


# ══════════════════════════════════════════════════════
#  PERGUNTA 4
# ══════════════════════════════════════════════════════
st.header("🏙️ Pergunta 4 — Top 10 Cidades com Maior Total de Vendas")

top_n_cidades = st.slider("Número de cidades", min_value=5, max_value=30, value=10, key="p4_topn")

vendas_cidade = (
    df.groupby("City")["Total Sales"]
    .sum()
    .reset_index()
    .sort_values("Total Sales", ascending=False)
    .head(top_n_cidades)
)

col1, col2 = st.columns([2, 1])

with col1:
    fig4 = px.bar(
        vendas_cidade,
        x="City",
        y="Total Sales",
        title=f"Top {top_n_cidades} Cidades — Total de Vendas",
        text_auto=".2s",
        color="Total Sales",
        color_continuous_scale="Turbo",
        labels={"Total Sales": "Vendas (US$)", "City": "Cidade"},
    )
    fig4.update_layout(height=400, xaxis_tickangle=-30, coloraxis_showscale=False)
    st.plotly_chart(fig4, use_container_width=True)

with col2:
    st.markdown(f"**Top {top_n_cidades} cidades**")
    df_show = vendas_cidade.copy()
    df_show["Rank"] = range(1, len(df_show) + 1)
    df_show = df_show[["Rank", "City", "Total Sales"]].rename(
        columns={"City": "Cidade", "Total Sales": "Vendas (US$)"}
    )
    df_show["Vendas (US$)"] = df_show["Vendas (US$)"].map("${:,.2f}".format)
    st.dataframe(df_show, hide_index=True, use_container_width=True)

top_cidade4 = vendas_cidade.iloc[0]
st.markdown(
    f"""
    <div class="insight-box">
    💡 <strong>Insight:</strong> As top {top_n_cidades} cidades são responsáveis por uma parcela significativa
    do faturamento total. <strong>{top_cidade4['City']}</strong> encabeça o ranking com
    <strong>${top_cidade4['Total Sales']:,.2f}</strong>. Concentrar ações logísticas, marketing e
    atendimento nessas cidades gera impacto direto e mensurável na receita.
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()


# ══════════════════════════════════════════════════════
#  PERGUNTA 5
# ══════════════════════════════════════════════════════
st.header("👥 Pergunta 5 — Segmento com Maior Total de Vendas")

vendas_segmento = (
    df.groupby("Segment")["Total Sales"]
    .sum()
    .reset_index()
    .sort_values("Total Sales", ascending=False)
)

lucro_segmento = (
    df.groupby("Segment")["Profit"]
    .sum()
    .reset_index()
)

df_seg_merged = vendas_segmento.merge(lucro_segmento, on="Segment")
df_seg_merged["Margem (%)"] = (df_seg_merged["Profit"] / df_seg_merged["Total Sales"] * 100).round(1)

col1, col2 = st.columns([1, 1])

with col1:
    fig5a = px.pie(
        df_seg_merged,
        names="Segment",
        values="Total Sales",
        title="Distribuição de Vendas por Segmento",
        hole=0.45,
        color_discrete_sequence=px.colors.qualitative.Bold,
    )
    fig5a.update_traces(textposition="outside", textinfo="percent+label")
    fig5a.update_layout(height=380)
    st.plotly_chart(fig5a, use_container_width=True)

with col2:
    fig5b = px.bar(
        df_seg_merged,
        x="Segment",
        y=["Total Sales", "Profit"],
        title="Vendas vs Lucro por Segmento",
        barmode="group",
        text_auto=".2s",
        color_discrete_map={"Total Sales": "#4361EE", "Profit": "#06D6A0"},
        labels={"value": "US$", "variable": "Métrica"},
    )
    fig5b.update_layout(height=380)
    st.plotly_chart(fig5b, use_container_width=True)

# Tabela resumo
st.markdown("**Resumo por Segmento**")
df_seg_display = df_seg_merged.copy()
df_seg_display["Total Sales"] = df_seg_display["Total Sales"].map("${:,.2f}".format)
df_seg_display["Profit"]      = df_seg_display["Profit"].map("${:,.2f}".format)
df_seg_display["Margem (%)"]  = df_seg_display["Margem (%)"].map("{:.1f}%".format)
df_seg_display.columns        = ["Segmento", "Vendas (US$)", "Lucro (US$)", "Margem (%)"]
st.dataframe(df_seg_display, hide_index=True, use_container_width=True)

top_seg = vendas_segmento.iloc[0]
st.markdown(
    f"""
    <div class="insight-box">
    💡 <strong>Insight:</strong> O segmento <strong>{top_seg['Segment']}</strong> lidera as vendas com
    <strong>${top_seg['Total Sales']:,.2f}</strong>. Entender o perfil de compra por segmento permite
    criar estratégias de precificação diferenciadas, programas de fidelidade específicos e
    direcionar o time de vendas para os clientes de maior valor e potencial.
    </div>
    """,
    unsafe_allow_html=True,
)
