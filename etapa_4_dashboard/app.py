from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(page_title="Avaliações de jogos na Steam", layout="wide")


@st.cache_data
def carregar_dados():
    arquivo = Path(__file__).resolve().parents[1] / "etapa_2_tratamento" / "games_limpo.csv"
    return pd.read_csv(arquivo)


def formatar_inteiro(valor):
    return f"{valor:,.0f}".replace(",", ".")


dados = carregar_dados()

st.title("Avaliações de jogos na Steam")
st.write(
    "Como o preço, o ano de lançamento e a quantidade de avaliações "
    "se relacionam com a aprovação dos títulos da Steam?"
)
st.write(
    "Cada linha da base representa um título do catálogo, incluindo jogos "
    "e conteúdos adicionais. Os preços e as avaliações correspondem ao "
    "momento em que os dados foram coletados."
)
st.caption("Desenvolvido por William Hennemann dos Santos e Murilo Damaceno Diefenbach.")
st.markdown(
    "[Fonte dos dados — Game Recommendations on Steam, no Kaggle]"
    "(https://www.kaggle.com/datasets/antonkozyriev/game-recommendations-on-steam)"
)

# Os dois filtros são aplicados antes de calcular os indicadores e os gráficos.
st.header("Filtros")

anos = sorted(dados["year_release"].dropna().astype(int).unique())
coluna_ano, coluna_preco = st.columns(2)

ano_escolhido = coluna_ano.selectbox(
    "Ano de lançamento",
    ["Todos os anos", *anos]
)

preco_escolhido = coluna_preco.selectbox(
    "Preço final do título",
    ["Todos", "Preço zero", "Pagos"]
)

dados_filtrados = dados

if ano_escolhido != "Todos os anos":
    dados_filtrados = dados_filtrados[
        dados_filtrados["year_release"] == ano_escolhido
    ]

if preco_escolhido == "Preço zero":
    dados_filtrados = dados_filtrados[dados_filtrados["price_final"] == 0]
elif preco_escolhido == "Pagos":
    dados_filtrados = dados_filtrados[dados_filtrados["price_final"] > 0]

st.header("Resumo da seleção")

if dados_filtrados.empty:
    st.metric("Títulos selecionados", 0)
    st.info("Nenhum título encontrado. Escolha outro ano ou outra opção de preço.")
    st.stop()

total_titulos = len(dados_filtrados)
total_avaliacoes = dados_filtrados["user_reviews"].sum()
aprovacao_mediana = dados_filtrados["positive_ratio"].median()

indicador1, indicador2, indicador3 = st.columns(3)
indicador1.metric("Títulos selecionados", formatar_inteiro(total_titulos))
indicador2.metric("Total de avaliações", formatar_inteiro(total_avaliacoes))
indicador3.metric("Aprovação mediana", f"{aprovacao_mediana:g}%".replace(".", ","))
st.caption("Cada título tem o mesmo peso no cálculo da aprovação mediana.")

st.header("Como os jogadores avaliaram os títulos?")

# Gráfico 1 — Quantidade de títulos por classificação
contagem = dados_filtrados["rating"].value_counts().reset_index()
contagem.columns = ["Classificação", "Quantidade de títulos"]

grafico = px.bar(
    contagem,
    x="Quantidade de títulos",
    y="Classificação",
    orientation="h",
    text="Quantidade de títulos",
    title="Quais classificações aparecem mais?"
)
grafico.update_yaxes(autorange="reversed")
st.plotly_chart(grafico)

# Gráfico 2 — Distribuição da aprovação
histograma = px.histogram(
    dados_filtrados,
    x="positive_ratio",
    title="Como se distribui a aprovação dos títulos?",
    labels={"positive_ratio": "Avaliações positivas por título (%)"}
)
histograma.update_traces(xbins=dict(start=0, end=110, size=10))
histograma.update_xaxes(dtick=10)
histograma.update_yaxes(title_text="Quantidade de títulos")
st.plotly_chart(histograma)
st.caption(
    "A barra que começa em 80 reúne os títulos com aprovação de 80% a 89%. "
    "A última barra reúne os títulos com exatamente 100% de aprovação."
)

st.header("Preço e aprovação")

# Gráfico 3 — Aprovação por faixa de preço
faixas = [
    "Preço zero",
    "Até US$ 5",
    "Acima de US$ 5 até 10",
    "Acima de US$ 10 até 20",
    "Acima de US$ 20"
]

dados_preco = dados_filtrados.copy()
dados_preco["faixa_preco"] = pd.cut(
    dados_preco["price_final"],
    bins=[-1, 0, 5, 10, 20, float("inf")],
    labels=faixas
)

grafico_preco = px.box(
    dados_preco,
    x="faixa_preco",
    y="positive_ratio",
    category_orders={"faixa_preco": faixas},
    labels={
        "faixa_preco": "Preço final do título",
        "positive_ratio": "Avaliações positivas (%)"
    },
    title="Como a aprovação varia por faixa de preço?",
    points=False
)
st.plotly_chart(grafico_preco)
st.caption(
    "A linha dentro de cada caixa marca a aprovação mediana. "
    "Selecione “Todos” no filtro de preço para comparar as faixas."
)

st.header("Ano de lançamento e volume de avaliações")

# Os gráficos 4 e 6 usam o mesmo resumo, com uma linha por ano.
resumo_anual = dados_filtrados.groupby("year_release", as_index=False).agg(
    mediana_avaliacoes=("user_reviews", "median"),
    quantidade_titulos=("app_id", "count")
)

if ano_escolhido != "Todos os anos":
    st.caption(
        "Você selecionou um único ano. Escolha “Todos os anos” "
        "para comparar os pontos ao longo do tempo."
    )

# Gráfico 4 — Mediana de avaliações por ano de lançamento
grafico_ano = px.line(
    resumo_anual,
    x="year_release",
    y="mediana_avaliacoes",
    markers=True,
    log_y=True,
    hover_data=["quantidade_titulos"],
    labels={
        "year_release": "Ano de lançamento",
        "mediana_avaliacoes": "Mediana de avaliações por título (escala log)",
        "quantidade_titulos": "Quantidade de títulos"
    },
    title="Os títulos mais antigos acumularam mais avaliações?"
)
st.plotly_chart(grafico_ano)
st.caption(
    "Cada ponto reúne os títulos lançados naquele ano e considera as "
    "avaliações que eles haviam acumulado até a coleta."
)

# Gráfico 5 — Quantidade de avaliações e aprovação
grafico_dispersao = px.scatter(
    dados_filtrados,
    x="user_reviews",
    y="positive_ratio",
    hover_name="title",
    log_x=True,
    opacity=0.35,
    labels={
        "user_reviews": "Quantidade de avaliações (escala log)",
        "positive_ratio": "Avaliações positivas (%)"
    },
    title="Títulos com mais avaliações também têm maior aprovação?"
)
st.plotly_chart(grafico_dispersao)
st.caption(
    "Cada ponto representa um título. Pontos mais à direita receberam mais "
    "avaliações. Pontos mais altos tiveram maior porcentagem de avaliações positivas."
)

# Gráfico 6 — Quantidade de títulos por ano de lançamento
grafico_lancamentos = px.area(
    resumo_anual,
    x="year_release",
    y="quantidade_titulos",
    markers=True,
    labels={
        "year_release": "Ano de lançamento",
        "quantidade_titulos": "Quantidade de títulos na base"
    },
    title="Quais anos de lançamento concentram mais títulos na base?"
)
st.plotly_chart(grafico_lancamentos)

# As conclusões abaixo se referem aos 50.872 títulos da análise completa.
with st.expander("Principais resultados da base completa"):
    st.markdown(
        """
- **Classificações.** Positive foi a mais frequente, com 13.502 títulos,
  seguida por Very Positive, com 13.139.
- **Distribuição da aprovação.** Dos 50.872 títulos, 27.751 tiveram pelo
  menos 80% de avaliações positivas. A aprovação mediana foi de 81%.
- **Preço.** A aprovação mediana variou de 80% a 83% entre as faixas.
  Tanto os títulos com preço zero quanto os acima de US$ 20 tiveram mediana de 80%.
- **Ano e avaliações acumuladas.** Os títulos lançados em 2014 tiveram mediana
  de 118 avaliações, contra 34 nos de 2022. Os mais antigos também tiveram
  mais tempo para receber avaliações.
- **Volume e aprovação.** A correlação de Spearman entre quantidade de avaliações
  e porcentagem positiva foi de aproximadamente 0,046. Na base, a associação
  entre as duas variáveis foi muito fraca.
- **Lançamentos.** O ano mais representado foi 2022, com 7.265 títulos.
  Em 2023, a base registra 3.425 títulos.
        """
    )