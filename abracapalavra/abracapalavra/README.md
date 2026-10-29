# Abracapalavra

Jogo educativo de formar palavras para as aulas de informática educativa.

O xamã enfrenta um monstro por fase. Os dois formam palavras ao mesmo tempo, cada um no seu quadro, e quem forma a palavra lança um poder no outro. Quanto maior a palavra, mais forte o poder. A cada fase o monstro monta palavras mais rápido.

- **Dois modos:** letras (monta a palavra letra por letra) e sílabas (junta pedaços: CA + SA).
- **10 fases**, cada uma com um monstro e um cenário. Uma fase só abre depois de vencer a anterior. O progresso fica salvo no computador.
- **Relatório no fim da fase:** tempo, palavras certas, maior palavra, dano causado, palavras do monstro e tentativas que não eram palavras. O botão "Copiar relatório" copia tudo como texto.
- **Ritmo calmo:** deixa o monstro bem mais lento (no menu ou na tela de pausa).
- Funciona **sem internet**, no computador, no tablet e no celular.

## Como jogar

| Onde | O que abrir |
| --- | --- |
| Qualquer navegador | `index.html` (dois cliques no arquivo) |
| Windows 10 ou 11 | `executaveis/Abracapalavra-Windows.exe` |
| Windows de 32 bits | `executaveis/Abracapalavra-Windows-32bits.exe` |
| Linux | extraia `executaveis/Abracapalavra-Linux.tar.gz` e abra `Abracapalavra` |
| Mac | extraia `executaveis/Abracapalavra-Mac.zip` e abra `Abracapalavra.app` |

Os executáveis abrem o jogo numa janela própria, sem barra de endereço, usando o Edge ou o Chrome que já estão no computador. Se nenhum dos dois estiver instalado, o jogo abre no navegador padrão.

**Teclado (modo letras):** digite as letras, `Enter` lança o poder, `Backspace` apaga a última peça e `Esc` limpa a palavra.

### Avisos na primeira vez

- **Windows:** o SmartScreen pode mostrar "O Windows protegeu o computador", porque o programa não tem assinatura digital. Clique em **Mais informações** e depois em **Executar assim mesmo**.
- **Mac:** o macOS pode bloquear o app de "desenvolvedor não identificado". Clique com o botão direito no app e escolha **Abrir**. Nas versões mais novas, vá em **Ajustes do Sistema → Privacidade e Segurança → Abrir mesmo assim**.
- **Computadores antigos (Windows 7 ou 8):** os executáveis precisam do Windows 10 ou mais novo. Nesses computadores, abra o `index.html` num navegador.

## Publicar no GitHub Pages (jogar pelo link)

1. No GitHub Desktop: **File → Add local repository**, escolha esta pasta e crie o repositório. Depois clique em **Publish repository** e desmarque **Keep this code private**, porque o GitHub Pages gratuito precisa de repositório público.
2. No site do GitHub, abra o repositório e vá em **Settings → Pages**.
3. Em **Build and deployment**, escolha **Source: Deploy from a branch**, **Branch: main** e a pasta **/ (root)**, e clique em **Save**.
4. Em alguns minutos o jogo estará em `https://SEU-USUARIO.github.io/NOME-DO-REPOSITORIO/`.

## Mudar as palavras

As listas ficam em arquivos de texto simples, uma palavra por linha (linhas com `#` são comentários):

- `codigo/dicionario.txt`: palavras que o jogo aceita. Acentos são ignorados, porque as peças não têm acento (maçã vale como MACA).
- `codigo/palavras-monstro.txt`: palavras que os monstros formam. Vale usar palavras simples e conhecidas da turma.
- `codigo/silabas.txt`: palavras do modo sílabas, com as sílabas separadas por hífen (`ca-sa`, `ba-na-na`).

Depois de editar, atualize o jogo:

```sh
python3 codigo/construir.py                      # atualiza o index.html
sh codigo/lancador/construir-executaveis.sh      # atualiza os executáveis (precisa do Go)
```

No Windows, o segundo comando roda pelo **Git Bash** (vem junto com o Git). O Go pode ser baixado em https://go.dev/dl/.

## Estrutura da pasta

```
index.html                  o jogo completo (versão para navegador e GitHub Pages)
executaveis/                versões para Windows, Linux e Mac
codigo/
  jogo.html                 modelo do jogo (visual, regras e fases)
  dicionario.txt            palavras aceitas
  palavras-monstro.txt      palavras dos monstros
  silabas.txt               palavras do modo sílabas
  construir.py              junta tudo no index.html
  fontes/                   fontes usadas no jogo e suas licenças
  lancador/                 código do executável (Go), ícones e script de build
```

As fases (nome do monstro, vida, velocidade e tamanho das palavras) ficam na lista `PHASES` dentro de `codigo/jogo.html`.

## Créditos e licenças

- **Fontes:** Andika (SIL International) e Rowdies (The Rowdies Project Authors), sob a SIL Open Font License 1.1; Luckiest Guy (Astigmatic), sob a Apache License 2.0. Os textos das licenças estão em `codigo/fontes/`.
- **Dicionário:** derivado da lista `pt_br_50k` do projeto [FrequencyWords](https://github.com/hermitdave/FrequencyWords), de Hermit Dave, baseada no OpenSubtitles, sob a licença [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). A lista foi filtrada (sem palavras estrangeiras, nomes próprios e palavrões) e teve os acentos removidos. Por isso, o `codigo/dicionario.txt` segue a mesma licença.
- Personagens, monstros, cenários e código: criados para este projeto.
