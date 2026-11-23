from pathlib import Path

import pandas as pd


# O CSV deve ficar na mesma pasta deste script para que a leitura e a
# gravação funcionem sem depender do diretorio de onde o script e executado.
arquivo = Path(__file__).with_name("games.csv")
dados = pd.read_csv(arquivo)

# Inspecao inicial: dimensoes, tipos, ausencias e duplicatas ajudam a
# identificar problemas antes de decidir como tratar cada coluna.
print("Dimensoes:", dados.shape)
print("\nTipos de dados:")
print(dados.dtypes)
print("\nValores ausentes:")
print(dados.isna().sum())
print("\nLinhas totalmente duplicadas:", dados.duplicated().sum())
print("\nPrimeiras linhas:")
print(dados.head())

# Remove espacos dos nomes para evitar diferencas causadas por espacos
# acidentais no cabecalho.
dados.columns = dados.columns.str.strip()

# Titulo e classificacao sao texto. Remover espacos e converter texto vazio
# em ausente evita tratar um campo em branco como um valor valido.
for coluna in ["title", "rating"]:
    dados[coluna] = dados[coluna].astype("string").str.strip()
    dados[coluna] = dados[coluna].replace("", pd.NA)

# IDs, avaliacoes, proporcoes e precos devem ser numericos para permitir
# comparacoes e calculos. Valores que nao puderem ser convertidos viram
# ausentes, em vez de receberem um numero inventado.
for coluna in [
    "app_id",
    "user_reviews",
    "positive_ratio",
    "price_final",
    "price_original",
    "discount",
]:
    dados[coluna] = pd.to_numeric(dados[coluna], errors="coerce")

# A data e convertida para permitir extrair o ano. Datas invalidas ficam
# ausentes, pois nao ha informacao suficiente para corrigi-las.
dados["date_release"] = pd.to_datetime(dados["date_release"], errors="coerce")

# Registra IDs repetidos antes da remocao para documentar a inspecao.
print("IDs de jogos duplicados:", dados["app_id"].duplicated().sum())

# Remove linhas identicas. Sem ID ou titulo, o registro nao pode ser
# identificado nem interpretado como um jogo, por isso essas linhas saem.
dados = dados.drop_duplicates()
dados = dados.dropna(subset=["app_id", "title"])

# O identificador de jogo e inteiro; o tipo anulavel preserva eventuais
# ausencias nas demais linhas sem converter a coluna para numero decimal.
dados["app_id"] = dados["app_id"].astype("Int64")

# Se um mesmo jogo aparecer mais de uma vez com dados diferentes, mantem-se
# a primeira ocorrencia para nao contar o mesmo app_id como jogos distintos.
dados = dados.drop_duplicates(subset="app_id")

# O ano de lancamento facilita a analise temporal.
dados["year_release"] = dados["date_release"].dt.year.astype("Int64")

print("\nDimensoes apos o tratamento:", dados.shape)
print("\nValores ausentes apos o tratamento:")
print(dados.isna().sum())

# A coluna rating mostra a classificacao textual da Steam. Sua frequencia
# ajuda a entender como as avaliacoes se distribuem entre os jogos.
print("\nQuantidade de jogos por classificacao:")
print(dados["rating"].value_counts(dropna=False))

# Spearman compara a ordem dos valores e e adequado para investigar
# associacoes sem supor uma relacao linear. O calculo usa pares disponiveis;
# os resultados indicam associacao, nao que uma variavel cause a outra.
variaveis = [
    "price_final",
    "year_release",
    "user_reviews",
    "positive_ratio",
]
print("\nCorrelacao de Spearman entre preco, ano, avaliacoes e proporcao positiva:")
print(dados[variaveis].corr(method="spearman"))

# Ausencias em colunas como preco ou avaliacao sao preservadas: sem uma fonte
# confiavel, preencher esses dados poderia introduzir informacao incorreta.
saida = arquivo.with_name("games_limpo.csv")
dados.to_csv(saida, index=False, encoding="utf-8")
print("\nArquivo tratado salvo em:", saida)
