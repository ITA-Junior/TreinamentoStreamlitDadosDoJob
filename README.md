# 📊 Dashboard de Vendas — Superstore

**Curso de Python 2026 · ITA Júnior**

Aplicativo interativo em Streamlit conectado ao Supabase (Postgres) que responde às 10 perguntas de negócio do projeto, com filtros globais, visualizações e insights por análise.

---

## 🚀 Como rodar

### 1. Pré-requisitos

- Python 3.10 ou superior
- Conta no [Supabase](https://supabase.com) com a tabela `orders` populada

### 2. Clone o repositório

```bash
git clone https://github.com/seu-usuario/seu-repo.git
cd seu-repo/streamlit_app
```

### 3. Crie e ative o ambiente virtual

```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate
```

### 4. Instale as dependências

```bash
pip install -r requirements.txt
```

### 5. Configure as variáveis de ambiente

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas credenciais do Supabase:

```env
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua-chave-anon-ou-service-role-aqui
```

> ⚠️ **Nunca commite o `.env` no GitHub.** Ele já está no `.gitignore`.

### 6. Rode o app

```bash
streamlit run main.py
```

Acesse em: `http://localhost:8501`

---

## 📁 Estrutura do Projeto

```
streamlit_app/
├── main.py                    # Página inicial — Visão Geral (KPIs + gráficos resumo)
├── pages/
│   ├── 1_Perguntas_1_a_5.py  # Perguntas de negócio 1 a 5
│   ├── 2_Perguntas_6_a_10.py # Perguntas de negócio 6 a 10
│   └── 3_Conclusoes.py       # Conclusões, recomendações e limitações
├── data/
│   ├── __init__.py
│   └── dataFrame.py           # Conexão Supabase + carga e limpeza dos dados
├── .streamlit/
│   └── config.toml            # Tema dark com cores ITA Júnior
├── .env.example               # Template de variáveis de ambiente
├── requirements.txt
└── README.md
```

---

## 🏗️ Arquitetura

```
Usuário (browser)
      │
      ▼
Streamlit App (main.py + pages/)
      │
      ├── data/dataFrame.py  ──▶  Supabase (Postgres)
      │         │                  tabela: orders
      │         ▼
      │    DataFrame Pandas
      │    (cache 10 min)
      │
      ├── Sidebar Filtros (período, região, segmento, categoria)
      │
      └── Páginas:
           ├── Visão Geral    → KPIs, evolução mensal, tabela
           ├── Perguntas 1–5  → Análises + gráficos + insights
           ├── Perguntas 6–10 → Análises + gráficos + insights
           └── Conclusões     → Resumo estratégico + limitações
```

**Fluxo de dados:**
1. `criar_dataframe("orders")` — busca todos os registros em batches de 1.000 linhas via Supabase Python SDK
2. Limpeza automática: datas inválidas removidas, colunas numéricas convertidas, `Total Sales` calculada se ausente
3. Cache Streamlit (`@st.cache_data(ttl=600)`) evita requisições repetidas ao banco
4. Filtros da sidebar aplicados em memória sobre o DataFrame já carregado

---

## 📋 Perguntas respondidas

| # | Pergunta | Visual |
|---|----------|--------|
| 1 | Cidade com maior venda em Office Supplies | Gráfico de barras horizontal |
| 2 | Total de vendas por data do pedido | Gráfico de barras (dia/mês/trimestre/ano) |
| 3 | Total de vendas por estado | Gráfico de barras + ranking |
| 4 | Top N cidades com maior total de vendas | Gráfico de barras |
| 5 | Segmento com maior total de vendas | Gráfico de pizza + barras agrupadas |
| 6 | Total de vendas por segmento e por ano | Barras agrupadas + linha temporal |
| 7 | Simulação de desconto (>US$1.000 → 15%) | Pizza + métricas |
| 8 | Média antes e depois do desconto de 15% | Barras comparativas + histograma |
| 9 | Média de vendas por segmento, ano e mês | Gráfico de linha + heatmap |
| 10 | Top 12 subcategorias por categoria | Barras + Treemap + Sunburst |

---

## ⭐ Extras implementados

- Botão de download CSV em todas as análises
- Simulador interativo de desconto com sliders (taxa e limiar configuráveis)
- Seção "Erros comuns / limitações dos dados" na página de Conclusões
- Tema dark customizado com cores ITA Júnior
- Cache de dados com TTL de 10 minutos para performance
- Carregamento paginado do Supabase (batches de 1.000 linhas)

---

## 🛡️ Segurança

- Credenciais nunca versionadas (`.env` no `.gitignore`)
- `.env.example` versionado como template
- Variáveis lidas via `os.environ` com `python-dotenv`
