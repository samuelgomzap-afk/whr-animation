# Reporte de análisis: ingreso y bienestar subjetivo (World Happiness Report)

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

- Observaciones (filas país-año): **1949**
- Países distintos: **166**
- Rango de años: **2005–2020** (16 años)
- Variables: **11** — `Country name` (texto), `year` (entero) y 9 variables numéricas (float).
- Duplicados país-año: 0
- Panel **no balanceado**: la cantidad de países varía entre 27 (2005) y 147 por año.

### Valores faltantes (base original)

| Variable | Faltantes | % |
|---|---|---|
| Country name | 0 | 0.0% |
| year | 0 | 0.0% |
| Life Ladder | 0 | 0.0% |
| Log GDP per capita | 36 | 1.8% |
| Social support | 13 | 0.7% |
| Healthy life expectancy at birth | 55 | 2.8% |
| Freedom to make life choices | 32 | 1.6% |
| Generosity | 89 | 4.6% |
| Perceptions of corruption | 110 | 5.6% |
| Positive affect | 22 | 1.1% |
| Negative affect | 16 | 0.8% |

Además de las celdas vacías hay **faltantes implícitos**: combinaciones país-año que no aparecen en la base (ver `output/figures/valores_faltantes.png`).

## 2. Decisiones de limpieza

1. Lectura con codificación `utf-8-sig` para eliminar el BOM del encabezado.
2. Se conservan solo las cinco columnas necesarias.
3. **Casos completos por año**: se excluyen 73 filas país-año con faltante en X, Y o tamaño. Quedan **1876 filas** y **159 países**.
   Los países sin `Log GDP per capita` ni `Healthy life expectancy` en ningún año (North Cyprus, Somaliland region) desaparecen por completo; otros (Kosovo, Hong Kong, Taiwan, Palestinian Territories) se pierden porque les falta la esperanza de vida sana.
4. **No se imputa ni se interpola**. Rellenar con medias o interpolar entre años inventaría trayectorias que no se observaron, justo lo que el video pretende mostrar. Si un país resaltado no tiene dato en un año, el video lo marca como "último dato: AAAA" en vez de inventar su posición.
5. No se eliminan atípicos ni se modifican valores observados.

## 3. Resumen por año (casos completos)

| Año | Países en base | Países completos | Mediana Life Ladder | Mediana Log GDP | r (Pearson) GDP–Ladder |
|---|---|---|---|---|---|
| 2005 | 27 | 27 | 6.62 | 10.46 | 0.68 |
| 2006 | 89 | 87 | 5.08 | 9.04 | 0.84 |
| 2007 | 102 | 101 | 5.22 | 9.27 | 0.77 |
| 2008 | 110 | 108 | 5.18 | 9.21 | 0.85 |
| 2009 | 114 | 111 | 5.35 | 9.33 | 0.73 |
| 2010 | 124 | 121 | 5.46 | 9.46 | 0.77 |
| 2011 | 146 | 141 | 5.22 | 9.33 | 0.77 |
| 2012 | 142 | 136 | 5.26 | 9.46 | 0.78 |
| 2013 | 137 | 133 | 5.24 | 9.44 | 0.78 |
| 2014 | 145 | 138 | 5.32 | 9.43 | 0.81 |
| 2015 | 143 | 137 | 5.34 | 9.46 | 0.82 |
| 2016 | 142 | 135 | 5.42 | 9.51 | 0.83 |
| 2017 | 147 | 142 | 5.57 | 9.50 | 0.80 |
| 2018 | 142 | 135 | 5.47 | 9.56 | 0.78 |
| 2019 | 144 | 136 | 5.64 | 9.59 | 0.76 |
| 2020 | 95 | 88 | 5.85 | 9.88 | 0.84 |

Tabla completa en `output/resumen_datos.csv`.

## 4. Hallazgos descriptivos

**Entre países (cada año):** la asociación entre ingreso y bienestar es positiva y estable: r de Pearson entre 0.68 y 0.85. Los países con mayor ingreso tienden a reportar mayor bienestar y mayor esperanza de vida sana. Considerando todos los países-año juntos, r = 0.79.

**Dentro de cada país (a través del tiempo)**, que es lo que plantea la pregunta, la relación es bastante más débil:

- Correlación de las desviaciones respecto a la media de cada país (variación "within"): r = 0.29.
- Para 144 países con al menos 8 años entre su primera y última observación, la correlación entre el cambio en Log GDP y el cambio en Life Ladder es r = 0.34 (Spearman ρ = 0.33). Ver `output/figures/cambios_gdp_vs_ladder.png` y `output/cambios_por_pais.csv`.
- En ese grupo, el ingreso subió en el 87% de los países, pero el bienestar subió solo en el 62%. En un 28% el ingreso subió y el bienestar bajó; en un 5% ocurrió lo contrario.
- **Panel balanceado** (98 países presentes en 2008 y 2019): media de Log GDP 9.19 → 9.41; media de Life Ladder 5.46 → 5.60; esperanza de vida sana 61.5 → 65.1 años.

Países resaltados en el video (primera vs. última observación con datos completos):

| País | Periodo | Δ Log GDP | Δ Life Ladder | Δ Esperanza vida sana |
|---|---|---|---|---|
| Estados Unidos | 2006–2020 | +0.08 | -0.15 | +0.0 |
| Dinamarca | 2005–2020 | +0.06 | -0.50 | +3.4 |
| China | 2006–2020 | +1.01 | +1.21 | +3.0 |
| India | 2006–2020 | +0.56 | -1.12 | +5.2 |
| Brasil | 2005–2020 | +0.08 | -0.53 | +3.5 |
| Venezuela | 2005–2017 | -0.24 | -2.10 | +0.9 |
| Zimbabue | 2006–2020 | +0.12 | -0.67 | +15.2 |
| Afganistán | 2008–2019 | +0.33 | -1.35 | +1.6 |

Ejemplos: China e India aumentaron su ingreso de forma marcada, pero en China el bienestar también subió y en India bajó. Afganistán y Zimbabue aumentaron levemente su ingreso y su bienestar bajó; Venezuela redujo ambos hasta 2017, su último año con datos completos. Dinamarca y Estados Unidos se mantienen en la zona alta, con poco cambio de ingreso y un leve descenso de bienestar. La esperanza de vida sana aumentó en casi todos los países resaltados.

**Respuesta a la pregunta (descriptiva):** en la comparación entre países, mayor ingreso se asocia con mayor bienestar en todos los años. Pero la evolución del ingreso *dentro* de un país no se acompaña de forma consistente de cambios en el mismo sentido en su bienestar: la asociación de los cambios es positiva pero moderada (r ≈ 0.34) y en cerca de 28% de los países el ingreso subió mientras el bienestar bajó. Estos resultados son asociaciones; **no permiten concluir que el ingreso cause bienestar** (ni lo contrario). Pueden influir otros factores (conflictos, crisis políticas, instituciones, salud, apoyo social) que no se modelan aquí.

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
