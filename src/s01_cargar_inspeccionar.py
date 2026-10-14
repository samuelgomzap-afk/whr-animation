"""Paso 1: descarga (si falta) e inspección de la base original.

Genera output/inspeccion_datos.txt y output/figures/valores_faltantes.png.
"""
import io
import urllib.request

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from config import (COUNTRY, DATA_DIR, DATA_URL, FIG_DIR, KEY_VARS, OUTPUT_DIR,
                    RAW_CSV, YEAR)


def download_if_missing():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not RAW_CSV.exists():
        print(f"Descargando {DATA_URL}")
        with urllib.request.urlopen(DATA_URL, timeout=60) as r:
            RAW_CSV.write_bytes(r.read())


def load_raw():
    # utf-8-sig elimina el BOM presente al inicio del archivo original
    return pd.read_csv(RAW_CSV, encoding="utf-8-sig")


def inspect(df):
    buf = io.StringIO()
    p = lambda *a: print(*a, file=buf)
    p("INSPECCIÓN DE LA BASE ORIGINAL")
    p("=" * 60)
    p(f"Archivo: {RAW_CSV.name}")
    p(f"Observaciones (filas país-año): {len(df)}")
    p(f"Variables (columnas): {df.shape[1]}")
    p(f"Países distintos: {df[COUNTRY].nunique()}")
    p(f"Rango de años: {df[YEAR].min()}–{df[YEAR].max()}")
    p(f"Duplicados país-año: {df.duplicated([COUNTRY, YEAR]).sum()}")
    p("\nTipos de datos:")
    p(df.dtypes.astype(str).to_string())
    p("\nValores faltantes por variable (n y %):")
    na = df.isna().sum()
    p(pd.DataFrame({"faltantes": na, "pct": (100 * na / len(df)).round(2)}).to_string())
    p("\nEstadísticos descriptivos:")
    p(df.describe().T.round(3).to_string())
    p("\nPaíses observados por año:")
    p(df.groupby(YEAR).size().to_string())
    miss = df[df[KEY_VARS].isna().any(axis=1)]
    p(f"\nFilas con algún faltante en las 3 variables de la animación: {len(miss)}")
    p(miss.groupby(COUNTRY).size().sort_values(ascending=False).to_string())
    return buf.getvalue()


def plot_missing(df):
    """Mapa de observaciones: país-año observado completo / incompleto / ausente."""
    complete = df.assign(ok=df[KEY_VARS].notna().all(axis=1).map({True: 2, False: 1}))
    mat = complete.pivot(index=COUNTRY, columns=YEAR, values="ok").fillna(0)
    mat = mat.loc[mat.sum(axis=1).sort_values().index]
    fig, ax = plt.subplots(figsize=(10, 20), dpi=110)
    cmap = matplotlib.colors.ListedColormap(["#f0f0f0", "#E69F00", "#0072B2"])
    ax.imshow(mat.values, aspect="auto", cmap=cmap, vmin=0, vmax=2, interpolation="none")
    ax.set_xticks(range(mat.shape[1]), mat.columns, rotation=90, fontsize=8)
    ax.set_yticks(range(mat.shape[0]), mat.index, fontsize=5)
    ax.set_title("Disponibilidad de datos por país y año\n"
                 "azul = completo en las 3 variables · naranja = fila con faltantes · gris = país-año ausente",
                 fontsize=10)
    fig.tight_layout()
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG_DIR / "valores_faltantes.png")
    plt.close(fig)


def main():
    download_if_missing()
    df = load_raw()
    report = inspect(df)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "inspeccion_datos.txt").write_text(report, encoding="utf-8")
    plot_missing(df)
    print(report)


if __name__ == "__main__":
    main()
