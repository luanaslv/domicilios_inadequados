'''O que esse script faz:
-> Conecta ao MySQL (infraestrutura_nordeste).
-> Cria as tabelas estados, metropolis e nordeste somente se não existirem.
-> Importa os CSVs finais de cada pasta para a tabela correspondente.'''

import pandas as pd
import mysql.connector
from pathlib import Path

# Configurações de conexão
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Coloque sua senha do MySQL
    'database': 'infraestrutura_nordeste'
}

# Pastas com os CSVs finais
CSV_DIRS = {
    'estados': Path("data/final/estados_final.csv"),
    'metropolis': Path("data/final/metropolis_final.csv"),
    'nordeste': Path("data/final/nordeste_final.csv")
}

# Estrutura das tabelas
TABLE_SCHEMAS = {
    'estados': """
        CREATE TABLE IF NOT EXISTS estados (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ano INT NOT NULL,
            inadequacao VARCHAR(255) NOT NULL,
            regiao VARCHAR(255) NOT NULL,
            contagem BIGINT NOT NULL,
            valor_percentual FLOAT NOT NULL
        );
    """,
    'metropolis': """
        CREATE TABLE IF NOT EXISTS metropolis (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ano INT NOT NULL,
            inadequacao VARCHAR(255) NOT NULL,
            regiao VARCHAR(255) NOT NULL,
            contagem BIGINT NOT NULL,
            valor_percentual FLOAT NOT NULL
        );
    """,
    'nordeste': """
        CREATE TABLE IF NOT EXISTS nordeste (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ano INT NOT NULL,
            inadequacao VARCHAR(255) NOT NULL,
            regiao VARCHAR(255) NOT NULL,
            contagem BIGINT NOT NULL,
            valor_percentual FLOAT NOT NULL
        );
    """
}

# Conexão com o banco
conn = mysql.connector.connect(**DB_CONFIG)
cursor = conn.cursor()

# Criação das tabelas
for table_name, schema in TABLE_SCHEMAS.items():
    cursor.execute(schema)
    print(f"[INFO] Tabela '{table_name}' criada ou já existente.")

# Função para importar CSV
def importa_csv_para_mysql(csv_path, table_name):
    df = pd.read_csv(csv_path)
    # Substitui vírgula por ponto no valor percentual e converte para float
    df['valor_percentual'] = df['valor_percentual'].astype(str).str.replace(',', '.').astype(float)

    for _, row in df.iterrows():
        cursor.execute(f"""
            INSERT INTO {table_name} (ano, inadequacao, regiao, contagem, valor_percentual)
            VALUES (%s, %s, %s, %s, %s)
        """, (row['ano'], row['inadequação'], row['região'], row['contagem'], row['valor_percentual']))
    
    conn.commit()
    print(f"[INFO] CSV '{csv_path.name}' importado para tabela '{table_name}'.")

# Importa todos os CSVs
for table_name, csv_path in CSV_DIRS.items():
    if csv_path.exists():
        importa_csv_para_mysql(csv_path, table_name)
    else:
        print(f"[WARN] CSV não encontrado: {csv_path}")

# Fecha conexão
cursor.close()
conn.close()
print("[INFO] Processo concluído!")