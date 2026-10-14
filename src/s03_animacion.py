"""Paso 3: genera un fotograma PNG por año y los une en output/video_final.mp4.

Cada imagen representa exactamente un año observado (sin interpolación entre
años). Para que el video sea legible, cada imagen se mantiene en pantalla
SECONDS_PER_YEAR segundos (se repite a VIDEO_FPS cuadros por segundo).
"""
import shutil
import subprocess

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

from config import (CLEAN_CSV, COUNTRY, DPI, FINAL_HOLD_SECONDS, FIG_DIR, FRAMES_DIR,
                    HEIGHT_PX, HIGHLIGHT, LABELS_ES, SECONDS_PER_YEAR, SIZE_VAR,
                    VIDEO_FPS, VIDEO_PATH, WIDTH_PX, X_VAR, Y_VAR, YEAR)

# Escala de tamaño: área del círculo lineal en (años - SIZE_BASE). La base no es
# cero para que las diferencias sean visibles; se indica en la leyenda.
SIZE_BASE, SIZE_MAX_VAL, SIZE_MAX_PT = 30.0, 80.0, 750.0
SMALL_SAMPLE = 100  # umbral para advertir muestra reducida
GREY = "#9AA3AD"
INK = "#1F2933"


def size_of(v):
    return 12 + SIZE_MAX_PT * np.clip((np.asarray(v) - SIZE_BASE) / (SIZE_MAX_VAL - SIZE_BASE), 0, None)


def axis_limits(df):
    """Límites fijos para todo el video, calculados sobre todos los años."""
    pad_x = 0.03 * (df[X_VAR].max() - df[X_VAR].min())
    pad_y = 0.05 * (df[Y_VAR].max() - df[Y_VAR].min())
    xl = (np.floor((df[X_VAR].min() - pad_x) * 2) / 2, np.ceil((df[X_VAR].max() + pad_x) * 2) / 2)
    yl = (np.floor((df[Y_VAR].min() - pad_y) * 2) / 2, np.ceil((df[Y_VAR].max() + pad_y) * 2) / 2)
    return xl, yl


def setup_style():
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "axes.edgecolor": "#B0B7BF",
        "axes.labelcolor": INK,
        "xtick.color": "#4A5560",
        "ytick.color": "#4A5560",
        "axes.spines.top": False,
        "axes.spines.right": False,
    })


def draw_frame(df, year, years, xl, yl, path):
    fig = plt.figure(figsize=(WIDTH_PX / DPI, HEIGHT_PX / DPI), dpi=DPI, facecolor="white")
    ax = fig.add_axes([0.065, 0.155, 0.70, 0.655])
    ax.set_xlim(*xl)
    ax.set_ylim(*yl)
    ax.grid(True, color="#E6E9EC", lw=0.8, zorder=0)
    ax.set_axisbelow(True)

    # Año grande de fondo (marca de agua) dentro del área de datos
    ax.text(0.5, 0.5, str(year), transform=ax.transAxes, ha="center", va="center",
            fontsize=170, color="#F2F4F5", fontweight="bold", zorder=0.5)

    cur = df[df[YEAR] == year].sort_values(SIZE_VAR, ascending=False)
    other = cur[~cur[COUNTRY].isin(HIGHLIGHT)]
    ax.scatter(other[X_VAR], other[Y_VAR], s=size_of(other[SIZE_VAR]), c=GREY,
               alpha=0.45, edgecolors="white", linewidths=0.7, zorder=2)

    # Estelas y puntos de países resaltados (solo años observados hasta el actual)
    for name, color in HIGHLIGHT.items():
        hist = df[(df[COUNTRY] == name) & (df[YEAR] <= year)].sort_values(YEAR)
        if hist.empty:
            continue
        # Segmentos entre años consecutivos: línea continua; si hay años sin
        # dato entre dos observaciones, línea punteada (no se interpola).
        for (_, a), (_, b) in zip(hist.iloc[:-1].iterrows(), hist.iloc[1:].iterrows()):
            gap = b[YEAR] - a[YEAR] > 1
            ax.plot([a[X_VAR], b[X_VAR]], [a[Y_VAR], b[Y_VAR]], color=color, lw=1.4,
                    alpha=0.55, zorder=3, linestyle=":" if gap else "-")
        if len(hist) > 1:
            ax.scatter(hist[X_VAR].iloc[:-1], hist[Y_VAR].iloc[:-1], s=9, color=color,
                       alpha=0.55, zorder=3, linewidths=0)
        last = hist.iloc[-1]
        observed_now = last[YEAR] == year
        if observed_now:
            ax.scatter(last[X_VAR], last[Y_VAR], s=size_of(last[SIZE_VAR]), color=color,
                       alpha=0.9, edgecolors="white", linewidths=1.2, zorder=5)
            label = LABELS_ES[name]
        else:
            # País sin dato este año: se muestra solo la estela y una marca hueca
            ax.scatter(last[X_VAR], last[Y_VAR], s=60, facecolors="none", edgecolors=color,
                       linewidths=1.3, linestyle=(0, (2, 2)), zorder=5)
            label = f"{LABELS_ES[name]} (último dato: {int(last[YEAR])})"
        r = np.sqrt(size_of(last[SIZE_VAR]) / np.pi) if observed_now else 5
        ax.annotate(label, (last[X_VAR], last[Y_VAR]), xytext=(r + 4, r * 0.4 + 2),
                    textcoords="offset points", fontsize=12.5, color=color,
                    fontweight="bold", zorder=6,
                    bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.75))

    ax.set_xlabel("Log GDP per capita  (logaritmo natural del PIB per cápita, PPA)", fontsize=14, labelpad=8)
    ax.set_ylabel("Life Ladder  (bienestar subjetivo, escala 0–10)", fontsize=14, labelpad=8)
    ax.tick_params(labelsize=12)

    # Eje superior de referencia: exp(Log GDP) en dólares aproximados
    sec = ax.secondary_xaxis("top", functions=(np.exp, lambda v: np.log(np.clip(v, 1e-9, None))))
    ticks = [v for v in [1000, 2000, 5000, 10000, 20000, 50000, 100000]
             if xl[0] <= np.log(v) <= xl[1]]
    sec.set_xticks(ticks, [f"${v/1000:g}k" for v in ticks])
    sec.tick_params(labelsize=10.5, colors="#6B7580")
    sec.set_xlabel("equivalente aproximado en dólares PPA = exp(Log GDP)", fontsize=10.5,
                   color="#6B7580", labelpad=6)
    sec.spines["top"].set_visible(True)
    sec.spines["top"].set_color("#D0D5DA")

    # Títulos
    fig.text(0.065, 0.955, "Ingreso y bienestar subjetivo por país, 2005–2020",
             fontsize=24, fontweight="bold", color=INK, va="top")
    fig.text(0.065, 0.905, "Cada círculo es un país en el año indicado · tamaño = esperanza de vida sana al nacer",
             fontsize=14, color="#4A5560", va="top")

    # Panel derecho: año, muestra, correlación, leyendas
    px = 0.795
    fig.text(px, 0.80, str(year), fontsize=72, fontweight="bold", color=INK, va="top")
    idx = years.index(year)
    # Barra de progreso de años
    bar = fig.add_axes([px, 0.665, 0.17, 0.025])
    bar.set_xlim(years[0] - 0.5, years[-1] + 0.5)
    bar.set_ylim(0, 1)
    bar.axis("off")
    bar.barh(0.5, year - years[0] + 1, left=years[0] - 0.5, height=0.5, color=INK)
    bar.barh(0.5, years[-1] - years[0] + 1, left=years[0] - 0.5, height=0.5, color="#E6E9EC", zorder=0)
    bar.text(years[0] - 0.5, -0.4, str(years[0]), fontsize=10, color="#6B7580", va="top")
    bar.text(years[-1] + 0.5, -0.4, str(years[-1]), fontsize=10, color="#6B7580", va="top", ha="right")

    r = cur[X_VAR].corr(cur[Y_VAR])
    fig.text(px, 0.60, f"Países con datos: {len(cur)}", fontsize=15, color=INK, va="top")
    if len(cur) < SMALL_SAMPLE:
        fig.text(px, 0.562, "Muestra reducida: comparar con cautela", fontsize=11, color="#B5480B", va="top")
    fig.text(px, 0.525, f"Correlación de Pearson\n(entre países, este año): r = {r:.2f}",
             fontsize=13, color=INK, va="top", linespacing=1.3)
    fig.text(px, 0.455, "Describe asociación,\nno causalidad.", fontsize=11.5,
             color="#6B7580", va="top", style="italic", linespacing=1.3)

    # Leyenda de tamaño
    lax = fig.add_axes([px, 0.225, 0.17, 0.165])
    lax.axis("off")
    lax.set_xlim(0, 1)
    lax.set_ylim(0, 1)
    lax.text(0, 0.98, "Esperanza de vida sana", fontsize=12, color=INK, va="top", fontweight="bold")
    for i, v in enumerate([45, 60, 75]):
        yy = 0.70 - i * 0.24
        lax.scatter(0.12, yy, s=size_of(v), c=GREY, alpha=0.5, edgecolors="#7A838C")
        lax.text(0.32, yy, f"{v} años", fontsize=12, color=INK, va="center")
    lax.text(0, -0.06, f"área ∝ (años − {SIZE_BASE:.0f})", fontsize=9.5, color="#6B7580", va="top")

    # Leyenda de estelas
    handles = [Line2D([0], [0], color="#555", lw=1.4, marker="o", ms=3),
               Line2D([0], [0], color="#555", lw=1.4, ls=":"),
               Line2D([0], [0], color="#555", lw=0, marker="o", mfc="none", ms=7, mew=1.3)]
    fig.legend(handles, ["trayectoria (años observados)", "salto sobre años sin dato",
                         "sin dato este año\n(última posición)"],
               loc="lower left", bbox_to_anchor=(px - 0.005, 0.06), frameon=False, fontsize=10.5)

    fig.text(0.065, 0.018,
             "Fuente: World Happiness Report (base del curso Data-Analysis-with-R). Solo países-año con datos completos en las "
             "tres variables; sin imputación ni interpolación.\nLa muestra de países cambia entre años (en especial 2005 y 2020): "
             "los cambios en la nube de puntos pueden reflejar qué países entran o salen, no solo su evolución.",
             fontsize=10, color="#6B7580", linespacing=1.4)

    fig.savefig(path, dpi=DPI, facecolor="white")
    plt.close(fig)


def build_video(n_frames):
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise RuntimeError("ffmpeg no está instalado o no está en el PATH")
    # Lista de concatenación: cada año dura SECONDS_PER_YEAR; el último año se
    # sostiene FINAL_HOLD_SECONDS adicionales.
    lst = FRAMES_DIR / "frames.txt"
    lines = []
    for i in range(n_frames):
        dur = SECONDS_PER_YEAR + (FINAL_HOLD_SECONDS if i == n_frames - 1 else 0)
        lines += [f"file 'frame_{i:02d}.png'", f"duration {dur}"]
    lines.append(f"file 'frame_{n_frames - 1:02d}.png'")  # requerido por el demuxer concat
    lst.write_text("\n".join(lines) + "\n")
    cmd = [ffmpeg, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
           "-vf", f"fps={VIDEO_FPS},format=yuv420p", "-c:v", "libx264", "-preset", "medium",
           "-crf", "18", "-movflags", "+faststart", str(VIDEO_PATH)]
    subprocess.run(cmd, check=True)


def main():
    setup_style()
    df = pd.read_csv(CLEAN_CSV)
    years = sorted(df[YEAR].unique().tolist())
    xl, yl = axis_limits(df)
    print(f"Límites fijos: X={xl}, Y={yl}; años={years[0]}–{years[-1]} ({len(years)} fotogramas)")
    if FRAMES_DIR.exists():
        shutil.rmtree(FRAMES_DIR)
    FRAMES_DIR.mkdir(parents=True)
    for i, y in enumerate(years):
        draw_frame(df, y, years, xl, yl, FRAMES_DIR / f"frame_{i:02d}.png")
    # Copias de fotogramas clave como figuras estáticas
    shutil.copy(FRAMES_DIR / "frame_00.png", FIG_DIR / f"fotograma_{years[0]}.png")
    shutil.copy(FRAMES_DIR / f"frame_{len(years) - 1:02d}.png", FIG_DIR / f"fotograma_{years[-1]}.png")
    build_video(len(years))
    print(f"Video escrito en {VIDEO_PATH} ({VIDEO_PATH.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
