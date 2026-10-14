"""Paso 2: limpieza y resumen.

Decisiones (documentadas en README y reporte):
- Se conservan solo las columnas usadas en la animación.
- Se eliminan filas país-año con faltante en X, Y o tamaño (análisis de casos
  completos por año). No se imputa ni se interpola.
- No se modifican valores observados ni se eliminan atípicos.
"""
import numpy as np
import pandas as pd

from config import CLEAN_CSV, COUNTRY, KEY_VARS, OUTPUT_DIR, X_VAR, Y_VAR, SIZE_VAR, YEAR
from s01_cargar_inspeccionar import download_if_missing, load_raw


def clean(df):
    df = df[[COUNTRY, YEAR] + KEY_VARS].copy()
    df[COUNTRY] = df[COUNTRY].str.strip()
    assert not df.duplicated([COUNTRY, YEAR]).any(), "duplicados país-año"
    return df.dropna(subset=KEY_VARS).sort_values([COUNTRY, YEAR]).reset_index(drop=True)


def yearly_summary(raw, clean_df):
    rows = []
    for y, g in clean_df.groupby(YEAR):
        r = raw[raw[YEAR] == y]
        rows.append({
            "year": y,
            "paises_en_base": len(r),
            "paises_completos": len(g),
            "paises_excluidos_por_faltantes": len(r) - len(g),
            "log_gdp_media": g[X_VAR].mean(),
            "log_gdp_mediana": g[X_VAR].median(),
            "life_ladder_media": g[Y_VAR].mean(),
            "life_ladder_mediana": g[Y_VAR].median(),
            "esperanza_vida_sana_media": g[SIZE_VAR].mean(),
            "corr_pearson_gdp_ladder": g[X_VAR].corr(g[Y_VAR]),
            "corr_spearman_gdp_ladder": g[X_VAR].rank().corr(g[Y_VAR].rank())  # Spearman sin scipy,
        })
    return pd.DataFrame(rows).round(4)


def main():
    download_if_missing()
    raw = load_raw()
    c = clean(raw)
    c.to_csv(CLEAN_CSV, index=False)
    s = yearly_summary(raw, c)
    s.to_csv(OUTPUT_DIR / "resumen_datos.csv", index=False)
    print(f"Filas originales: {len(raw)} -> limpias: {len(c)} "
          f"({len(raw) - len(c)} eliminadas); países: {c[COUNTRY].nunique()}")
    print(s.to_string(index=False))


if __name__ == "__main__":
    main()
