import os
import pandas as pd

# Descobre o diretório da raiz do projeto (2 níveis acima do script atual)
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

# Define pastas de entrada e saída
RAW_DIR = os.path.join(ROOT_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(ROOT_DIR, "data", "processed")

# Cria pasta processed caso não exista
os.makedirs(PROCESSED_DIR, exist_ok=True)

def tratar_csv(nome_arquivo):
    """Carrega, trata e salva um CSV específico"""
    caminho_entrada = os.path.join(RAW_DIR, nome_arquivo)
    caminho_saida = os.path.join(PROCESSED_DIR, f"tratado_{nome_arquivo}")

    print(f"\n[INFO] Lendo {caminho_entrada}...")
    df = pd.read_csv(caminho_entrada)

    # Exemplo de padronização 
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # Salva o arquivo tratado
    df.to_csv(caminho_saida, index=False, encoding="utf-8")
    print(f"[INFO] Arquivo tratado salvo em {caminho_saida}")

if __name__ == "__main__":
    arquivos = arquivos = [
    "abastecimento_agua.csv",
    "ausencia_banheiro.csv",
    "coleta_lixo.csv",
    "esgotamento_sanitario.csv",
    "inadequacao_fundiaria.csv",
    "piso_inadequado.csv",
    "total_inadequados.csv",
]

    for arquivo in arquivos:
        tratar_csv(arquivo)