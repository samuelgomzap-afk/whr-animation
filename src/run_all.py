"""Ejecuta el proyecto completo desde cero: python src/run_all.py"""
import s01_cargar_inspeccionar, s02_limpieza, s03_animacion, s04_verificacion, s05_analisis

if __name__ == "__main__":
    for step in (s01_cargar_inspeccionar, s02_limpieza, s03_animacion, s04_verificacion, s05_analisis):
        print(f"\n===== {step.__name__} =====")
        step.main()
    print("\nListo: output/video_final.mp4")
