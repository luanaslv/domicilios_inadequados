# scripts/integracao/00_consolida_final_to_csv.py
import pandas as pd
from pathlib import Path
import re

BASE_DIR = Path.cwd()  # geralmente o diretório do projeto quando rodar no terminal
FINAL_DIR = BASE_DIR / "data" / "final"
EXPORTS_DIR = BASE_DIR / "data" / "exports"
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH = EXPORTS_DIR / "infraestrutura_final.csv"

# Mapeamento de possíveis nomes de coluna para padrão interno
COL_MAP = {
    "ano": "year",
    "year": "year",
    "inadequação": "indicator",
    "inadequacao": "indicator",
    "indicator": "indicator",
    "região": "region",
    "regiao": "region",
    "region": "region",
    "contagem": "count",
    "count": "count",
    "valor_percentual": "percent_value",
    "porcentagem_em_relação_ao_total_de_domicílios_particulares_permanentes_duráveis_urbanos": "percent_value",
    "percentual": "percent_value",
    "percent_value": "percent_value"
}

def normalize_colnames(df):
    cols = {c: c.strip().lower().replace(" ", "_") for c in df.columns}
    df = df.rename(columns=cols)
    # rename using COL_MAP
    rename_map = {}
    for c in df.columns:
        if c in COL_MAP:
            rename_map[c] = COL_MAP[c]
    df = df.rename(columns=rename_map)
    return df

def parse_count(x):
    if pd.isna(x):
        return None
    s = str(x).strip()
    # remove quotes and thousands separators. Try robust conversion:
    s = s.replace('"', '').replace("'", "")
    # If looks like '1.234.567' treat dots as thousands and commas as decimals
    # Replace '.' as thousands (remove), replace ',' with '.' then float
    # But if there is only a comma and no dot and comma indicates thousands like '1,234' (unlikely PT), still handle
    s = s.replace("\xa0", "")
    s = s.replace(".", "")
    s = s.replace(",", ".")
    # now try float
    try:
        f = float(s)
        if f.is_integer():
            return int(f)
        return f
    except:
        # fallback: drop non-digits
        nums = re.sub(r"[^\d]", "", s)
        if nums == "":
            return None
        return int(nums)

def parse_percent(x):
    if pd.isna(x):
        return None
    s = str(x).strip()
    s = s.replace("%", "").replace('"', '').replace("'", "")
    s = s.replace(".", "") if (s.count(".") > 1 and "," in s) else s  # guard
    s = s.replace(",", ".")
    try:
        return float(s)
    except:
        nums = re.sub(r"[^\d\.]", "", s)
        if nums == "":
            return None
        try:
            return float(nums)
        except:
            return None

def infer_indicator_from_filename(path: Path):
    name = path.stem.lower()
    # exemplos: estados_tratado_abastecimento_agua -> encontra 'abastecimento_agua'
    # tentar extrair substring após último '_' que faça sentido
    parts = name.split("_")
    # heurística: buscar palavras-chave conhecidas
    known = {
        "abastecimento": "Abastecimento de água",
        "abastecimento_agua": "Abastecimento de água",
        "esgotamento": "Esgotamento",
        "esgotamento_sanitario": "Esgotamento",
        "coleta": "Coleta de Lixo",
        "coleta_lixo": "Coleta de Lixo",
        "ausencia_banheiro": "Ausência de Banheiro",
        "piso": "Piso inadequado",
        "piso_inadequado": "Piso inadequado",
        "inadequacao": "Inadequação fundiária",
        "inadequacao_fundiaria": "Inadequação fundiária",
        "total": "Domicílios inadequados",
        "total_inadequados": "Domicílios inadequados"
    }
    for k, v in known.items():
        if k in name:
            return v
    # fallback: title case the filename
    return name.replace("_", " ").title()

def consolidate():
    csv_files = sorted(FINAL_DIR.glob("*.csv"))
    if not csv_files:
        print(f"[WARN] Nenhum CSV encontrado em {FINAL_DIR}")
        return

    dfs = []
    for p in csv_files:
        try:
            df = pd.read_csv(p, dtype=str)
        except Exception as e:
            print(f"[WARN] erro ao ler {p.name}: {e} — pulando")
            continue

        df = normalize_colnames(df)

        # map columns to standard names
        # ensure presence of key columns
        if "indicator" not in df.columns:
            # tentar usar header 'inadequacao' variants -> handled in normalize
            # se ainda não, inferir do filename
            df["indicator"] = infer_indicator_from_filename(p)

        if "year" not in df.columns and "ano" in df.columns:
            df = df.rename(columns={"ano": "year"})

        # garantir colunas
        if "region" not in df.columns:
            # tentar pegar col3
            if len(df.columns) >= 3:
                df = df.rename(columns={df.columns[2]: "region"})
            else:
                df["region"] = None

        if "count" not in df.columns:
            # tentar por posição 4
            if len(df.columns) >= 4:
                df = df.rename(columns={df.columns[3]: "count"})
            else:
                df["count"] = None

        if "percent_value" not in df.columns:
            # tentar último
            if len(df.columns) >= 5:
                df = df.rename(columns={df.columns[4]: "percent_value"})
            else:
                df["percent_value"] = None

        # limpeza de valores
        df["year"] = df["year"].astype(str).str.extract(r"(\d{4})", expand=False).astype(float).astype('Int64')

        df["count_clean"] = df["count"].apply(parse_count)
        df["percent_clean"] = df["percent_value"].apply(parse_percent)

        # tipo_inadequacao: de "indicator" (prefira valor original)
        df["tipo_inadequacao"] = df["indicator"].astype(str).str.strip()

        # mantemos colunas finais na ordem desejada
        df_final = df[["year", "tipo_inadequacao", "region", "count_clean", "percent_clean"]].copy()
        df_final = df_final.rename(columns={
            "year": "ano",
            "tipo_inadequacao": "inadequacao",
            "region": "regiao",
            "count_clean": "contagem",
            "percent_clean": "valor_percentual"
        })

        # opcional: marcar o arquivo de origem
        df_final["source_file"] = p.name

        dfs.append(df_final)

    if not dfs:
        print("[WARN] Nenhum DataFrame válido para concatenar.")
        return

    full = pd.concat(dfs, ignore_index=True)
    # ordem e tipos finais
    full["contagem"] = pd.to_numeric(full["contagem"], errors="coerce").astype("Int64")
    full["valor_percentual"] = pd.to_numeric(full["valor_percentual"], errors="coerce")
    full = full[["ano", "inadequacao", "regiao", "contagem", "valor_percentual", "source_file"]]

    full.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")
    print(f"[OK] Consolidado salvo em {OUTPUT_PATH} ({len(full)} linhas)")

if __name__ == "__main__":
    consolidate()
