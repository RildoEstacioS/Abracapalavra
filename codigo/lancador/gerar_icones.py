#!/usr/bin/env python3
"""Gera os ícones dos executáveis a partir de icone/icone-<tamanho>.png.

Saídas:
  icone/icone.ico               ícone do Windows (arquivo solto)
  icone/icone.icns              ícone do Mac
  rsrc_windows_amd64.syso       recurso que o Go embute no .exe (64 bits)
  rsrc_windows_386.syso         recurso que o Go embute no .exe (32 bits)

Só usa a biblioteca padrão do Python. Os PNG são desenhados a partir de icone/icone.svg
(qualquer programa serve: Inkscape, navegador, etc.).
"""
import pathlib
import struct
import zlib

AQUI = pathlib.Path(__file__).resolve().parent
ICONE = AQUI / "icone"
TAMANHOS_WIN = [16, 24, 32, 48, 64, 128, 256]


# ---------- PNG -> RGBA (PNG 8 bits RGBA, sem entrelaçamento) ----------
def ler_png(caminho):
    dados = caminho.read_bytes()
    assert dados[:8] == b"\x89PNG\r\n\x1a\n", caminho
    pos, idat, largura = 8, b"", 0
    while pos < len(dados):
        n, tipo = struct.unpack(">I4s", dados[pos:pos + 8])
        bloco = dados[pos + 8:pos + 8 + n]
        if tipo == b"IHDR":
            largura, altura, prof, cor, _, _, entrel = struct.unpack(">IIBBBBB", bloco)
            assert prof == 8 and cor == 6 and entrel == 0, "use PNG RGBA 8 bits"
        elif tipo == b"IDAT":
            idat += bloco
        pos += 12 + n
    bruto = zlib.decompress(idat)
    bpp, passo = 4, largura * 4
    linhas, anterior, i = [], bytearray(passo), 0
    for _ in range(altura):
        filtro, linha = bruto[i], bytearray(bruto[i + 1:i + 1 + passo])
        i += 1 + passo
        for x in range(passo):
            a = linha[x - bpp] if x >= bpp else 0
            b = anterior[x]
            c = anterior[x - bpp] if x >= bpp else 0
            if filtro == 1:
                linha[x] = (linha[x] + a) & 255
            elif filtro == 2:
                linha[x] = (linha[x] + b) & 255
            elif filtro == 3:
                linha[x] = (linha[x] + (a + b) // 2) & 255
            elif filtro == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                linha[x] = (linha[x] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        linhas.append(bytes(linha))
        anterior = linha
    return largura, altura, linhas


def dib(caminho):
    """Imagem do ícone no formato BMP de 32 bits que o Windows usa dentro do .ico."""
    largura, altura, linhas = ler_png(caminho)
    cabecalho = struct.pack("<IiiHHIIiiII", 40, largura, altura * 2, 1, 32, 0, 0, 0, 0, 0, 0)
    pixels = b"".join(
        bytes(v for px in range(largura) for v in (linha[px * 4 + 2], linha[px * 4 + 1], linha[px * 4], linha[px * 4 + 3]))
        for linha in reversed(linhas)
    )
    mascara = bytes(((largura + 31) // 32) * 4 * altura)
    return cabecalho + pixels + mascara


def imagens_windows():
    out = []
    for t in TAMANHOS_WIN:
        png = ICONE / f"icone-{t}.png"
        out.append((t, png.read_bytes() if t >= 256 else dib(png)))
    return out


def gerar_ico(imagens):
    cab = struct.pack("<HHH", 0, 1, len(imagens))
    pos = 6 + 16 * len(imagens)
    entradas, corpo = b"", b""
    for t, dado in imagens:
        entradas += struct.pack("<BBBBHHII", t % 256, t % 256, 0, 0, 1, 32, len(dado), pos + len(corpo))
        corpo += dado
    (ICONE / "icone.ico").write_bytes(cab + entradas + corpo)


# ---------- recurso COFF (.syso) para o linker do Go ----------
def gerar_syso(imagens, maquina, tipo_reloc, destino):
    grupo = struct.pack("<HHH", 0, 1, len(imagens)) + b"".join(
        struct.pack("<BBBBHHIH", t % 256, t % 256, 0, 0, 1, 32, len(d), i + 1) for i, (t, d) in enumerate(imagens)
    )
    tipos = [(3, [(i + 1, d) for i, (_, d) in enumerate(imagens)]),  # RT_ICON
             (14, [(1, grupo)])]                                      # RT_GROUP_ICON
    # posições das tabelas
    pos = 16 + 8 * len(tipos)
    pos_nomes = []
    for _, nomes in tipos:
        pos_nomes.append(pos)
        pos += 16 + 8 * len(nomes)
    pos_idiomas = []
    for _, nomes in tipos:
        pos_idiomas.append([])
        for _ in nomes:
            pos_idiomas[-1].append(pos)
            pos += 16 + 8
    pos_entradas = []
    for _, nomes in tipos:
        pos_entradas.append([])
        for _ in nomes:
            pos_entradas[-1].append(pos)
            pos += 16
    pos_dados = []
    for _, nomes in tipos:
        pos_dados.append([])
        for _, d in nomes:
            pos = (pos + 7) & ~7
            pos_dados[-1].append(pos)
            pos += len(d)
    sec = bytearray(pos)

    def diretorio(onde, entradas):
        struct.pack_into("<IIHHHH", sec, onde, 0, 0, 0, 0, 0, len(entradas))
        for k, (ident, alvo) in enumerate(entradas):
            struct.pack_into("<II", sec, onde + 16 + 8 * k, ident, alvo)

    diretorio(0, [(t, 0x80000000 | pos_nomes[i]) for i, (t, _) in enumerate(tipos)])
    relocs = []
    for i, (_, nomes) in enumerate(tipos):
        diretorio(pos_nomes[i], [(n, 0x80000000 | pos_idiomas[i][j]) for j, (n, _) in enumerate(nomes)])
        for j, (_, d) in enumerate(nomes):
            diretorio(pos_idiomas[i][j], [(0x0409, pos_entradas[i][j])])
            struct.pack_into("<IIII", sec, pos_entradas[i][j], pos_dados[i][j], len(d), 0, 0)
            relocs.append(pos_entradas[i][j])
            sec[pos_dados[i][j]:pos_dados[i][j] + len(d)] = d

    inicio_dados = 20 + 40
    inicio_relocs = inicio_dados + len(sec)
    inicio_simbolos = inicio_relocs + 10 * len(relocs)
    arq = struct.pack("<HHIIIHH", maquina, 1, 0, inicio_simbolos, 1, 0, 0)
    arq += struct.pack("<8sIIIIIIHHI", b".rsrc", 0, 0, len(sec), inicio_dados, inicio_relocs, 0, len(relocs), 0, 0x40000040)
    arq += bytes(sec)
    arq += b"".join(struct.pack("<IIH", r, 0, tipo_reloc) for r in relocs)
    arq += struct.pack("<8sIhHBB", b".rsrc", 0, 1, 0, 3, 0) + struct.pack("<I", 4)
    destino.write_bytes(arq)


# ---------- ícone do Mac ----------
def gerar_icns():
    blocos = [(b"ic11", 32), (b"ic12", 64), (b"ic07", 128), (b"ic13", 256), (b"ic08", 256), (b"ic14", 512), (b"ic09", 512)]
    corpo = b"".join(tipo + struct.pack(">I", 8 + len(d)) + d
                     for tipo, t in blocos for d in [(ICONE / f"icone-{t}.png").read_bytes()])
    (ICONE / "icone.icns").write_bytes(b"icns" + struct.pack(">I", 8 + len(corpo)) + corpo)


if __name__ == "__main__":
    imgs = imagens_windows()
    gerar_ico(imgs)
    gerar_syso(imgs, 0x8664, 3, AQUI / "rsrc_windows_amd64.syso")  # IMAGE_REL_AMD64_ADDR32NB
    gerar_syso(imgs, 0x014C, 7, AQUI / "rsrc_windows_386.syso")    # IMAGE_REL_I386_DIR32NB
    gerar_icns()
    print("ícones gerados")
