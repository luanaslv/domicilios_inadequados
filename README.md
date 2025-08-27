# Análise de Domicílios Inadequados no Nordeste (2016–2019)

## **Resumo curto**

Projeto para analisar e visualizar domicílios inadequados no Nordeste (estados e regiões metropolitanas) usando dados públicos da **Fundação João Pinheiro**. Pipeline reprodutível: coleta → tratamento → padronização → modelagem relacional (MySQL) → consultas analíticas → exportação para Power BI.

## **Objetivos**

* Construir um pipeline reprodutível em Python (Pandas) para transformar planilhas públicas em CSVs padronizados.
* Modelar e carregar os dados em MySQL (XAMPP) de forma estruturada.
* Gerar consultas analíticas e exportá-las como CSVs prontos para consumo no Power BI.
* Criar dashboards que permitam comparar Nordeste, estados e metrópoles entre 2016–2019.

## **Fonte dos dados**

Dados originais: Fundação João Pinheiro — arquivo `2023.06.15_REPONDERADO0112_Dados-Inadequacao-de-Domicilios-2016-2019` (planilhas públicas).

## **Estrutura do repositório**

```
domicilios_inadequados/
├── data/
│   ├── raw/            # dados brutos (downloads das planilhas)
│   ├── processed/      # arquivos processados intermediários
│   ├── filtered/       # filtragens (estados/, metropolis/, nordeste/)
│   ├── final/          # consolidados finais (padronizados)
│   └── exports/        # CSVs resultantes das consultas (prontos para BI)
├── scripts/
│   ├── coleta/         # 01_coleta_dados.py
│   ├── tratamento/     # 02_.. 03_.. 04_padronizacao_csvs.py
│   ├── modelagem/      # 05_importa_mysql.py
│   ├── integracao/     # scripts para consolidar/exportar
│   └── analise/        # scripts que geram exports (consultas -> CSV)
├── README.md
└── requirements.txt
```

## **Formato esperado — CSVs finais**

Todos os CSVs em `data/final/` devem ter este esquema (consistente para importação automática):

```
ano,inadequacao,regiao,contagem,valor_percentual
```

* `ano`: inteiro (2016–2019)
* `inadequacao`: texto (ex.: `Abastecimento de água`)
* `regiao`: nome da localidade (estado ou região metropolitana)
* `contagem`: número absoluto (inteiro)
* `valor_percentual`: percentual como `float` (ex.: `45.8`)

## **Quickstart — pré-requisitos**

* Python 3.8+
* `pip` e virtualenv
* Bibliotecas: `pandas`, `sqlalchemy`, `pymysql` (ou `mysql-connector-python`) — ver `requirements.txt`
* MySQL (XAMPP) em execução
* (Opcional) Conta no GitHub para publicar `data/exports/infraestrutura_final.csv` e usar o link raw no Power BI

## **Instalação rápida (exemplo POSIX)**

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## **Rodando o pipeline (etapas principais)**

1. **Coleta** (baixa as planilhas via Google Sheets):

```bash
python scripts/coleta/01_coleta_dados.py
```

2. **Limpeza e padronização** (colunas, encoding):

```bash
python scripts/tratamento/02_limpeza_padronizacao.py
```

3. **Filtragem por região** (gera `data/filtered/{estados,metropolis,nordeste}`):

```bash
python scripts/tratamento/03_filtragem_regioes.py
```

4. **Padronização relacional (CSV final)** (gera `data/final/*_final.csv`):

```bash
python scripts/tratamento/04_padronizacao_csvs.py
```

5. **Criar banco e importar dados (MySQL)** — ajuste credenciais em `scripts/modelagem/05_importa_mysql.py` e execute:

```bash
python scripts/modelagem/05_importa_mysql.py
```

6. **Executar consultas de análise e exportar**:

```bash
python scripts/analise/06_exporta_consultas.py
```

## **Notas sobre MySQL / XAMPP**

* No XAMPP Control Panel, inicie o MySQL.
* Conexão padrão: `host=localhost`, `port=3306` — ajuste usuário/senha conforme sua instalação.
* Os scripts de importação criam tabelas se não existirem; para recriar do zero, execute `DROP TABLE` ou remova o banco no MySQL Workbench.

## **Exportações / Consultas (data/exports) — resumo e propósito**

Os CSVs em `data/exports/` são o produto das consultas analíticas e servem como insumo direto para o Power BI. Abaixo um resumo das exports já implementadas (com descrição curta):

* `00_anos_disponiveis_por_tabela.csv` — cobertura temporal por indicador (útil para validar anos disponíveis antes da análise).
* `01_top5_estados_2019_domicilios_inadequados.csv` — top 5 estados por contagem/% de domicílios inadequados em 2019.
* `02_top5_metropolis_2019_abastecimento.csv` — top 5 RMs do Nordeste com maior problema em abastecimento no ano de 2019.
* `03_evolucao_pernambuco_abastecimento.csv` — série temporal (2016–2019) de abastecimento para Pernambuco; usado para analisar tendências locais.
* `04_lag_variacao_por_estado_Domicílios_inadequados.csv` — variação absoluta entre 2016 e 2019 por estado (identifica aumentos/quedas maiores).
* `05_resumo_estatistico_estado_indicador.csv` — medidas descritivas (média/mediana/std) por estado e indicador para comparar dispersões.
* `06_diff_2019_2016_top50.csv` — top 50 localidades com maior variação absoluta entre 2016 e 2019 (útil para priorização).
* `07_media_estado_indicador_for_heatmap.csv` — média percentual por estado e indicador, formatado para heatmap no Power BI.
* `08_alertas_outliers.csv` — observações com z-score alto (potenciais outliers) para inspeção manual.
* `09_comparativo_estado_metropole_2019_abastecimento.csv` — comparação direta entre estados e suas metrópoles para abastecimento (2019).
* `infraestrutura_final.csv` — consolidação mestre de todos os indicadores/localidades no formato final (pronto para BI/GitHub raw).

## **Integração com Power BI**

Opções para alimentar o Power BI Desktop:

* **Manual (local)**: `Get Data` → `CSV` → selecionar `data/final/infraestrutura_final.csv` localmente.
* **Via GitHub raw** (recomendado para relatórios públicos/compartilhados): commit em `data/exports/infraestrutura_final.csv`, copie o link raw e em Power BI: `Get Data` → `Web` → cole o link.

## **Observações sobre modelagem relacional (para MySQL)**

O formato final `ano,inadequacao,regiao,contagem,valor_percentual` permite modelagem simples em uma tabela fato (fato\_inadequacao) e dimensões auxiliares (dim\_indicador, dim\_localidade) se você quiser normalizar:

* `dim_indicador(indicador_id, nome)`
* `dim_localidade(localidade_id, nome, tipo(Estado/Metropole), uf)`
* `fato_inadequacao(id, localidade_id, indicador_id, ano, contagem, valor_percentual)`

Essa modelagem facilita joins e queries performáticas para dashboards.