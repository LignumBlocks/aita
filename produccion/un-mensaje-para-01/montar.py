#!/usr/bin/env python3
"""Monta «Un mensaje para… · episodio 1» a partir de plan.json.

    python3 montar.py plan.json salida.mp4            # pieza real: clips de video con voz
    python3 montar.py plan.json salida.mp4 --muestra  # plantilla: fotos fijas, tiempos repartidos

Capas (a lo Splitero, MONTAJE.md):
  1. Título fijo arriba, en recuadro blanco, todo el video salvo la placa.
  2. Subtítulos palabra por palabra, Outfit ExtraBold blanco con borde negro; la palabra clave en
     terracota. Los tiempos salen de faster-whisper sobre cada escena, alineados al texto del guion
     (se muestra el guion, no lo que whisper cree oír).
  3. Tarjetas que se apilan bajo el título, una por escena. En «la cuenta» se ven todas juntas.
  4. Insertos de manos encima de la escena, con la voz de la escena debajo.
  5. El cuestionario de umbralio.com a pantalla completa con Nelson recortado en una esquina.
  6. La placa final con la letra chica.

Tres cosas que no son obvias:
  - Los textos se dibujan con PIL y entran como una sola capa con alfa (concat de PNG por estados):
    drawtext no mezcla fuentes y cientos de overlays sueltos hacen el filtro lentísimo.
  - Cada escena se normaliza a -16 LUFS por separado antes de unirlas (MONTAJE § Audio).
  - Nada de ffprobe: la ffmpeg de imageio no lo trae. Las duraciones se leen de la salida de ffmpeg.
"""
import difflib
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import unicodedata

from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(BASE, "fonts")
FFMPEG = os.environ.get("FFMPEG", "ffmpeg")

TERRA = (179, 74, 40, 255)      # #B34A28
INK = (46, 42, 36, 255)         # #2E2A24
MUTED = (122, 110, 96, 255)     # #7A6E60
BONE = (247, 245, 240, 255)     # #F7F5F0
WHITE = (255, 255, 255, 255)
BLACK = (0, 0, 0, 255)

_cache = {}


def fuente(nombre, size):
    k = (nombre, size)
    if k not in _cache:
        _cache[k] = ImageFont.truetype(os.path.join(FONTS, nombre), size)
    return _cache[k]


def ff(*args):
    subprocess.run([FFMPEG, "-v", "error", "-y", *args], check=True)


def duracion(path):
    r = subprocess.run([FFMPEG, "-i", path], capture_output=True, text=True)
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", r.stderr)
    return int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3])


def es_imagen(path):
    return path.lower().rsplit(".", 1)[-1] in ("png", "jpg", "jpeg", "webp")


def traer(src, work):
    """URL → archivo local (en el sandbox de Higgsfield); ruta local → tal cual."""
    if not src.startswith("http"):
        return src if os.path.isabs(src) else os.path.join(BASE, src)
    nombre = os.path.join(work, "in_" + re.sub(r"[^\w.]", "_", src.rsplit("/", 1)[-1])[-80:])
    if not os.path.exists(nombre):
        subprocess.run(["curl", "-sfL", "-o", nombre, src], check=True)
    return nombre


# ------------------------------------------------------------------ texto enriquecido

def partes_markup(texto):
    """«**$2,200** de renta» → [("$2,200", "num"), (" de renta", "txt")]. ** = número, * = clave."""
    out = []
    for m in re.finditer(r"\*\*(.+?)\*\*|\*(.+?)\*|([^*]+)", texto):
        if m[1] is not None:
            out.append((m[1], "num"))
        elif m[2] is not None:
            out.append((m[2], "key"))
        else:
            out.append((m[3], "txt"))
    return out


def estilo(tipo, size, base="Outfit-Bold.ttf"):
    if tipo == "num":
        return fuente("DMMono-Medium.ttf", int(size * 0.95)), TERRA
    if tipo == "key":
        return fuente(base, size), TERRA
    return fuente(base, size), INK


def maquetar(d, partes, size, ancho, base="Outfit-Bold.ttf"):
    """Reparte palabras con estilo en líneas de como mucho `ancho` px. Devuelve [[(texto, font, color, w)]]."""
    palabras = []
    for texto, tipo in partes:
        for i, trozo in enumerate(re.split(r"(\n)", texto)):
            if trozo == "\n":
                palabras.append(("\n", None, None))
                continue
            if re.match(r"\s", trozo) and palabras and palabras[-1][0] != "\n" and not palabras[-1][0].endswith(" "):
                palabras[-1] = (palabras[-1][0] + " ", palabras[-1][1], palabras[-1][2])
            for w in re.findall(r"\S+\s*", trozo):
                f, c = estilo(tipo, size, base)
                palabras.append((w, f, c))
    lineas, actual, ancho_act = [], [], 0
    for w, f, c in palabras:
        if w == "\n":
            lineas.append(actual)
            actual, ancho_act = [], 0
            continue
        wl = d.textlength(w.rstrip(), font=f)
        esp = d.textlength(" ", font=fuente(base, size)) if w != w.rstrip() else 0
        if actual and ancho_act + wl > ancho:
            lineas.append(actual)
            actual, ancho_act = [], 0
        actual.append((w, f, c, wl, esp))
        ancho_act += wl + esp
    if actual:
        lineas.append(actual)
    return lineas


def ancho_linea(linea):
    return sum(wl + esp for _, _, _, wl, esp in linea) - (linea[-1][4] if linea else 0)


def dibujar_lineas(d, lineas, x, y, alto_linea, centrado=False, ancho_caja=0):
    for linea in lineas:
        lx = x + (ancho_caja - ancho_linea(linea)) / 2 if centrado else x
        for w, f, c, wl, esp in linea:
            d.text((lx, y), w.rstrip(), font=f, fill=c)
            lx += wl + esp
        y += alto_linea
    return y


# ------------------------------------------------------------------ capas fijas

def caja(W, alto, radio=18, color=WHITE):
    im = Image.new("RGBA", (W, alto), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle([0, 0, W - 1, alto - 1], radius=radio, fill=color)
    return im


def sombra(im, desplaz=6, alfa=70):
    s = Image.new("RGBA", (im.width + 24, im.height + 24), (0, 0, 0, 0))
    m = im.split()[3].point(lambda a: alfa if a else 0)
    s.paste((0, 0, 0, 255), (12, 12 + desplaz), m)
    from PIL import ImageFilter
    s = s.filter(ImageFilter.GaussianBlur(8))
    s.alpha_composite(im, (12, 12))
    return s


def render_titulo(cfg, W):
    t = cfg["titulo"]
    ancho = int(W * 0.88)
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    f1 = fuente("DMMono-Medium.ttf", int(W * 0.028))
    size2 = int(W * 0.043)
    lineas = maquetar(tmp, partes_markup(t["linea2"]), size2, ancho - 64)
    alto = 26 + int(W * 0.028 * 1.3) + 10 + len(lineas) * int(size2 * 1.2) + 22
    im = caja(ancho, alto)
    d = ImageDraw.Draw(im)
    d.text((32, 24), t["linea1"], font=f1, fill=TERRA)
    dibujar_lineas(d, lineas, 32, 26 + int(W * 0.028 * 1.3) + 6, int(size2 * 1.2))
    return sombra(im)


def render_tarjeta(texto, W, escala=1.0):
    ancho = int(W * 0.88 * escala)
    size = int(W * 0.034 * escala)
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    lineas = maquetar(tmp, partes_markup(texto), size, ancho - int(56 * escala), base="Outfit-Medium.ttf")
    alto_l = int(size * 1.28)
    alto = int(14 * escala) * 2 + len(lineas) * alto_l
    im = caja(ancho, alto, radio=int(14 * escala))
    d = ImageDraw.Draw(im)
    dibujar_lineas(d, lineas, int(26 * escala), int(12 * escala), alto_l)
    return sombra(im, desplaz=4, alfa=60)


def render_placa(cfg, W, H):
    p = cfg["placa"]
    im = Image.new("RGBA", (W, H), BONE)
    d = ImageDraw.Draw(im)
    f = fuente("Outfit-ExtraBold.ttf", int(W * 0.105))
    tw = d.textlength(p["marca"], font=f)
    y = int(H * p.get("y_marca", 0.30))
    d.text(((W - tw) / 2, y), p["marca"], font=f, fill=TERRA)
    y += int(W * 0.105 * 1.35)
    if p.get("bajada"):
        fb = fuente("Outfit-Medium.ttf", int(W * 0.042))
        lineas = maquetar(d, [(p["bajada"], "txt")], int(W * 0.042), int(W * 0.8), base="Outfit-Medium.ttf")
        y = dibujar_lineas(d, lineas, int(W * 0.1), y, int(W * 0.042 * 1.3), centrado=True, ancho_caja=int(W * 0.8))
        y += int(W * 0.04)
    fs = int(W * 0.024)
    lineas = maquetar(d, [(p["letra_chica"], "txt")], fs, int(W * 0.8), base="Outfit-Regular.ttf")
    for linea in lineas:
        for i, (w, f_, c, wl, esp) in enumerate(linea):
            linea[i] = (w, f_, MUTED, wl, esp)
    dibujar_lineas(d, lineas, int(W * 0.1), max(y, int(H * p.get("y_letra", 0.45))), int(fs * 1.45),
                   centrado=True, ancho_caja=int(W * 0.8))
    return im


def mascara_redondeada(w, h, r):
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], radius=r, fill=255)
    return m


# ------------------------------------------------------------------ subtítulos

TOKEN = re.compile(r"\{(\w+)\}|\[([^\]|]+)\|([^\]]+)\]([^\s\[{]*)|(\S+)")


def normalizar(w):
    w = unicodedata.normalize("NFD", w.lower())
    w = "".join(c for c in w if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9ñ]", "", w)


def tokens_de(subs):
    """«pagan más de [*$2,000*|dos mil dólares] de *renta*: {c1}tu…» → tokens con lo que se ve y lo que se oye."""
    out, ancla = [], None
    for m in TOKEN.finditer(subs):
        if m[1]:
            ancla = m[1]
            continue
        if m[2] is not None:
            disp, oido = m[2] + (m[4] or ""), m[3].split()
        else:
            disp, oido = m[5], [m[5]]
        clave = "*" in disp
        disp = disp.replace("*", "")
        oido = [normalizar(x) for x in oido if normalizar(x)]
        out.append({"disp": disp, "oido": oido, "clave": clave, "tarjeta": ancla,
                    "corte": bool(re.search(r"[.?!:;,]$", disp))})
        ancla = None
    return out


def repartir(tokens, t0, t1):
    """Sin audio (plantilla): reparte el tiempo por sílabas aproximadas."""
    pesos = [max(1, len(re.findall(r"[aeiouáéíóúü]+", " ".join(t["oido"]) or t["disp"], re.I))) for t in tokens]
    total, t = sum(pesos), t0
    for tok, p in zip(tokens, pesos):
        dur = (t1 - t0) * p / total
        tok["t0"], tok["t1"] = t, t + dur * 0.92
        t += dur


def alinear(tokens, palabras):
    """Pone a cada token el tiempo de sus palabras oídas, con la lista de whisper [(texto, t0, t1)]."""
    oidas = [(normalizar(w), a, b) for w, a, b in palabras if normalizar(w)]
    esperadas, dueno = [], []
    for i, tok in enumerate(tokens):
        for w in tok["oido"]:
            esperadas.append(w)
            dueno.append(i)
    sm = difflib.SequenceMatcher(None, esperadas, [w for w, _, _ in oidas], autojunk=False)
    tiempos = [None] * len(esperadas)
    for a, b, n in sm.get_matching_blocks():
        for k in range(n):
            tiempos[a + k] = oidas[b + k][1:]
    # huecos: interpolar entre vecinos conocidos
    conocidos = [i for i, t in enumerate(tiempos) if t]
    for i in range(len(tiempos)):
        if tiempos[i]:
            continue
        antes = max([k for k in conocidos if k < i], default=None)
        despues = min([k for k in conocidos if k > i], default=None)
        ta = tiempos[antes][1] if antes is not None else (oidas[0][1] if oidas else 0)
        tb = tiempos[despues][0] if despues is not None else (oidas[-1][2] if oidas else ta + 0.3)
        lo = antes if antes is not None else -1
        hi = despues if despues is not None else len(tiempos)
        frac = (i - lo) / (hi - lo)
        t = ta + (tb - ta) * frac
        tiempos[i] = (t, t + 0.25)
    for i, tok in enumerate(tokens):
        ts = [tiempos[k] for k in range(len(esperadas)) if dueno[k] == i]
        if ts:
            tok["t0"], tok["t1"] = min(a for a, _ in ts), max(b for _, b in ts)
    return sum(1 for t in tiempos if t) / max(1, len(tiempos))


def whisper_palabras(wav, texto_guion):
    from faster_whisper import WhisperModel
    ruta = glob.glob("/opt/whisper-models/models--Systran--faster-whisper-small/snapshots/*")
    modelo = WhisperModel(ruta[0] if ruta else "small", device="cpu", compute_type="int8")
    segs, _ = modelo.transcribe(wav, language="es", word_timestamps=True, initial_prompt=texto_guion,
                                vad_filter=False, beam_size=5)
    return [(w.word, w.start, w.end) for s in segs for w in s.words]


def agrupar(tokens, W, cfg):
    """Frases cortas para el subtítulo: corta en puntuación, a las `max_palabras`, o si hay pausa."""
    grupos, g = [], []
    d = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    f = fuente("Outfit-ExtraBold.ttf", cfg["subs"]["size"])
    for tok in tokens:
        if g:
            ancho = d.textlength(" ".join(x["disp"] for x in g + [tok]), font=f)
            pausa = tok["t0"] - g[-1]["t1"] > 0.6
            if len(g) >= cfg["subs"]["max_palabras"] or ancho > W * 0.86 or pausa or g[-1]["corte"]:
                grupos.append(g)
                g = []
        g.append(tok)
    if g:
        grupos.append(g)
    return grupos


def render_subs(visibles, W, cfg):
    s = cfg["subs"]
    f = fuente("Outfit-ExtraBold.ttf", s["size"])
    d = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    esp = d.textlength(" ", font=f)
    total = sum(d.textlength(t["disp"], font=f) for t in visibles) + esp * (len(visibles) - 1)
    alto = int(s["size"] * 1.5)
    im = Image.new("RGBA", (W, alto), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x = (W - total) / 2
    for t in visibles:
        color = TERRA if t["clave"] else WHITE
        d.text((x, 4), t["disp"], font=f, fill=color, stroke_width=s["borde"], stroke_fill=BLACK)
        x += d.textlength(t["disp"], font=f) + esp
    return im


# ------------------------------------------------------------------ escenas

def preparar_escena(e, cfg, work, muestra):
    W, H, fps = cfg["W"], cfg["H"], cfg["fps"]
    src = traer(e["src"], work)
    dur = e["out"] - e["in"]
    esc = f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},setsar=1,fps={fps}"
    entradas, fc = [], []
    if es_imagen(src):
        # plantilla: foto fija con un zoom muy lento para que se note que es video
        entradas += ["-loop", "1", "-t", f"{dur}", "-i", src,
                     "-f", "lavfi", "-t", f"{dur}", "-i", "anullsrc=r=48000:cl=stereo"]
        frames = int(dur * fps)
        fc.append(f"[0:v]scale={W * 2}:-2,zoompan=z='1+0.04*on/{frames}':d=1:s={W}x{H}:fps={fps},"
                  f"setsar=1,trim=duration={dur}[v0]")
        fc.append("[1:a]anull[a0]")
    else:
        entradas += ["-ss", f"{e['in']}", "-t", f"{dur}", "-i", src]
        fc.append(f"[0:v]{esc},setpts=PTS-STARTPTS[v0]")
        fc.append(f"[0:a]asetpts=PTS-STARTPTS,aresample=48000,"
                  f"loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000,"
                  f"afade=t=in:d=0.03,afade=t=out:st={dur - 0.04:.3f}:d=0.04[a0]")
    v, a, n = "v0", "a0", 2 if es_imagen(src) else 1
    mezclas = []
    for k, ins in enumerate(e.get("insertos", [])):
        isrc = traer(ins["src"], work)
        if es_imagen(isrc):
            entradas += ["-loop", "1", "-t", f"{ins['dur']}", "-i", isrc]
            fc.append(f"[{n}:v]{esc},trim=duration={ins['dur']},setpts=PTS-STARTPTS+{ins['en']}/TB[i{k}]")
        else:
            entradas += ["-ss", f"{ins.get('src_in', 0)}", "-t", f"{ins['dur']}", "-i", isrc]
            fc.append(f"[{n}:v]{esc},setpts=PTS-STARTPTS+{ins['en']}/TB[i{k}]")
            if ins.get("vol", 0) > 0 and not muestra:
                ms = int(ins["en"] * 1000)
                fc.append(f"[{n}:a]asetpts=PTS-STARTPTS,aresample=48000,volume={ins['vol']},"
                          f"afade=t=in:d=0.1,afade=t=out:st={ins['dur'] - 0.15:.2f}:d=0.15,"
                          f"adelay={ms}|{ms}[ia{k}]")
                mezclas.append(f"[ia{k}]")
        fc.append(f"[{v}][i{k}]overlay=0:0:eof_action=pass:"
                  f"enable='between(t,{ins['en']},{ins['en'] + ins['dur']})'[v{k + 1}]")
        v = f"v{k + 1}"
        n += 1
    q = cfg.get("cuestionario")
    if q and q["escena"] == e["id"]:
        wsrc = traer(q["src"], work)
        wdur = q["hasta"] - q["desde"]
        vel = q.get("velocidad", 1.0)
        entradas += ["-ss", f"{q.get('src_in', 0)}", "-i", wsrc]
        pw = q["pip"]["w"]
        ph = int(pw * H / W)
        ph -= ph % 2
        mask = os.path.join(work, "pip_mask.png")
        mascara_redondeada(pw, ph, q["pip"].get("radio", 28)).save(mask)
        entradas += ["-loop", "1", "-i", mask]
        fc.append(f"[{n}:v]setpts=(PTS-STARTPTS)/{vel},scale={W}:{H}:force_original_aspect_ratio=decrease:"
                  f"flags=lanczos,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=0xF7F5F0,setsar=1,fps={fps},"
                  f"trim=duration={wdur},setpts=PTS-STARTPTS+{q['desde']}/TB[wz]")
        fc.append(f"[{v}]split[full][peq]")
        fc.append(f"[peq]scale={pw}:{ph}:flags=lanczos,format=rgba[peq2]")
        fc.append(f"[{n + 1}:v]format=gray,scale={pw}:{ph}[pm]")
        fc.append("[peq2][pm]alphamerge[pip]")
        fc.append(f"[full][wz]overlay=0:0:eof_action=pass:enable='between(t,{q['desde']},{q['hasta']})'[bg]")
        fc.append(f"[bg][pip]overlay={q['pip']['x']}:{q['pip']['y']}:shortest=0:"
                  f"enable='between(t,{q['desde']},{q['hasta']})'[vq]")
        v = "vq"
        n += 2
    if mezclas:
        fc.append(f"[{a}]{''.join(mezclas)}amix=inputs={1 + len(mezclas)}:normalize=0:duration=first[am]")
        a = "am"
    fc.append(f"[{v}]trim=duration={dur},format=yuv420p[vout]")
    salida = os.path.join(work, f"esc{e['id']}.mp4")
    ff(*entradas, "-filter_complex", ";".join(fc), "-map", "[vout]", "-map", f"[{a}]",
       "-c:v", "libx264", "-crf", "16", "-preset", "veryfast", "-r", str(fps),
       "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-t", f"{dur}", salida)
    return salida, dur


def placa_video(cfg, work):
    W, H, fps, dur = cfg["W"], cfg["H"], cfg["fps"], cfg["placa"]["dur"]
    png = os.path.join(work, "placa.png")
    render_placa(cfg, W, H).convert("RGB").save(png)
    salida = os.path.join(work, "placa.mp4")
    ff("-loop", "1", "-t", f"{dur}", "-i", png, "-f", "lavfi", "-t", f"{dur}", "-i", "anullsrc=r=48000:cl=stereo",
       "-filter_complex", f"[0:v]fps={fps},format=yuv420p,fade=t=in:d=0.25[v]", "-map", "[v]", "-map", "1:a",
       "-c:v", "libx264", "-crf", "16", "-preset", "veryfast", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
       "-t", f"{dur}", salida)
    return salida, dur


# ------------------------------------------------------------------ capa de textos

def capa_textos(cfg, escenas_t, tokens_abs, total, work):
    """Recorre el video a `fps` y dibuja un PNG solo cuando cambia lo que se ve."""
    W, H, fps = cfg["W"], cfg["H"], cfg["fps"]
    titulo = render_titulo(cfg, W)
    ty = cfg["capas"]["titulo_y"]
    tarjetas = {c["id"]: c for c in cfg["tarjetas"]}
    for tok in tokens_abs:
        if tok.get("tarjeta"):
            tarjetas[tok["tarjeta"]]["t"] = tok["t0"]
    orden = sorted([c for c in tarjetas.values() if "t" in c], key=lambda c: c["t"])
    img_tarjeta = {c["id"]: render_tarjeta(c["texto"], W) for c in orden}
    img_mini = {c["id"]: render_tarjeta(c["texto"], W, escala=cfg["capas"]["cuenta_escala"]) for c in orden}
    grupos = agrupar(tokens_abs, W, cfg)
    fin_placa = total - cfg["placa"]["dur"]
    cuenta = cfg["capas"]["cuenta"]
    cuenta_t0 = escenas_t[cuenta["escena"]] + cuenta["desde"]
    cuenta_t1 = escenas_t[cuenta["escena"]] + cuenta["hasta"]
    q = cfg.get("cuestionario")
    wz = (escenas_t[q["escena"]] + q["desde"], escenas_t[q["escena"]] + q["hasta"]) if q else (-1, -1)
    anim = 0.22
    carpeta = os.path.join(work, "capa")
    shutil.rmtree(carpeta, ignore_errors=True)
    os.makedirs(carpeta)
    lista, anterior, n_frames = [], None, int(total * fps) + 1
    for fr in range(n_frames):
        t = fr / fps
        if t >= fin_placa:
            estado = ("placa",)
        else:
            en_wz = wz[0] <= t < wz[1]
            en_cuenta = cuenta_t0 <= t < cuenta_t1
            # subtítulo
            subs = ()
            for gi, g in enumerate(grupos):
                sig = grupos[gi + 1][0]["t0"] if gi + 1 < len(grupos) else 1e9
                if g[0]["t0"] <= t < min(sig, g[-1]["t1"] + 0.7):
                    subs = tuple(i for i, tok in enumerate(g) if tok["t0"] <= t)
                    subs = (gi, subs)
                    break
            # tarjetas
            vis = [c for c in orden if c["t"] <= t]
            if en_wz:
                cards = ()
            elif en_cuenta:
                cards = ("cuenta", tuple(c["id"] for c in vis))
            else:
                ult = vis[-cfg["capas"]["max_tarjetas"]:]
                cards = tuple((c["id"], min(1.0, round((t - c["t"]) / anim, 1))) for c in ult)
            estado = ("v", subs, cards, en_wz)
        if estado != anterior:
            png = os.path.join(carpeta, f"c{len(lista):05d}.png")
            if estado[0] == "placa":
                Image.new("RGBA", (W, H), (0, 0, 0, 0)).save(png)
            else:
                im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                _, subs, cards, en_wz = estado
                if cards and cards[0] == "cuenta":
                    velo = Image.new("RGBA", (W, H), (0, 0, 0, int(255 * cuenta["velo"])))
                    im.alpha_composite(velo)
                im.alpha_composite(titulo, ((W - titulo.width) // 2, ty))
                y = ty + titulo.height + cfg["capas"]["hueco"]
                if cards and cards[0] == "cuenta":
                    for cid in cards[1]:
                        c = img_mini[cid]
                        im.alpha_composite(c, ((W - c.width) // 2, y))
                        y += c.height - 12
                else:
                    for cid, p in cards:
                        c = img_tarjeta[cid]
                        if p < 1:
                            s = 0.92 + 0.08 * p
                            c2 = c.resize((int(c.width * s), int(c.height * s)), Image.LANCZOS)
                            a = c2.split()[3].point(lambda v, p=p: int(v * p))
                            c2.putalpha(a)
                            im.alpha_composite(c2, ((W - c2.width) // 2, y + int((c.height - c2.height) / 2)))
                        else:
                            im.alpha_composite(c, ((W - c.width) // 2, y))
                        y += c.height - 12
                if subs:
                    gi, idx = subs
                    if idx:
                        s_im = render_subs([grupos[gi][i] for i in idx], W, cfg)
                        sy = cfg["subs"]["y_cuestionario"] if en_wz else cfg["subs"]["y"]
                        im.alpha_composite(s_im, (0, sy))
                im.save(png)
            lista.append([png, t])
            anterior = estado
    txt = os.path.join(work, "capa.ffconcat")
    with open(txt, "w") as fh:
        fh.write("ffconcat version 1.0\n")
        for i, (png, t) in enumerate(lista):
            t_sig = lista[i + 1][1] if i + 1 < len(lista) else total
            fh.write(f"file '{png}'\nduration {max(t_sig - t, 1 / fps):.5f}\n")
        fh.write(f"file '{lista[-1][0]}'\n")
    return txt, len(lista)


# ------------------------------------------------------------------ principal

def main():
    plan, salida = sys.argv[1], sys.argv[2]
    muestra = "--muestra" in sys.argv
    cfg = json.load(open(plan, encoding="utf-8"))
    work = os.path.join(os.path.dirname(os.path.abspath(salida)), "trabajo")
    os.makedirs(work, exist_ok=True)
    escenas = cfg["escenas_muestra"] if muestra else cfg["escenas"]
    q = cfg.get("cuestionario")
    if q and muestra and cfg.get("cuestionario_muestra"):
        cfg["cuestionario"] = {**q, **cfg["cuestionario_muestra"]}
    partes, escenas_t, tokens_abs, t = [], {}, [], 0.0
    informe = []
    for e in escenas:
        clip, dur = preparar_escena(e, cfg, work, muestra)
        partes.append(clip)
        escenas_t[e["id"]] = t
        toks = tokens_de(e["subs"])
        if muestra or es_imagen(traer(e["src"], work)):
            repartir(toks, e.get("habla_desde", 0.3), dur - 0.3)
            cobertura = None
        else:
            wav = os.path.join(work, f"esc{e['id']}.wav")
            ff("-i", clip, "-vn", "-ac", "1", "-ar", "16000", wav)
            guion = " ".join(" ".join(tok["oido"]) for tok in toks)
            cobertura = alinear(toks, whisper_palabras(wav, guion))
        for tok in toks:
            tok["t0"] += t
            tok["t1"] += t
        tokens_abs += toks
        informe.append({"escena": e["id"], "dur": round(dur, 2),
                        "alineadas": None if cobertura is None else round(cobertura, 3)})
        t += dur
    placa, dplaca = placa_video(cfg, work)
    partes.append(placa)
    total = t + dplaca
    lista = os.path.join(work, "partes.txt")
    with open(lista, "w") as fh:
        fh.writelines(f"file '{p}'\n" for p in partes)
    base = os.path.join(work, "base.mp4")
    ff("-f", "concat", "-safe", "0", "-i", lista, "-c", "copy", base)
    capa, n_png = capa_textos(cfg, escenas_t, tokens_abs, total, work)
    ff("-i", base, "-f", "concat", "-safe", "0", "-i", capa,
       "-filter_complex", "[1:v]format=rgba[c];[0:v][c]overlay=0:0:format=auto:eof_action=repeat,format=yuv420p[v]",
       "-map", "[v]", "-map", "0:a", "-c:v", "libx264", "-crf", "18", "-preset", "medium",
       "-profile:v", "high", "-movflags", "+faststart", "-c:a", "aac", "-b:a", "192k", "-t", f"{total}", salida)
    with open(os.path.join(work, "subs_tiempos.json"), "w", encoding="utf-8") as fh:
        json.dump([{k: tok[k] for k in ("disp", "t0", "t1", "clave")} for tok in tokens_abs], fh,
                  ensure_ascii=False, indent=0)
    print(json.dumps({"salida": salida, "duracion": round(total, 2), "capas_png": n_png, "escenas": informe},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
