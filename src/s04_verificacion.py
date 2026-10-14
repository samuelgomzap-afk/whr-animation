"""Paso 4: verifica el MP4 (existencia, tamaño, duración, resolución, frames,
y que pueda decodificarse completo). Escribe output/verificacion_video.txt."""
import json
import shutil
import subprocess

from config import (FINAL_HOLD_SECONDS, HEIGHT_PX, OUTPUT_DIR, SECONDS_PER_YEAR,
                    VIDEO_FPS, VIDEO_PATH, WIDTH_PX, CLEAN_CSV, YEAR)
import pandas as pd


def probe():
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames",
         "-show_entries", "stream=codec_name,width,height,r_frame_rate,nb_read_frames,pix_fmt:format=duration,size",
         "-of", "json", str(VIDEO_PATH)], capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


def main():
    assert VIDEO_PATH.exists(), "el video no existe"
    size = VIDEO_PATH.stat().st_size
    assert size > 0, "el video está vacío"
    if shutil.which("ffprobe") is None:
        print(f"ffprobe no disponible; video existe con {size} bytes")
        return
    info = probe()
    st, fm = info["streams"][0], info["format"]
    n_years = pd.read_csv(CLEAN_CSV)[YEAR].nunique()
    expected_dur = n_years * SECONDS_PER_YEAR + FINAL_HOLD_SECONDS
    # Decodificación completa: cualquier error de lectura aparece en stderr
    dec = subprocess.run(["ffmpeg", "-v", "error", "-i", str(VIDEO_PATH), "-f", "null", "-"],
                         capture_output=True, text=True)
    checks = {
        "existe": True,
        "tamano_bytes": size,
        "codec": st["codec_name"],
        "pix_fmt": st["pix_fmt"],
        "resolucion": f"{st['width']}x{st['height']}",
        "resolucion_ok": (st["width"], st["height"]) == (WIDTH_PX, HEIGHT_PX),
        "fps": st["r_frame_rate"],
        "frames_video": int(st["nb_read_frames"]),
        "frames_esperados": int(round(expected_dur * VIDEO_FPS)),
        "duracion_s": round(float(fm["duration"]), 2),
        "duracion_esperada_s": expected_dur,
        "anios_distintos_en_video": n_years,
        "decodifica_sin_errores": dec.returncode == 0 and not dec.stderr.strip(),
    }
    checks["duracion_ok"] = abs(checks["duracion_s"] - expected_dur) < 0.2
    txt = "\n".join(f"{k}: {v}" for k, v in checks.items())
    (OUTPUT_DIR / "verificacion_video.txt").write_text(txt + "\n", encoding="utf-8")
    print(txt)
    assert checks["resolucion_ok"] and checks["duracion_ok"] and checks["decodifica_sin_errores"], \
        "la verificación del video falló"


if __name__ == "__main__":
    main()
