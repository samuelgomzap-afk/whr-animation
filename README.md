# Ingreso y bienestar: animación al estilo Hans Rosling (World Happiness Report)

**Pregunta:** ¿La evolución del ingreso de los países a través del tiempo está acompañada por cambios en sus niveles de bienestar?

El proyecto descarga la base del World Happiness Report, la inspecciona, la limpia sin imputar valores y genera un video MP4 con un gráfico de burbujas animado (estilo Gapminder/Hans Rosling), además de un análisis descriptivo.

| Elemento | Variable de la base |
|---|---|
| Eje X | `Log GDP per capita` |
| Eje Y | `Life Ladder` |
| Tamaño | `Healthy life expectancy at birth` |
| Etiqueta | `Country name` (solo 8 países resaltados, para no saturar el gráfico) |
| Tiempo | `year` (un fotograma por año, 2005–2020) |

## Qué se hizo

1. **Carga e inspección** (`src/s01_cargar_inspeccionar.py`): 1949 filas país-año, 166 países, años 2005–2020, 11 variables (`Country name` texto, `year` entero y 9 numéricas). Sin duplicados país-año. Faltantes en las variables clave: `Log GDP per capita` 36 y `Healthy life expectancy at birth` 55; `Life Ladder` no tiene faltantes. El panel no está balanceado (27 países en 2005; entre 89 y 147 en los demás años; 95 en 2020).
2. **Limpieza** (`src/s02_limpieza.py`): casos completos en las tres variables de la animación → 1876 filas y 159 países. Sin imputación ni interpolación.
3. **Animación** (`src/s03_animacion.py`): un PNG por año con ejes fijos, estelas para los países resaltados y el número de países con datos en cada año; luego se unen con ffmpeg.
4. **Verificación** (`src/s04_verificacion.py`): existencia, tamaño, códec, resolución, duración, número de fotogramas y decodificación completa del MP4.
5. **Análisis y reporte** (`src/s05_analisis.py`): correlaciones por año entre países, cambios dentro de cada país, un panel balanceado 2008 vs. 2019 y el reporte en Markdown.

## Archivos generados

| Archivo | Contenido |
|---|---|
| `output/video_final.mp4` | Video final: 1920×1080, H.264, 30 fps, 35 s (16 años × 2 s + 3 s en el último año). |
| `output/resumen_datos.csv` | Por año: países en la base, países completos, excluidos, medias y medianas, y correlaciones de Pearson y Spearman entre GDP y Ladder. |
| `output/reporte_analisis.md` | Estructura de datos, faltantes, decisiones, hallazgos, revisión crítica y limitaciones. |
| `output/inspeccion_datos.txt` | Salida completa de la inspección inicial. |
| `output/cambios_por_pais.csv` | Cambio entre la primera y la última observación por país (≥ 8 años de diferencia). |
| `output/verificacion_video.txt` | Resultado de la verificación técnica del video. |
| `output/figures/valores_faltantes.png` | Mapa de disponibilidad país × año. |
| `output/figures/cambios_gdp_vs_ladder.png` | Cambio en ingreso vs. cambio en bienestar dentro de cada país. |
| `output/figures/fotograma_2005.png`, `fotograma_2020.png` | Primer y último fotograma del video. |
| `output/figures/frames/` | Los 16 fotogramas del video (se regeneran; no se versionan). |
| `data/world-happiness-report.csv` | Base original descargada. |
| `data/whr_limpio.csv` | Base limpia usada para la animación. |

## Decisiones de limpieza

- Se lee con `utf-8-sig` para eliminar el BOM del encabezado del CSV.
- Se conservan solo `Country name`, `year` y las tres variables graficadas.
- Se excluyen 73 filas país-año con algún faltante en X, Y o tamaño (análisis de casos completos por año). Algunos territorios desaparecen por completo (p. ej., North Cyprus, Somaliland region, Kosovo, Hong Kong, Taiwan, Palestinian Territories) porque nunca tienen las tres variables a la vez.
- **No se imputa ni se interpola**, ni entre países ni entre años: los valores imputados aparecerían en el video como trayectorias observadas. Cuando un país resaltado no tiene dato en un año, se muestra su última posición con un círculo hueco y la leyenda "último dato: AAAA". Si en su trayectoria hay años sin dato, ese tramo se dibuja punteado.
- No se eliminan atípicos ni se modifican valores observados.

## Diseño de la visualización

- Límites de ejes fijos para todo el video (X: 6–12, Y: 2–8.5), calculados sobre todos los años.
- El año aparece en grande en el panel derecho, con una barra de progreso y una marca de agua tenue en el fondo.
- Se resaltan 8 países con colores Okabe-Ito (aptos para daltonismo): Estados Unidos, Dinamarca, China, India, Brasil, Venezuela, Zimbabue y Afganistán. Se eligieron por cubrir distintos niveles de ingreso, regiones y trayectorias. El resto de los países aparece en gris, sin etiqueta.
- El eje superior muestra `exp(Log GDP)` en dólares PPA aproximados, solo como ayuda de lectura (es la misma variable).
- Cada fotograma muestra el número de países con datos, la correlación entre países de ese año (con la nota "asociación, no causalidad") y un aviso cuando la muestra tiene menos de 100 países.

## Dependencias

- Python ≥ 3.10
- `pandas`, `numpy`, `matplotlib` (ver `requirements.txt`)
- `ffmpeg` y `ffprobe` en el PATH (codificación H.264 con `libx264`)

## Cómo ejecutar desde cero

```bash
pip install -r requirements.txt
python src/run_all.py
```

`run_all.py` ejecuta los cinco pasos en orden. Si `data/world-happiness-report.csv` no existe, se descarga desde
<https://raw.githubusercontent.com/Andres1984/Data-Analysis-with-R/refs/heads/master/Bases/world-happiness-report.csv>.
Cada paso también se puede ejecutar por separado (`python src/s03_animacion.py`, etc.). Los parámetros (países resaltados, segundos por año, resolución) están en `src/config.py`.

## Principales hallazgos (descriptivos)

- **Entre países**, la asociación entre `Log GDP per capita` y `Life Ladder` es positiva en todos los años (r de Pearson entre 0.68 y 0.85).
- **Dentro de cada país**, a lo largo del tiempo, la asociación es bastante más débil: r ≈ 0.29 para las desviaciones respecto a la media de cada país, y r ≈ 0.34 entre el cambio de ingreso y el cambio de bienestar en 144 países. El ingreso subió en ~87% de esos países, pero el bienestar solo en ~63%; en ~28% el ingreso subió y el bienestar bajó.
- Por lo tanto, que los países más ricos reporten más bienestar no implica que el crecimiento del ingreso de un país vaya acompañado de forma consistente de más bienestar. Nada de esto establece causalidad. Detalles en `output/reporte_analisis.md`.

## Limitaciones

- Panel no balanceado y faltantes probablemente no aleatorios (afectan más a países de bajo ingreso o en conflicto). La composición de la muestra cambia entre años, sobre todo en 2005 (27 países) y 2020 (88 países con datos completos, año de pandemia).
- `Life Ladder` es una medida autoreportada de encuesta, con error muestral; los cambios anuales pequeños pueden ser ruido.
- El área de los círculos es proporcional a (años − 30), no a los años, para que las diferencias se vean. Se indica en la leyenda, pero exagera visualmente las diferencias relativas.
- Al no interpolar, el video avanza a saltos de un año; las estelas ayudan a seguir a los países, pero solo se dibujan para los 8 resaltados.
- La elección de los países resaltados es una decisión de diseño y puede orientar la lectura.
- Es un análisis descriptivo: no controla otras variables ni identifica efectos causales.
