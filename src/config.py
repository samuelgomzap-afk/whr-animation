"""Configuración común del proyecto (rutas, variables y parámetros visuales)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "output"
FIG_DIR = OUTPUT_DIR / "figures"
FRAMES_DIR = FIG_DIR / "frames"

DATA_URL = (
    "https://raw.githubusercontent.com/Andres1984/Data-Analysis-with-R/"
    "refs/heads/master/Bases/world-happiness-report.csv"
)
RAW_CSV = DATA_DIR / "world-happiness-report.csv"
CLEAN_CSV = DATA_DIR / "whr_limpio.csv"

COUNTRY, YEAR = "Country name", "year"
X_VAR = "Log GDP per capita"
Y_VAR = "Life Ladder"
SIZE_VAR = "Healthy life expectancy at birth"
KEY_VARS = [X_VAR, Y_VAR, SIZE_VAR]

# Países resaltados (etiqueta + estela). Elegidos por cubrir distintos niveles
# de ingreso y regiones, y por tener series largas. Colores Okabe-Ito
# (aptos para daltonismo).
HIGHLIGHT = {
    "United States": "#0072B2",
    "Denmark": "#56B4E9",
    "China": "#D55E00",
    "India": "#E69F00",
    "Brazil": "#009E73",
    "Venezuela": "#CC79A7",
    "Zimbabwe": "#8C6D1F",
    "Afghanistan": "#000000",
}
LABELS_ES = {
    "United States": "Estados Unidos",
    "Denmark": "Dinamarca",
    "China": "China",
    "India": "India",
    "Brazil": "Brasil",
    "Venezuela": "Venezuela",
    "Zimbabwe": "Zimbabue",
    "Afghanistan": "Afganistán",
}

# Video
WIDTH_PX, HEIGHT_PX, DPI = 1920, 1080, 120
SECONDS_PER_YEAR = 2.0
FINAL_HOLD_SECONDS = 3.0
VIDEO_FPS = 30
VIDEO_PATH = OUTPUT_DIR / "video_final.mp4"
