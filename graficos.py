from pathlib import Path

import pandas as pd
import plotly.express as px

# Lê o CSV que você acabou de gerar.
arquivo = Path(__file__).with_name("games_limpo.csv")
dados = pd.read_csv(arquivo)

# Conta quantos títulos receberam cada classificação da Steam.
contagem = dados["rating"].value_counts().reset_index()
contagem.columns = ["Classificação", "Quantidade de títulos"]

grafico = px.bar(
    contagem,
    x="Quantidade de títulos",
    y="Classificação",
    orientation="h",
    text="Quantidade de títulos",
    title="Quais classificações aparecem mais entre os títulos da Steam?"
)

grafico.update_yaxes(autorange="reversed")
grafico.show()
# Gráfico 2: distribuição da porcentagem de avaliações positivas
histograma = px.histogram(
    dados,
    x="positive_ratio",
    title="Como se distribui a aprovação dos títulos da Steam?",
    labels={"positive_ratio": "Avaliações positivas por título (%)"}
)

# Agrupa os percentuais em faixas de 10 pontos, começando em zero.
histograma.update_traces(xbins=dict(start=0, end=110, size=10))
histograma.update_xaxes(dtick=10)
histograma.update_yaxes(title_text="Quantidade de títulos")

histograma.show()

# Gráfico 3: aprovação dos títulos por faixa de preço
faixas = [
    "Preço zero",
    "Até US$ 5",
    "Acima de US$ 5 até 10",
    "Acima de US$ 10 até 20",
    "Acima de US$ 20"
]

# Agrupa os títulos pelo preço final. O zero fica em uma faixa própria.
dados["faixa_preco"] = pd.cut(
    dados["price_final"],
    bins=[-1, 0, 5, 10, 20, float("inf")],
    labels=faixas
)

grafico_preco = px.box(
    dados,
    x="faixa_preco",
    y="positive_ratio",
    category_orders={"faixa_preco": faixas},
    labels={
        "faixa_preco": "Preço final do título",
        "positive_ratio": "Avaliações positivas (%)"
    },
    title="Como a aprovação dos títulos varia por faixa de preço?",
    points=False
)

grafico_preco.show()

# Gráfico 4: quantidade de avaliações por ano de lançamento
resumo_anual = dados.groupby("year_release", as_index=False).agg(
    mediana_avaliacoes=("user_reviews", "median"),
    quantidade_titulos=("app_id", "count")
)

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
        "quantidade_titulos": "Títulos lançados nesse ano"
    },
    title="Os títulos mais antigos acumularam mais avaliações?"
)

grafico_ano.show()

# Gráfico 5: relação entre quantidade de avaliações e aprovação
grafico_dispersao = px.scatter(
    dados,
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

grafico_dispersao.show()

# Gráfico 6: quantidade de títulos da base por ano de lançamento
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

grafico_lancamentos.show()