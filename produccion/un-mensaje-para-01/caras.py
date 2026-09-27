#!/usr/bin/env python3
"""¿Es la cara del Element? Parecido objetivo entre la cara del Element de Nelson y la de cada foto o clip.

    python3 caras.py <foto|clip|url> [<foto|clip|url> ...]

OpenCV: YuNet encuentra la cara y SFace la compara (coseno; 0,363 es el umbral de «misma persona»).
Calibrado el 2026-09-26 con las fotos que Nelson aprobó: **A 0,76 · B 0,72 · C 0,81**. Una foto
nueva muy por debajo de esa banda (p. ej. 0,46) se repite aunque pase el umbral: su «ese no soy yo»
está justo ahí. En un clip mide un fotograma por segundo y da el mínimo y la mediana: si el mínimo
cae, la cara se deforma dentro del clip.
Instala solo lo que falta: `pip install opencv-python-headless` y baja los dos modelos de opencv_zoo.
"""
import json
import os
import subprocess
import sys

import cv2
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.join(AQUI, "modelos")
ELEMENT = ("https://d8j0ntlcm91z4.cloudfront.net/user_36cfr0plJt7eQqcK83OjeHA0YJ9/"
           "hf_20260814_125833_d0cef32b-2794-4f6e-ad02-4aaac0fbda9c_min.webp")
ZOO = "https://github.com/opencv/opencv_zoo/raw/main/models/"
MODELOS = {"yunet.onnx": ZOO + "face_detection_yunet/face_detection_yunet_2023mar.onnx",
           "sface.onnx": ZOO + "face_recognition_sface/face_recognition_sface_2021dec.onnx"}
FFMPEG = os.environ.get("FFMPEG", "ffmpeg")


def traer(src, carpeta):
    if not src.startswith("http"):
        return src
    p = os.path.join(carpeta, src.rsplit("/", 1)[-1])
    if not os.path.exists(p):
        subprocess.run(["curl", "-sfL", "-o", p, src], check=True)
    return p


def leer(path):
    img = cv2.imread(path)
    if img is None:
        from PIL import Image
        img = cv2.cvtColor(np.array(Image.open(path).convert("RGB")), cv2.COLOR_RGB2BGR)
    s = 1280 / max(img.shape[:2])
    return cv2.resize(img, None, fx=s, fy=s) if s < 1 else img


def cara(img, rec):
    det = cv2.FaceDetectorYN.create(os.path.join(MOD, "yunet.onnx"), "", (img.shape[1], img.shape[0]), 0.6)
    _, f = det.detect(img)
    if f is None or not len(f):
        return None
    f = max(f, key=lambda x: x[2] * x[3])
    return rec.feature(rec.alignCrop(img, f))


def main():
    os.makedirs(MOD, exist_ok=True)
    for n, u in MODELOS.items():
        if not os.path.exists(os.path.join(MOD, n)):
            subprocess.run(["curl", "-sfL", "-o", os.path.join(MOD, n), u], check=True)
    rec = cv2.FaceRecognizerSF.create(os.path.join(MOD, "sface.onnx"), "")
    ref = cara(leer(traer(ELEMENT, MOD)), rec)
    out = {}
    for src in sys.argv[1:]:
        p = traer(src, MOD)
        nombre = src.rsplit("/", 1)[-1][:60]
        if p.lower().rsplit(".", 1)[-1] in ("mp4", "mov", "webm"):
            carpeta = os.path.join(MOD, "fr_" + os.path.basename(p))
            os.makedirs(carpeta, exist_ok=True)
            subprocess.run([FFMPEG, "-v", "error", "-y", "-i", p, "-vf", "fps=1",
                            os.path.join(carpeta, "%03d.png")], check=True)
            vals = []
            for fr in sorted(os.listdir(carpeta)):
                c = cara(leer(os.path.join(carpeta, fr)), rec)
                vals.append(None if c is None else round(float(rec.match(ref, c, cv2.FaceRecognizerSF_FR_COSINE)), 3))
            ok = [v for v in vals if v is not None]
            out[nombre] = {"por_segundo": vals, "minimo": min(ok) if ok else None,
                           "mediana": float(np.median(ok)) if ok else None}
        else:
            c = cara(leer(p), rec)
            out[nombre] = None if c is None else round(float(rec.match(ref, c, cv2.FaceRecognizerSF_FR_COSINE)), 3)
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
