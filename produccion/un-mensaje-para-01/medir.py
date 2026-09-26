#!/usr/bin/env python3
"""Mide un clip antes de dárselo a Nelson (MONTAJE.md § Revisión antes de entregar).

    python3 medir.py <clip.mp4|url> "<línea del guion>" [salida_dir]

Saca, en JSON:
  - palabras: transcripción de faster-whisper SIN el guion como pista (medida honesta) y el % de
    palabras del guion que aparecen en orden. Whisper no juzga pronunciación: eso es del oído de Nelson.
  - habla: dónde empieza y termina la voz (para recortar el arranque: Seedance habla en 0,00).
  - ritmo: sílabas por segundo del guion sobre el tramo hablado (≈5 natural; 8+ atropella).
  - tono: rango en semitonos por frase, con el mismo método que studio/scouting/pipeline/analizar_video.py
    (autocorrelación, p10-p90), para que se compare con sus números: voz real 24-29, plana 8-11.
  - hoja.jpg: 12 fotogramas en rejilla, para mirar cara, boca, manos y letras.
"""
import difflib
import glob
import json
import os
import re
import subprocess
import sys
import unicodedata
import wave

import numpy as np

FFMPEG = os.environ.get("FFMPEG", "ffmpeg")


def normalizar(w):
    w = unicodedata.normalize("NFD", w.lower())
    w = "".join(c for c in w if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9ñ]", "", w)


def silabas(texto):
    return len(re.findall(r"[aeiouáéíóúü]+", texto.lower()))


def f0_rangos(wav_path, segmentos):
    with wave.open(wav_path, "rb") as wf:
        sr = wf.getframerate()
        audio = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
    win, hop = int(0.04 * sr), int(0.01 * sr)
    min_lag, max_lag = int(sr / 400), int(sr / 75)

    def f0(frame):
        frame = frame - frame.mean()
        if np.max(np.abs(frame)) < 1e-4:
            return 0.0
        ac = np.correlate(frame, frame, mode="full")[len(frame) - 1:]
        seg = ac[min_lag:max_lag]
        if len(seg) == 0 or np.max(seg) <= 0:
            return 0.0
        lag = min_lag + int(np.argmax(seg))
        if ac[0] <= 0 or seg[lag - min_lag] / ac[0] < 0.3:
            return 0.0
        return sr / lag

    out = []
    for texto, a, b in segmentos:
        vals = [v for s in range(int(a * sr), max(int(a * sr) + 1, int(b * sr) - win), hop)
                if (v := f0(audio[s:s + win])) > 0]
        if len(vals) >= 3:
            st = 12 * np.log2(np.array(vals) / np.median(vals))
            out.append({"texto": texto.strip(), "desde": round(a, 2), "hasta": round(b, 2),
                        "hz_mediana": round(float(np.median(vals)), 1),
                        "semitonos": round(float(np.percentile(st, 90) - np.percentile(st, 10)), 1)})
    return out


def main():
    src, guion = sys.argv[1], sys.argv[2]
    out = sys.argv[3] if len(sys.argv) > 3 else "medida"
    os.makedirs(out, exist_ok=True)
    clip = src
    if src.startswith("http"):
        clip = os.path.join(out, "clip.mp4")
        subprocess.run(["curl", "-sfL", "-o", clip, src], check=True)
    wav = os.path.join(out, "voz.wav")
    subprocess.run([FFMPEG, "-v", "error", "-y", "-i", clip, "-vn", "-ac", "1", "-ar", "16000", wav], check=True)
    r = subprocess.run([FFMPEG, "-i", clip], capture_output=True, text=True).stderr
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", r)
    dur = int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3])
    vs = re.search(r"Video: .*?(\d{3,4})x(\d{3,4})", r)
    fps = re.search(r"([\d.]+) fps", r)

    from faster_whisper import WhisperModel
    ruta = glob.glob("/opt/whisper-models/models--Systran--faster-whisper-small/snapshots/*")
    modelo = WhisperModel(ruta[0] if ruta else os.environ.get("WHISPER_MODEL", "small"),
                          device="cpu", compute_type="int8")
    segs, _ = modelo.transcribe(wav, language="es", word_timestamps=True, beam_size=5)
    segs = list(segs)
    palabras = [(w.word, w.start, w.end) for s in segs for w in s.words]
    oidas = [normalizar(w) for w, _, _ in palabras if normalizar(w)]
    esperadas = [normalizar(w) for w in guion.split() if normalizar(w)]
    sm = difflib.SequenceMatcher(None, esperadas, oidas, autojunk=False)
    iguales = sum(n for _, _, n in sm.get_matching_blocks())
    faltan = [" ".join(esperadas[i1:i2]) for tag, i1, i2, _, _ in sm.get_opcodes() if tag in ("delete", "replace")]
    sobran = [" ".join(oidas[j1:j2]) for tag, _, _, j1, j2 in sm.get_opcodes() if tag in ("insert", "replace")]
    t0 = palabras[0][1] if palabras else None
    t1 = palabras[-1][2] if palabras else None
    ritmo = silabas(guion) / (t1 - t0) if palabras and t1 > t0 else None
    tono = f0_rangos(wav, [(s.text, s.start, s.end) for s in segs])

    subprocess.run([FFMPEG, "-v", "error", "-y", "-i", clip, "-vf",
                    f"fps=12/{max(dur, 0.1):.3f},scale=240:-2,tile=6x2", "-frames:v", "1",
                    os.path.join(out, "hoja.jpg")], check=True)
    informe = {
        "clip": src, "duracion": round(dur, 2),
        "video": f"{vs[1]}x{vs[2]}" if vs else None, "fps": float(fps[1]) if fps else None,
        "transcripcion": " ".join(s.text.strip() for s in segs),
        "palabras_del_guion": f"{iguales}/{len(esperadas)} ({100 * iguales / max(1, len(esperadas)):.0f} %)",
        "faltan": faltan, "sobran": sobran,
        "habla_desde": round(t0, 2) if t0 is not None else None,
        "habla_hasta": round(t1, 2) if t1 is not None else None,
        "silabas_por_segundo": round(ritmo, 1) if ritmo else None,
        "tono_por_frase": tono,
        "semitonos_promedio": round(float(np.mean([x["semitonos"] for x in tono])), 1) if tono else None,
        "palabras": [(w.strip(), round(a, 2), round(b, 2)) for w, a, b in palabras],
    }
    json.dump(informe, open(os.path.join(out, "medida.json"), "w"), ensure_ascii=False, indent=1)
    resumen = {k: informe[k] for k in ("duracion", "video", "palabras_del_guion", "faltan", "sobran",
                                         "habla_desde", "habla_hasta", "silabas_por_segundo",
                                         "semitonos_promedio", "transcripcion")}
    print(json.dumps(resumen, ensure_ascii=False))


if __name__ == "__main__":
    main()
