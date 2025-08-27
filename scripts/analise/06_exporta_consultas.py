# scripts/analise/06_exporta_consultas.py
"""
Executa queries analíticas no banco MySQL e exporta resultados para CSV.
Ajustes:
 - Atualize DB_CONFIG com host/user/password/database corretos.
 - Os CSVs serão salvos em data/exports/.
"""

import os
from pathlib import Path
import pandas as pd
import mysql.connector
from mysql.connector import Error

# ------------- CONFIG -------------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",              # <-- ajuste se necessário
    "database": "infraestrutura_nordeste"  # <-- ajuste se necessário
}

OUTPUT_DIR = Path("data/exports")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Parâmetros de análise (mude se quiser)
ANALYSIS_YEAR = 2019
TOP_N = 5
INDICADOR_DOMICILIOS = "Domicílios inadequados"
INDICADOR_ABAST = "Abastecimento de água"
# -----------------------------------

def connect():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            print("[INFO] Conectado ao MySQL.")
            return conn
    except Error as e:
        print(f"[ERROR] Falha na conexão: {e}")
        raise

def run_and_save(df_query, filename):
    out_path = OUTPUT_DIR / filename
    df_query.to_csv(out_path, index=False, encoding="utf-8")
    print(f"[OK] Salvo: {out_path}")

def main():
    conn = connect()
    try:
        # Use pandas.read_sql_query que aceita conexões DB-API
        # 0) Verificação de anos disponíveis (rápida)
        q0 = """
        SELECT 'estados' AS tabela, MIN(ano) AS ano_min, MAX(ano) AS ano_max FROM estados
        UNION ALL
        SELECT 'metropolis', MIN(ano), MAX(ano) FROM metropolis
        UNION ALL
        SELECT 'nordeste', MIN(ano), MAX(ano) FROM nordeste;
        """
        df0 = pd.read_sql_query(q0, conn)
        run_and_save(df0, "00_anos_disponiveis_por_tabela.csv")

        # 1) Top N por ano e indicador — Estados (ex.: Domicílios inadequados)
        q1 = """
        SELECT
          ano,
          inadequacao,
          regiao AS estado,
          contagem,
          valor_percentual
        FROM estados
        WHERE ano = %s
          AND inadequacao = %s
        ORDER BY valor_percentual DESC
        LIMIT %s;
        """
        df1 = pd.read_sql_query(q1, conn, params=(ANALYSIS_YEAR, INDICADOR_DOMICILIOS, int(TOP_N)))
        run_and_save(df1, f"01_top{TOP_N}_estados_{ANALYSIS_YEAR}_domicilios_inadequados.csv")

        # 1b) Top N por ano e indicador — Metropolis (ex.: Abastecimento de água)
        q1b = """
        SELECT
          ano,
          inadequacao,
          regiao AS metropole,
          contagem,
          valor_percentual
        FROM metropolis
        WHERE ano = %s
          AND inadequacao = %s
        ORDER BY valor_percentual DESC
        LIMIT %s;
        """
        df1b = pd.read_sql_query(q1b, conn, params=(ANALYSIS_YEAR, INDICADOR_ABAST, int(TOP_N)))
        run_and_save(df1b, f"02_top{TOP_N}_metropolis_{ANALYSIS_YEAR}_abastecimento.csv")

        # 2) Evolução temporal por localidade e indicador (ex.: Pernambuco, Abastecimento)
        q2 = """
        SELECT ano, valor_percentual
        FROM estados
        WHERE regiao = %s
          AND inadequacao = %s
        ORDER BY ano;
        """
        df2 = pd.read_sql_query(q2, conn, params=("Pernambuco", INDICADOR_ABAST))
        run_and_save(df2, "03_evolucao_pernambuco_abastecimento.csv")

        # 3) Variação ano-a-ano (LAG) por estado e indicador
        # Observação: funções de janela requerem MySQL 8+
        q3 = """
        SELECT
          regiao AS estado,
          inadequacao,
          ano,
          valor_percentual,
          LAG(valor_percentual) OVER (PARTITION BY regiao, inadequacao ORDER BY ano) AS valor_ano_anterior,
          (valor_percentual - LAG(valor_percentual) OVER (PARTITION BY regiao, inadequacao ORDER BY ano)) AS diff_pct_points
        FROM estados
        WHERE inadequacao = %s
        ORDER BY regiao, ano;
        """
        df3 = pd.read_sql_query(q3, conn, params=(INDICADOR_DOMICILIOS,))
        run_and_save(df3, f"04_lag_variacao_por_estado_{INDICADOR_DOMICILIOS.replace(' ','_')}.csv")

        # 4) Resumo estatístico (média, desvio) por estado/indicador
        q4 = """
        SELECT
          regiao AS estado,
          inadequacao,
          ROUND(AVG(valor_percentual),2) AS media_pct,
          ROUND(STDDEV_SAMP(valor_percentual),2) AS stddev_pct,
          MIN(valor_percentual) AS min_pct,
          MAX(valor_percentual) AS max_pct
        FROM estados
        GROUP BY regiao, inadequacao
        ORDER BY inadequacao, media_pct DESC;
        """
        df4 = pd.read_sql_query(q4, conn)
        run_and_save(df4, "05_resumo_estatistico_estado_indicador.csv")

        # 5) Maior variação entre 2016 e 2019 (por estado e indicador)
        q5 = """
        SELECT
          a.inadequacao,
          a.regiao AS estado,
          a.valor_percentual AS pct_2016,
          b.valor_percentual AS pct_2019,
          ROUND(b.valor_percentual - a.valor_percentual,2) AS diff_2019_2016
        FROM
          (SELECT regiao, inadequacao, valor_percentual FROM estados WHERE ano = 2016) a
        JOIN
          (SELECT regiao, inadequacao, valor_percentual FROM estados WHERE ano = 2019) b
          ON a.regiao = b.regiao AND a.inadequacao = b.inadequacao
        ORDER BY diff_2019_2016 DESC
        LIMIT 50;
        """
        df5 = pd.read_sql_query(q5, conn)
        run_and_save(df5, "06_diff_2019_2016_top50.csv")

        # 6) Pivot-like: média percentual por estado x indicador (export para heatmap)
        q6 = """
        SELECT
          regiao AS estado,
          inadequacao AS indicador,
          ROUND(AVG(valor_percentual),2) AS media_pct
        FROM estados
        GROUP BY regiao, inadequacao
        ORDER BY indicador, media_pct DESC;
        """
        df6 = pd.read_sql_query(q6, conn)
        run_and_save(df6, "07_media_estado_indicador_for_heatmap.csv")

        # 7) Alertas: valores recentes > media + 2*sd
        q7 = """
        WITH stats AS (
          SELECT
            regiao,
            inadequacao,
            AVG(valor_percentual) AS media,
            STDDEV_SAMP(valor_percentual) AS sd
          FROM estados
          GROUP BY regiao, inadequacao
        ),
        latest AS (
          SELECT s.regiao, s.inadequacao, s.valor_percentual
          FROM estados s
          JOIN (
            SELECT regiao, inadequacao, MAX(ano) AS max_ano FROM estados GROUP BY regiao, inadequacao
          ) lm ON s.regiao = lm.regiao AND s.inadequacao = lm.inadequacao AND s.ano = lm.max_ano
        )
        SELECT
          l.regiao,
          l.inadequacao,
          l.valor_percentual AS atual,
          ROUND(st.media,2) AS media_historica,
          ROUND(st.sd,2) AS sd_historica,
          ROUND((l.valor_percentual - st.media),2) AS diff_from_mean
        FROM latest l
        JOIN stats st ON l.regiao = st.regiao AND l.inadequacao = st.inadequacao
        WHERE l.valor_percentual > st.media + 2 * st.sd
        ORDER BY diff_from_mean DESC;
        """
        df7 = pd.read_sql_query(q7, conn)
        run_and_save(df7, "08_alertas_outliers.csv")

        # 8) Comparativo Estados x Metropolis (mesmo indicador/ano) — exemplo Abastecimento de água / 2019
        q8 = f"""
        SELECT
          e.ano,
          e.inadequacao,
          e.regiao AS estado,
          e.valor_percentual AS pct_estado,
          m.regiao AS metropole,
          m.valor_percentual AS pct_metropole,
          ROUND(m.valor_percentual - e.valor_percentual,2) AS diff_metropole_minus_estado
        FROM estados e
        LEFT JOIN metropolis m
          ON e.inadequacao = m.inadequacao AND e.ano = m.ano
        WHERE e.ano = %s
          AND e.inadequacao = %s
        ORDER BY diff_metropole_minus_estado DESC
        LIMIT 100;
        """
        df8 = pd.read_sql_query(q8, conn, params=(ANALYSIS_YEAR, INDICADOR_ABAST))
        run_and_save(df8, f"09_comparativo_estado_metropole_{ANALYSIS_YEAR}_abastecimento.csv")

        print("[ALL] Todas as consultas executadas e exportadas.")
    except Exception as e:
        print(f"[ERROR] Durante execução das queries: {e}")
    finally:
        if conn:
            conn.close()
            print("[INFO] Conexão fechada.")

if __name__ == "__main__":
    main()