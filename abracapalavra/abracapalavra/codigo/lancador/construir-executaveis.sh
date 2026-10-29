#!/bin/sh
# Gera os executáveis do Abracapalavra na pasta executaveis/ da raiz.
# Precisa do Go (1.22 ou mais novo), do Python 3, do tar e do zip.
# No Windows, rode pelo Git Bash.
set -e
cd "$(dirname "$0")"
LANCADOR="$(pwd)"
SAIDA="$(cd ../.. && pwd)/executaveis"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

python3 ../construir.py
mkdir -p "$SAIDA"
export CGO_ENABLED=0
OPCOES="-trimpath"

echo "Windows..."
GOOS=windows GOARCH=amd64 go build $OPCOES -ldflags "-s -w -H windowsgui" -o "$SAIDA/Abracapalavra-Windows.exe" .
GOOS=windows GOARCH=386   go build $OPCOES -ldflags "-s -w -H windowsgui" -o "$SAIDA/Abracapalavra-Windows-32bits.exe" .

echo "Linux..."
mkdir -p "$TMP/Abracapalavra"
GOOS=linux GOARCH=amd64 go build $OPCOES -ldflags "-s -w" -o "$TMP/Abracapalavra/Abracapalavra" .
cp icone/icone-256.png "$TMP/Abracapalavra/abracapalavra.png"
chmod 755 "$TMP/Abracapalavra/Abracapalavra"
tar -C "$TMP" -czf "$SAIDA/Abracapalavra-Linux.tar.gz" Abracapalavra

echo "Mac..."
APP="$TMP/Abracapalavra.app/Contents"
mkdir -p "$APP/MacOS" "$APP/Resources"
GOOS=darwin GOARCH=arm64 go build $OPCOES -ldflags "-s -w" -o "$APP/MacOS/abracapalavra-arm64" .
GOOS=darwin GOARCH=amd64 go build $OPCOES -ldflags "-s -w" -o "$APP/MacOS/abracapalavra-amd64" .
cat > "$APP/MacOS/Abracapalavra" <<'EOF'
#!/bin/sh
DIR="$(cd "$(dirname "$0")" && pwd)"
if [ "$(uname -m)" = "arm64" ]; then exec "$DIR/abracapalavra-arm64"; else exec "$DIR/abracapalavra-amd64"; fi
EOF
chmod 755 "$APP/MacOS/"*
cp icone/icone.icns "$APP/Resources/icone.icns"
cat > "$APP/Info.plist" <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleName</key><string>Abracapalavra</string>
  <key>CFBundleDisplayName</key><string>Abracapalavra</string>
  <key>CFBundleIdentifier</key><string>local.abracapalavra.jogo</string>
  <key>CFBundleVersion</key><string>1.0</string>
  <key>CFBundleShortVersionString</key><string>1.0</string>
  <key>CFBundleExecutable</key><string>Abracapalavra</string>
  <key>CFBundleIconFile</key><string>icone</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>LSMinimumSystemVersion</key><string>11.0</string>
</dict>
</plist>
EOF
rm -f "$SAIDA/Abracapalavra-Mac.zip"
(cd "$TMP" && zip -qry "$SAIDA/Abracapalavra-Mac.zip" Abracapalavra.app)

echo "Pronto: $SAIDA"
ls -l "$SAIDA"
