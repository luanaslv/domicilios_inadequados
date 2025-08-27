import pandas as pd
from pathlib import Path

# Diretórios
processed_dir = Path("data/processed")
filtered_dir = Path("data/filtered")
filtered_nordeste = filtered_dir / "nordeste"
filtered_estados = filtered_dir / "estados"
filtered_metropolis = filtered_dir / "metropolis"

# Cria pastas se não existirem
for d in [filtered_nordeste, filtered_estados, filtered_metropolis]:
    d.mkdir(parents=True, exist_ok=True)

# CSVs na pasta processed
csv_files = processed_dir.glob("*.csv")

# Lista de estados do Nordeste
estados_nordeste = [
    "Maranhão", "Piauí", "Ceará", "Rio Grande do Norte", "Paraíba",
    "Pernambuco", "Alagoas", "Sergipe", "Bahia"
]

# Loop para processar cada CSV
for csv_file in csv_files:
    df = pd.read_csv(csv_file, sep=",")
    
    # Padroniza a coluna de percentual
    if "porcentagem_em_relação_ao_total_de_domicílios_particulares_permanentes_duráveis_urbanos" in df.columns:
        df = df.rename(columns={
            "porcentagem_em_relação_ao_total_de_domicílios_particulares_permanentes_duráveis_urbanos": "valor_percentual"
        })
        df['valor_percentual'] = df['valor_percentual'].str.replace(',', '.', regex=False)\
                                                     .str.replace('%', '', regex=False)\
                                                     .astype(float)
    
    # Filtra Nordeste
    df_nordeste = df[df["região"] == "Nordeste"]
    if not df_nordeste.empty:
        df_nordeste.to_csv(filtered_nordeste / f"nordeste_{csv_file.name}", index=False)
        print(f"[INFO] Nordeste salvo: nordeste_{csv_file.name}")
    
    # Filtra Estados do Nordeste
    df_estados = df[df["região"].isin(estados_nordeste)]
    if not df_estados.empty:
        df_estados.to_csv(filtered_estados / f"estados_{csv_file.name}", index=False)
        print(f"[INFO] Estados salvo: estados_{csv_file.name}")
    
    # Filtra Regiões Metropolitanas do Nordeste
    df_metropolis = df[
        df["região"].str.contains("Região Metropolitana", na=False) &
        df["região"].str.contains(
            "|".join([
                "Maranhão", "São Luís",  
                "Piauí", "Teresina",     
                "Ceará", "Fortaleza",
                "Rio Grande do Norte", "Natal",
                "Paraíba", "João Pessoa",
                "Pernambuco", "Recife",
                "Alagoas", "Maceió",
                "Sergipe", "Aracaju",
                "Bahia", "Salvador"
            ]),
            na=False
        )
    ]
    if not df_metropolis.empty:
        df_metropolis.to_csv(filtered_metropolis / f"metropolis_{csv_file.name}", index=False)
        print(f"[INFO] Metropolis salvo (Nordeste): metropolis_{csv_file.name}")
