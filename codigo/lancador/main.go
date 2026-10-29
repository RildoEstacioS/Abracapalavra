// Lançador do Abracapalavra.
//
// O jogo inteiro é um único arquivo HTML (web/index.html), embutido neste executável.
// Ao abrir, o lançador grava esse arquivo na pasta do usuário e abre numa janela de
// aplicativo do Edge ou do Chrome (sem barra de endereço). Se nenhum dos dois existir,
// abre no navegador padrão. O progresso fica salvo no próprio navegador.
package main

import (
	_ "embed"
	"net/url"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
)

//go:embed web/index.html
var jogo []byte

func main() {
	arquivo, err := gravarJogo()
	if err != nil {
		os.Exit(1)
	}
	endereco := enderecoArquivo(arquivo)
	if abrirComoAplicativo(endereco) {
		return
	}
	abrirNoNavegadorPadrao(arquivo)
}

// gravarJogo copia o HTML para uma pasta fixa do usuário (sempre a mesma, para o
// navegador lembrar o progresso entre uma partida e outra).
func gravarJogo() (string, error) {
	var pastas []string
	if d, err := os.UserCacheDir(); err == nil {
		pastas = append(pastas, filepath.Join(d, "Abracapalavra"))
	}
	pastas = append(pastas, filepath.Join(os.TempDir(), "Abracapalavra"))
	var ultimo error
	for _, pasta := range pastas {
		if err := os.MkdirAll(pasta, 0o755); err != nil {
			ultimo = err
			continue
		}
		caminho := filepath.Join(pasta, "abracapalavra.html")
		if err := os.WriteFile(caminho, jogo, 0o644); err != nil {
			ultimo = err
			continue
		}
		return caminho, nil
	}
	return "", ultimo
}

func enderecoArquivo(caminho string) string {
	p := filepath.ToSlash(caminho)
	if runtime.GOOS == "windows" {
		p = "/" + p // C:/Users/... vira file:///C:/Users/...
	}
	return (&url.URL{Scheme: "file", Path: p}).String()
}

func navegadoresComJanelaDeApp() []string {
	switch runtime.GOOS {
	case "windows":
		var edge, chrome []string
		for _, variavel := range []string{"ProgramFiles(x86)", "ProgramFiles", "LocalAppData"} {
			base := os.Getenv(variavel)
			if base == "" {
				continue
			}
			edge = append(edge, filepath.Join(base, "Microsoft", "Edge", "Application", "msedge.exe"))
			chrome = append(chrome, filepath.Join(base, "Google", "Chrome", "Application", "chrome.exe"))
		}
		return append(edge, chrome...)
	case "darwin":
		return []string{
			"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
			"/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
			"/Applications/Chromium.app/Contents/MacOS/Chromium",
			"/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
		}
	default:
		var achados []string
		for _, nome := range []string{"google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "microsoft-edge", "microsoft-edge-stable", "brave-browser"} {
			if p, err := exec.LookPath(nome); err == nil {
				achados = append(achados, p)
			}
		}
		return achados
	}
}

func abrirComoAplicativo(endereco string) bool {
	for _, navegador := range navegadoresComJanelaDeApp() {
		if info, err := os.Stat(navegador); err != nil || info.IsDir() {
			continue
		}
		cmd := exec.Command(navegador, "--app="+endereco, "--start-maximized", "--no-first-run", "--no-default-browser-check")
		if err := cmd.Start(); err == nil {
			_ = cmd.Process.Release()
			return true
		}
	}
	return false
}

func abrirNoNavegadorPadrao(caminho string) {
	var cmd *exec.Cmd
	switch runtime.GOOS {
	case "windows":
		cmd = exec.Command("rundll32", "url.dll,FileProtocolHandler", caminho)
	case "darwin":
		cmd = exec.Command("open", caminho)
	default:
		cmd = exec.Command("xdg-open", caminho)
	}
	if err := cmd.Start(); err == nil {
		_ = cmd.Process.Release()
	}
}
