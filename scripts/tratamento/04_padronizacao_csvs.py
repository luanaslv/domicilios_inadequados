import pandas as pd
from pathlib import Path

# Diretórios
filtered_dir = Path("data/filtered")
final_dir = Path("data/final")

# Pastas finais
final_dir.mkdir(parents=True, exist_ok=True)

# Categorias
categorias = ["nordeste", "estados", "metropolis"]

for cat in categorias:
    # Lista de arquivos CSV filtrados
    csv_files = list((filtered_dir / cat).glob(f"{cat}_*.csv"))
    
    if not csv_files:
        print(f"[INFO] Nenhum arquivo encontrado para {cat}, pulando...")
        continue
    
    dfs = []
    for csv_file in csv_files:
        df = pd.read_csv(csv_file, sep=",")
        
        # Padroniza coluna de percentual se existir
        if "porcentagem_em_relação_ao_total_de_domicílios_particulares_permanentes_duráveis_urbanos" in df.columns:
            df = df.rename(columns={
                "porcentagem_em_relação_ao_total_de_domicílios_particulares_permanentes_duráveis_urbanos": "valor_percentual"
            })
            df['valor_percentual'] = df['valor_percentual'].str.replace(',', '.', regex=False)\
                                                         .str.replace('%', '', regex=False)\
                                                         .astype(float)
        
        dfs.append(df)
    
    # Concatena todos os arquivos de cada categoria
    df_final = pd.concat(dfs, ignore_index=True)
    
    # Salva CSV final
    df_final.to_csv(final_dir / f"{cat}_final.csv", index=False)
    print(f"[INFO] CSV final salvo: {cat}_final.csv")