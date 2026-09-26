#!/usr/bin/env python3
"""¿Los textos tapan la cara? Mide, cada medio segundo, qué parte de la cara (YuNet sobre el video sin textos)
queda bajo la capa de textos. Uso: python3 medir_capas.py <carpeta trabajo de montar.py> <cortes de escena en s…>"""
import sys
import cv2
import numpy as np
from PIL import Image

T = sys.argv[1]
cortes = [0.0] + [float(x) for x in sys.argv[2:]]
lst = [l for l in open(f"{T}/capa.ffconcat").read().split("\n") if l]
files = [l.split("'")[1] for l in lst[1:] if l.startswith("file")]
durs = [float(l.split()[1]) for l in lst[1:] if l.startswith("duration")]
t0 = np.concatenate([[0], np.cumsum(durs)])
cap = cv2.VideoCapture(f"{T}/base.mp4")
fps = cap.get(5)
det = cv2.FaceDetectorYN.create(sys.argv[0].rsplit("/", 1)[0] + "/modelos/yunet.onnx", "", (1080, 1920), 0.6)
res = {}
for s in np.arange(0.25, cortes[-1], 0.5):
    cap.set(1, int(s * fps))
    ok, fr = cap.read()
    if not ok:
        continue
    _, f = det.detect(fr)
    e = int(np.searchsorted(cortes, s, side="right"))
    if f is None:
        continue
    x, y, w, h = [int(v) for v in max(f, key=lambda z: z[2] * z[3])[:4]]
    a = np.asarray(Image.open(files[min(int(np.searchsorted(t0, s, side="right") - 1), len(files) - 1)]))[:, :, 3]
    x0, y0, x1, y1 = max(0, x), max(0, y), min(1080, x + w), min(1920, y + h)
    res.setdefault(e, []).append(float((a[y0:y1, x0:x1] > 100).mean()) if x1 > x0 and y1 > y0 else 0.0)
for e, v in sorted(res.items()):
    print(f"escena {e}: cara tapada máx {max(v):.2f} · media {np.mean(v):.2f} · muestras {len(v)}")
