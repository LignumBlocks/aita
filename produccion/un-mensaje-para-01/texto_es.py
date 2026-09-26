"""Normalización de palabras en español para comparar el guion con lo que escribe whisper.

Whisper escribe los números en cifras («12.000», «230 000», «$2,200») aunque se digan en palabras;
el guion los trae en palabras. Aquí las cifras se pasan a palabras antes de comparar.
"""
import re
import unicodedata

_U = "cero uno dos tres cuatro cinco seis siete ocho nueve diez once doce trece catorce quince dieciseis diecisiete dieciocho diecinueve veinte veintiuno veintidos veintitres veinticuatro veinticinco veintiseis veintisiete veintiocho veintinueve".split()
_D = {3: "treinta", 4: "cuarenta", 5: "cincuenta", 6: "sesenta", 7: "setenta", 8: "ochenta", 9: "noventa"}
_C = {1: "ciento", 2: "doscientos", 3: "trescientos", 4: "cuatrocientos", 5: "quinientos", 6: "seiscientos",
      7: "setecientos", 8: "ochocientos", 9: "novecientos"}


def _menor_mil(n):
    if n < 30:
        return _U[n]
    if n < 100:
        d, u = divmod(n, 10)
        return _D[d] + (" y " + _U[u] if u else "")
    if n == 100:
        return "cien"
    c, r = divmod(n, 100)
    return _C[c] + (" " + _menor_mil(r) if r else "")


def numero_a_palabras(n):
    if n < 1000:
        return _menor_mil(n)
    if n < 1_000_000:
        m, r = divmod(n, 1000)
        pre = "mil" if m == 1 else _menor_mil(m).replace("uno", "un") + " mil"
        return pre + (" " + _menor_mil(r) if r else "")
    return str(n)


def sin_tildes(w):
    w = unicodedata.normalize("NFD", w.lower())
    return "".join(c for c in w if unicodedata.category(c) != "Mn")


def palabras_normales(texto):
    """«cada 100 dólares, 12.000» → ['cada', 'cien', 'dolares', 'doce', 'mil']"""
    out = []
    # juntar cifras partidas por punto, coma o espacio de miles: «230 000», «12.000», «2,200»
    texto = re.sub(r"(?<=\d)[.,\s](?=\d{3}\b)", "", texto)
    for w in texto.split():
        w = sin_tildes(w)
        num = re.sub(r"[^\d]", "", w)
        if num and re.fullmatch(r"\$?\d+[.,:;?!]*", w):
            out += numero_a_palabras(int(num)).split()
            continue
        dom = re.fullmatch(r"([a-z0-9ñ]+)\.(com|org|net)[.,:;?!]*", w)
        if dom:
            out += [dom[1], "punto", dom[2]]
            continue
        w = re.sub(r"[^a-z0-9ñ]", "", w)
        if w:
            out.append(w)
    return out
