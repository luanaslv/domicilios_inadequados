# Análise de Domicílios Inadequados no Nordeste (2016–2019)

**Visão rápida**

Projeto para analisar e visualizar domicílios inadequados no Nordeste (estados e regiões metropolitanas) usando dados públicos da **Fundação João Pinheiro**. Pipeline reprodutível: coleta → tratamento → padronização → modelagem relacional (MySQL) → consultas analíticas → exportação para Power BI.

---

## Sumário

* [Motivação](#motivação)
* [Estrutura do repositório](#estrutura-do-repositório)
* [Formato dos dados finais](#formato-dos-dados-finais)
* [Pré-requisitos](#pré-requisitos)
* [Como rodar (quickstart)](#como-rodar-quickstart)
* [Integração com Power BI](#integração-com-power-bi)
* [Modelagem sugerida (MySQL)](#modelagem-sugerida-mysql)
* [Checklist / Lousa](#checklist--lousa)
* [Próximos passos recomendados](#próximos-passos-recomendados)
* [Licença e créditos](#licença-e-créditos)

---

## Motivação

Analisar padrões e evolução de domicílios inadequados no Nordeste (2016–2019) para apoiar visualizações e possíveis recomendações de políticas públicas.

---

## Estrutura do repositório

```
domicilios_inadequados/
├── data/
│   ├── raw/            # downloads originais (.csv exportados das planilhas)
│   ├── processed/      # processados intermediários (normalização de colunas)
│   ├── filtered/       # filtragens por escopo (estados/, metropolis/, nordeste/)
│   ├── final/          # CSVs finais padronizados (prontos para DB/BI)
│   └── exports/        # CSVs gerados pelas queries analíticas (para BI)
├── scripts/
│   ├── coleta/         # 01_coleta_dados.py
│   ├── tratamento/     # 02_.. 03_.. 04_padronizacao_csvs.py
│   ├── modelagem/      # 05_importa_mysql.py
│   ├── integracao/     # scripts de consolidação
│   └── analise/        # consultas + exportação (scripts/analise)
├── .gitignore
├── requirements.txt
├── README.md
└── LICENSE
```

---

## Formato dos dados finais

Todos os CSVs em `data/final/` devem seguir este esquema (colunas e tipos):

```
ano,inadequacao,regiao,contagem,valor_percentual
```

* `ano`: INTEGER (2016–2019)
* `inadequacao`: TEXT (ex.: `Abastecimento de água`)
* `regiao`: TEXT (estado ou nome da RM)
* `contagem`: INTEGER (número absoluto)
* `valor_percentual`: FLOAT (ex.: `45.8`)

Manter esse padrão evita erros ao criar tabelas e carregar para o MySQL ou no Power BI.

---

## Pré-requisitos

* Python 3.8+
* MySQL (XAMPP) em execução
* Recomenda-se virtualenv

Instalação das dependências:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# POSIX
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Como rodar (quickstart)

1. Coleta:

```bash
python scripts/coleta/01_coleta_dados.py
```

2. Limpeza / padronização inicial:

```bash
python scripts/tratamento/02_limpeza_padronizacao.py
```

3. Filtragem por escopo (gera `data/filtered/`):

```bash
python scripts/tratamento/03_filtragem_regioes.py
```

4. Padronização relacional (gera `data/final/*_final.csv`):

```bash
python scripts/tratamento/04_padronizacao_csvs.py
```

5. Importar para MySQL (ajuste credenciais em `scripts/modelagem/05_importa_mysql.py`):

```bash
python scripts/modelagem/05_importa_mysql.py
```

6. Gerar exports (consultas → `data/exports/`):

```bash
python scripts/analise/06_exporta_consultas.py
```

---

## Integração com Power BI

Opções para conectar dados ao Power BI Desktop:

* **Local**: `Get Data` → `Text/CSV` → selecionar `data/final/infraestrutura_final.csv`.
* **GitHub raw** (recomendado se publicar no repo): commit de `data/exports/infraestrutura_final.csv` e use o link raw no Power BI (`Get Data` → `Web`).

Se preferir automatizar a atualização, podemos criar um script que atualize o CSV no repositório via API GitHub ou servir via um endpoint simples.

---

## Modelagem sugerida (MySQL)

Para análises eficientes e escaláveis, sugerimos uma modelagem com dimensões e fato:

* `dim_indicador(indicador_id, nome)`
* `dim_localidade(localidade_id, nome, tipo, uf)`
* `fato_inadequacao(id, localidade_id, indicador_id, ano, contagem, valor_percentual)`

Vantagem: facilita joins, índices e agregações rápidas para dashboards.

---

## Checklist (Lousa) — status atual

* [x] Coleta dos dados via Google Sheets
* [x] Limpeza e padronização básica
* [x] Filtragem Nordeste / Estados / Metrópoles
* [x] Consolidação final em `data/final/`
* [x] Importação básica em MySQL (tabelas criadas)
* [x] Consultas analíticas exportadas (`data/exports/`)
* [ ] Dashboard Power BI (pendente)
* [ ] Docker (opcional: MySQL + Grafana)

---