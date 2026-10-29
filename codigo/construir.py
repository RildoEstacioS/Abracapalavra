#!/usr/bin/env python3
"""Monta o Abracapalavra em um único arquivo HTML que funciona sem internet.

Junta o modelo (jogo.html) com as listas de palavras e as fontes e grava:
  ../index.html            versão para navegador (e para o GitHub Pages)
  lancador/web/index.html  cópia que vai dentro dos executáveis

Uso:  python3 construir.py
Não precisa instalar nada além do Python 3.
"""
import base64
import pathlib
import re
import unicodedata

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parent

FONTES = [
    ("Andika", 400, "Andika-400.woff2"),
    ("Andika", 700, "Andika-700.woff2"),
    ("Luckiest Guy", 400, "LuckiestGuy-400.woff2"),
    ("Rowdies", 400, "Rowdies-400.woff2"),
    ("Rowdies", 700, "Rowdies-700.woff2"),
]


def sem_acento(palavra):
    """casa -> casa, maçã -> maca, Pé -> pe (as peças do jogo não têm acento)."""
    nfd = unicodedata.normalize("NFD", palavra.strip().lower())
    return "".join(c for c in nfd if unicodedata.category(c) != "Mn")


def ler_palavras(nome):
    """Uma palavra por linha; linhas vazias ou começando com # são ignoradas."""
    saida, vistas = [], set()
    for linha in (AQUI / nome).read_text(encoding="utf-8").splitlines():
        if not linha.strip() or linha.lstrip().startswith("#"):
            continue
        p = sem_acento(linha)
        if re.fullmatch(r"[a-z]{2,12}", p) and p not in vistas:
            vistas.add(p)
            saida.append(p)
    return saida


def ler_silabas(nome):
    """Uma palavra por linha, com as sílabas separadas por hífen: ca-sa, ba-na-na."""
    saida = []
    for linha in (AQUI / nome).read_text(encoding="utf-8").splitlines():
        if not linha.strip() or linha.lstrip().startswith("#"):
            continue
        p = sem_acento(linha)
        if re.fullmatch(r"[a-z]+(-[a-z]+){1,4}", p):
            saida.append(p)
    return saida


def css_fontes():
    faixa = (AQUI / "fontes" / "unicode-range.txt").read_text(encoding="utf-8").strip()
    regras = []
    for familia, peso, arquivo in FONTES:
        dados = base64.b64encode((AQUI / "fontes" / arquivo).read_bytes()).decode("ascii")
        regras.append(
            f"@font-face{{font-family:'{familia}';font-style:normal;font-weight:{peso};font-display:swap;"
            f"src:url(data:font/woff2;base64,{dados}) format('woff2');unicode-range:{faixa};}}"
        )
    return "\n".join(regras)


def main():
    modelo = (AQUI / "jogo.html").read_text(encoding="utf-8")
    dicionario = ler_palavras("dicionario.txt")
    monstro = ler_palavras("palavras-monstro.txt")
    silabas = ler_silabas("silabas.txt")
    icone = base64.b64encode((AQUI / "lancador" / "icone" / "icone.svg").read_bytes()).decode("ascii")

    html = (
        modelo.replace("__WORDS__", " ".join(dicionario))
        .replace("__MONSTER__", " ".join(monstro))
        .replace("__SILABAS__", " ".join(silabas))
        .replace("/*__FONTES__*/", css_fontes())
        .replace("__ICONE__", icone)
    )
    for destino in (RAIZ / "index.html", AQUI / "lancador" / "web" / "index.html"):
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(html, encoding="utf-8", newline="\n")
        print(f"gravado {destino.relative_to(RAIZ)} ({len(html) // 1024} KB)")
    print(f"{len(dicionario)} palavras no dicionário, {len(monstro)} do monstro, {len(silabas)} no modo sílabas")


if __name__ == "__main__":
    main()
