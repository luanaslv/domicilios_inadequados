"""Esse script vai criar uma pasta dados_brutos/ com os arquivos:
-> abastecimento_agua.csv
-> esgotamento_sanitario.csv
-> coleta_lixo.csv
-> ausencia_banheiro.csv
-> piso_inadequado.csv
-> inadequacao_fundiaria.csv
-> total_inadequados.csv"""

import os
import pandas as pd

# Criar pasta para armazenar os dados brutos
os.makedirs("dados_brutos", exist_ok=True)

# ID fixo da planilha
SHEET_ID = "1CzNCJm5f4aNR3BY28FPUcaMlkKpC5MLK"

# Dicionário com os indicadores e seus respectivos GIDs
indicadores = {
    "abastecimento_agua": "904038394",
    "esgotamento_sanitario": "509586310",
    "coleta_lixo": "43770486",
    "ausencia_banheiro": "269593114",
    "piso_inadequado": "1133721675",
    "inadequacao_fundiaria": "1250915513",
    "total_inadequados": "1806311470"
}

# Loop para baixar e salvar cada indicador
for nome, gid in indicadores.items():
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"
    print(f"Baixando: {nome} ...")
    try:
        df = pd.read_csv(url)
        df.to_csv(f"dados_brutos/{nome}.csv", index=False, encoding="utf-8-sig")
        print(f"✅ {nome} salvo com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao baixar {nome}: {e}")
