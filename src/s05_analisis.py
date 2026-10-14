"""Paso 5: análisis descriptivo complementario y generación del reporte.

La pregunta es temporal (¿la evolución del ingreso se acompaña de cambios en el
bienestar?), así que además de la correlación entre países en cada año se
calculan cambios DENTRO de cada país. Todo es descriptivo: no se estiman
efectos causales.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from config import (CLEAN_CSV, COUNTRY, FIG_DIR, HIGHLIGHT, LABELS_ES, OUTPUT_DIR,
                    SIZE_VAR, X_VAR, Y_VAR, YEAR)

MIN_SPAN = 8  # años mínimos entre primera y última observación para comparar cambios


def country_changes(df):
    rows = []
    for c, g in df.sort_values(YEAR).groupby(COUNTRY):
        if len(g) < 2:
            continue
        a, b = g.iloc[0], g.iloc[-1]
        rows.append({COUNTRY: c, "anio_ini": int(a[YEAR]), "anio_fin": int(b[YEAR]),
                     "n_obs": len(g), "span": int(b[YEAR] - a[YEAR]),
                     "d_log_gdp": b[X_VAR] - a[X_VAR], "d_ladder": b[Y_VAR] - a[Y_VAR],
                     "d_hle": b[SIZE_VAR] - a[SIZE_VAR]})
    return pd.DataFrame(rows)


def within_corr(df):
    """Correlación agrupada de desviaciones respecto a la media de cada país."""
    d = df.copy()
    for v in (X_VAR, Y_VAR):
        d[v] = d[v] - d.groupby(COUNTRY)[v].transform("mean")
    return d[X_VAR].corr(d[Y_VAR])


def plot_changes(ch):
    fig, ax = plt.subplots(figsize=(10, 7), dpi=130)
    ax.axhline(0, color="#999", lw=0.8)
    ax.axvline(0, color="#999", lw=0.8)
    other = ch[~ch[COUNTRY].isin(HIGHLIGHT)]
    ax.scatter(other["d_log_gdp"], other["d_ladder"], c="#9AA3AD", alpha=0.7, s=28,
               edgecolors="white", linewidths=0.5)
    for c, col in HIGHLIGHT.items():
        r = ch[ch[COUNTRY] == c]
        if r.empty:
            continue
        ax.scatter(r["d_log_gdp"], r["d_ladder"], c=col, s=55, edgecolors="white", zorder=3)
        ax.annotate(LABELS_ES[c], (r["d_log_gdp"].iloc[0], r["d_ladder"].iloc[0]),
                    xytext={"Denmark": (-8, -14)}.get(c, (5, 4)), textcoords="offset points",
                    ha="right" if c == "Denmark" else "left", color=col, fontsize=9, fontweight="bold")
    rr = ch["d_log_gdp"].corr(ch["d_ladder"])
    ax.set_xlabel("Cambio en Log GDP per capita (última − primera observación)")
    ax.set_ylabel("Cambio en Life Ladder (última − primera observación)")
    ax.set_title(f"Cambios dentro de cada país (n = {len(ch)}, ≥{MIN_SPAN} años entre observaciones)\n"
                 f"r = {rr:.2f} · asociación descriptiva, no causal", fontsize=11)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "cambios_gdp_vs_ladder.png")
    plt.close(fig)


def main():
    df = pd.read_csv(CLEAN_CSV)
    ch = country_changes(df)
    ch_long = ch[ch["span"] >= MIN_SPAN].copy()
    ch_long.round(4).to_csv(OUTPUT_DIR / "cambios_por_pais.csv", index=False)
    plot_changes(ch_long)

    # Panel balanceado 2008 vs 2019 para separar composición de evolución
    both = set(df[df[YEAR] == 2008][COUNTRY]) & set(df[df[YEAR] == 2019][COUNTRY])
    bal = df[df[COUNTRY].isin(both) & df[YEAR].isin([2008, 2019])]
    bal_means = bal.groupby(YEAR)[[X_VAR, Y_VAR, SIZE_VAR]].mean()

    s = {
        "n_cambios": len(ch_long),
        "r_cambios": ch_long["d_log_gdp"].corr(ch_long["d_ladder"]),
        "rho_cambios": ch_long["d_log_gdp"].rank().corr(ch_long["d_ladder"].rank()),
        "pct_gdp_sube": 100 * (ch_long["d_log_gdp"] > 0).mean(),
        "pct_ladder_sube": 100 * (ch_long["d_ladder"] > 0).mean(),
        "pct_gdp_sube_ladder_baja": 100 * ((ch_long["d_log_gdp"] > 0) & (ch_long["d_ladder"] < 0)).mean(),
        "pct_gdp_baja_ladder_sube": 100 * ((ch_long["d_log_gdp"] < 0) & (ch_long["d_ladder"] > 0)).mean(),
        "r_within": within_corr(df),
        "r_pooled": df[X_VAR].corr(df[Y_VAR]),
        "n_bal": len(both),
        "bal": bal_means,
    }
    resumen = pd.read_csv(OUTPUT_DIR / "resumen_datos.csv")
    hl = ch[ch[COUNTRY].isin(HIGHLIGHT)].set_index(COUNTRY)
    write_report(df, resumen, s, hl)
    print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in s.items() if k != "bal"})
    print(bal_means.round(3))


def write_report(df, resumen, s, hl):
    raw = pd.read_csv(CLEAN_CSV.parent / "world-happiness-report.csv", encoding="utf-8-sig")
    na = raw.isna().sum()
    na_tbl = "\n".join(f"| {c} | {int(na[c])} | {100 * na[c] / len(raw):.1f}% |" for c in raw.columns)
    yr_tbl = "\n".join(
        f"| {int(r.year)} | {int(r.paises_en_base)} | {int(r.paises_completos)} | {r.life_ladder_mediana:.2f} | "
        f"{r.log_gdp_mediana:.2f} | {r.corr_pearson_gdp_ladder:.2f} |" for r in resumen.itertuples())
    hl_tbl = "\n".join(
        f"| {LABELS_ES[c]} | {int(r.anio_ini)}–{int(r.anio_fin)} | {r.d_log_gdp:+.2f} | {r.d_ladder:+.2f} | {r.d_hle:+.1f} |"
        for c, r in hl.loc[[c for c in HIGHLIGHT if c in hl.index]].iterrows())
    b = s["bal"]
    rmin, rmax = resumen.corr_pearson_gdp_ladder.min(), resumen.corr_pearson_gdp_ladder.max()
    excl = len(raw) - len(df)
    md = f"""# Reporte de análisis: ingreso y bienestar subjetivo (World Happiness Report)

*Documento generado automáticamente por `src/s05_analisis.py`.*

## Pregunta

¿La evolución del ingreso de los países a través del tiempo está acompañada por cambios en sus niveles de bienestar?

Variables usadas (todas existen en la base; no se crearon variables nuevas para la visualización):

| Rol | Variable |
|---|---|
| Eje X | `Log GDP per capita` |
| Eje Y | `Life Ladder` (escalera de Cantril, 0–10) |
| Tamaño | `Healthy life expectancy at birth` |
| Etiqueta | `Country name` |
| Tiempo | `year` |

El eje superior del video muestra `exp(Log GDP per capita)` solo como ayuda de lectura del eje X (misma variable, otra escala).

## 1. Estructura de la base

- Observaciones (filas país-año): **{len(raw)}**
- Países distintos: **{raw[COUNTRY].nunique()}**
- Rango de años: **{raw[YEAR].min()}–{raw[YEAR].max()}** ({raw[YEAR].nunique()} años)
- Variables: **{raw.shape[1]}** — `Country name` (texto), `year` (entero) y 9 variables numéricas (float).
- Duplicados país-año: {int(raw.duplicated([COUNTRY, YEAR]).sum())}
- Panel **no balanceado**: la cantidad de países varía entre {int(resumen.paises_en_base.min())} (2005) y {int(resumen.paises_en_base.max())} por año.

### Valores faltantes (base original)

| Variable | Faltantes | % |
|---|---|---|
{na_tbl}

Además de las celdas vacías hay **faltantes implícitos**: combinaciones país-año que no aparecen en la base (ver `output/figures/valores_faltantes.png`).

## 2. Decisiones de limpieza

1. Lectura con codificación `utf-8-sig` para eliminar el BOM del encabezado.
2. Se conservan solo las cinco columnas necesarias.
3. **Casos completos por año**: se excluyen {excl} filas país-año con faltante en X, Y o tamaño. Quedan **{len(df)} filas** y **{df[COUNTRY].nunique()} países**.
   Los países sin `Log GDP per capita` ni `Healthy life expectancy` en ningún año (North Cyprus, Somaliland region) desaparecen por completo; otros (Kosovo, Hong Kong, Taiwan, Palestinian Territories) se pierden porque les falta la esperanza de vida sana.
4. **No se imputa ni se interpola**. Rellenar con medias o interpolar entre años inventaría trayectorias que no se observaron, justo lo que el video pretende mostrar. Si un país resaltado no tiene dato en un año, el video lo marca como "último dato: AAAA" en vez de inventar su posición.
5. No se eliminan atípicos ni se modifican valores observados.

## 3. Resumen por año (casos completos)

| Año | Países en base | Países completos | Mediana Life Ladder | Mediana Log GDP | r (Pearson) GDP–Ladder |
|---|---|---|---|---|---|
{yr_tbl}

Tabla completa en `output/resumen_datos.csv`.

## 4. Hallazgos descriptivos

**Entre países (cada año):** la asociación entre ingreso y bienestar es positiva y estable: r de Pearson entre {rmin:.2f} y {rmax:.2f}. Los países con mayor ingreso tienden a reportar mayor bienestar y mayor esperanza de vida sana. Considerando todos los países-año juntos, r = {s['r_pooled']:.2f}.

**Dentro de cada país (a través del tiempo)**, que es lo que plantea la pregunta, la relación es bastante más débil:

- Correlación de las desviaciones respecto a la media de cada país (variación "within"): r = {s['r_within']:.2f}.
- Para {s['n_cambios']} países con al menos {MIN_SPAN} años entre su primera y última observación, la correlación entre el cambio en Log GDP y el cambio en Life Ladder es r = {s['r_cambios']:.2f} (Spearman ρ = {s['rho_cambios']:.2f}). Ver `output/figures/cambios_gdp_vs_ladder.png` y `output/cambios_por_pais.csv`.
- En ese grupo, el ingreso subió en el {s['pct_gdp_sube']:.0f}% de los países, pero el bienestar subió solo en el {s['pct_ladder_sube']:.0f}%. En un {s['pct_gdp_sube_ladder_baja']:.0f}% el ingreso subió y el bienestar bajó; en un {s['pct_gdp_baja_ladder_sube']:.0f}% ocurrió lo contrario.
- **Panel balanceado** ({s['n_bal']} países presentes en 2008 y 2019): media de Log GDP {b.loc[2008, X_VAR]:.2f} → {b.loc[2019, X_VAR]:.2f}; media de Life Ladder {b.loc[2008, Y_VAR]:.2f} → {b.loc[2019, Y_VAR]:.2f}; esperanza de vida sana {b.loc[2008, SIZE_VAR]:.1f} → {b.loc[2019, SIZE_VAR]:.1f} años.

Países resaltados en el video (primera vs. última observación con datos completos):

| País | Periodo | Δ Log GDP | Δ Life Ladder | Δ Esperanza vida sana |
|---|---|---|---|---|
{hl_tbl}

Ejemplos: China e India aumentaron su ingreso de forma marcada, pero en China el bienestar también subió y en India bajó. Afganistán y Zimbabue aumentaron levemente su ingreso y su bienestar bajó; Venezuela redujo ambos hasta 2017, su último año con datos completos. Dinamarca y Estados Unidos se mantienen en la zona alta, con poco cambio de ingreso y un leve descenso de bienestar. La esperanza de vida sana aumentó en casi todos los países resaltados.

**Respuesta a la pregunta (descriptiva):** en la comparación entre países, mayor ingreso se asocia con mayor bienestar en todos los años. Pero la evolución del ingreso *dentro* de un país no se acompaña de forma consistente de cambios en el mismo sentido en su bienestar: la asociación de los cambios es positiva pero moderada (r ≈ {s["r_cambios"]:.2f}) y en cerca de {s["pct_gdp_sube_ladder_baja"]:.0f}% de los países el ingreso subió mientras el bienestar bajó. Estos resultados son asociaciones; **no permiten concluir que el ingreso cause bienestar** (ni lo contrario). Pueden influir otros factores (conflictos, crisis políticas, instituciones, salud, apoyo social) que no se modelan aquí.

## 5. Revisión crítica de la visualización

| Aspecto | Evaluación y medida tomada |
|---|---|
| Claridad visual | Puntos grises translúcidos para el contexto y 8 países resaltados con colores Okabe-Ito (aptos para daltonismo). |
| Consistencia de escalas | Límites de ejes fijos para todo el video (X: 6–12; Y: 2–8.5), calculados sobre todos los años. La escala de tamaño también es fija. |
| Legibilidad | 1920×1080, texto ≥10 pt, año en grande en el panel derecho y como marca de agua tenue. |
| Saturación de etiquetas | Solo se etiquetan 8 países; el resto queda sin etiqueta. Las etiquetas tienen fondo blanco semitransparente. |
| Seguimiento de países | Estelas acumuladas para los países resaltados; los saltos sobre años sin dato se dibujan punteados. |
| Valores faltantes | Sin imputación; el número de países con datos se muestra en cada fotograma; aviso "muestra reducida" cuando hay menos de 100 países. |
| Velocidad | Un fotograma por año, 2 s por año y 3 s más en el último año (35 s en total). No se interpola entre años, así que el movimiento es por saltos; las estelas compensan. |
| Riesgos de interpretación | (a) El cambio de composición de la muestra (2005: 27 países, casi todos de ingreso alto; 2020: 88) puede parecer una mejora o un empeoramiento general; se advierte en el video. (b) El área de los círculos es proporcional a (años − 30), no a los años, para que las diferencias se vean; se indica en la leyenda. (c) La correlación mostrada es entre países y no describe la evolución de cada país. (d) Ninguna relación mostrada es causal. |

Durante el desarrollo, la revisión de los fotogramas llevó a estas correcciones: la nota al pie se cortaba y se superponía a la etiqueta del eje X; el rango del eje Y dejaba espacio vacío (2–9 → 2–8.5); las estelas unían años no consecutivos como si fueran continuos (ahora se dibujan punteados); la etiqueta de los países sin dato era demasiado larga; y el aviso de muestra reducida se superponía al conteo.

## 6. Limitaciones

- Panel no balanceado y faltantes no aleatorios: los países sin datos suelen ser de bajo ingreso o estar en conflicto, así que los resultados pueden estar sesgados hacia países con mejor información estadística.
- 2005 y 2020 tienen muestras pequeñas y distintas; 2020 coincide con la pandemia de COVID-19.
- `Life Ladder` es una medida autoreportada basada en encuestas (Gallup World Poll) con error muestral; los cambios anuales pequeños pueden ser ruido.
- Las variables de ingreso y de esperanza de vida sana provienen de fuentes externas y pueden estar revisadas o extrapoladas por los productores del WHR.
- El análisis es descriptivo: no controla otras variables ni identifica efectos causales.
- La selección de los 8 países resaltados es una decisión de diseño (diversidad de ingreso, región y trayectoria); otros países podrían mostrar patrones distintos.
"""
    (OUTPUT_DIR / "reporte_analisis.md").write_text(md, encoding="utf-8")


if __name__ == "__main__":
    main()
