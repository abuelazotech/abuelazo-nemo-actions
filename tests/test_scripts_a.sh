#!/bin/bash
set -uo pipefail
ORIGEN="${BASH_SOURCE[0]}"
RAIZ=$(cd -- "$(dirname -- "$ORIGEN")/.." && pwd)
export ABUELAZO_LIB_DIR="$RAIZ/src/lib"
LIB="${ABUELAZO_LIB_DIR:-/usr/share/abuelazo-nemo-actions/lib}/abuelazo-common.sh"
[[ -f $LIB ]] || { printf 'FALLO: no se encontró la librería común.\n' >&2; exit 1; }
. "$LIB"

TMP=$(mktemp -d)
trap 'rm -rf -- "$TMP"' EXIT
BIN="$TMP/bin"
mkdir -p -- "$BIN"

cat > "$BIN/notify-send" <<'EOF'
exit 0
EOF

cat > "$BIN/zenity" <<'EOF'
case " $* " in
  *" --question "*) exit 0 ;;
  *" --entry "*) printf '%s\n' 'Serie'; exit 0 ;;
  *" --password "*) printf '%s\n' 'clave-prueba'; exit 0 ;;
  *" --text-info "*) exit 0 ;;
  *) exit 0 ;;
esac
EOF

cat > "$BIN/xdg-open" <<'EOF'
exit 0
EOF

cat > "$BIN/gdbus" <<'EOF'
exit 0
EOF

cat > "$BIN/python3" <<'EOF'
valor="${!#}"
valor="${valor#file://}"
printf '%b\n' "${valor//%/\\x}"
EOF

cat > "$BIN/ffmpeg" <<'EOF'
salida="${!#}"
: > "$salida"
exit 0
EOF

cat > "$BIN/convert" <<'EOF'
salida="${!#}"
: > "$salida"
exit 0
EOF

cat > "$BIN/magick" <<'EOF'
salida="${!#}"
: > "$salida"
exit 0
EOF

cat > "$BIN/exiftool" <<'EOF'
exit 0
EOF

cat > "$BIN/gpg" <<'EOF'
salida=''
while [[ $# -gt 0 ]]; do
  if [[ $1 == --output ]]; then
    shift
    salida="${1:-}"
  fi
  shift
done
[[ -z $salida ]] || : > "$salida"
exit 0
EOF

cat > "$BIN/tree" <<'EOF'
salida=''
while [[ $# -gt 0 ]]; do
  if [[ $1 == -o ]]; then
    shift
    salida="${1:-}"
  fi
  shift
done
[[ -z $salida ]] || : > "$salida"
exit 0
EOF

cat > "$BIN/find" <<'EOF'
exec /usr/bin/find "$@"
EOF

cat > "$BIN/mv" <<'EOF'
forzar=0
origen=''
destino=''
for argumento in "$@"; do
  case "$argumento" in
    -f|--force) forzar=1 ;;
    -n|--no-clobber|--) ;;
    *)
      if [[ -z $origen ]]; then
        origen="$argumento"
      else
        destino="$argumento"
      fi
      ;;
  esac
done
[[ -n $origen && -n $destino ]] || exit 0
if [[ -e $destino && $forzar -eq 0 ]]; then
  exit 0
fi
exec /bin/mv -- "$origen" "$destino"
EOF

cat > "$BIN/du" <<'EOF'
if [[ ${1:-} == -k && ${!#} == *_miniatura*.jpg ]]; then
  printf '3000\t%s\n' "${!#}"
  exit 0
fi
exec /usr/bin/du "$@"
EOF

cat > "$BIN/wc" <<'EOF'
exec /usr/bin/wc "$@"
EOF

cat > "$BIN/cwebp" <<'EOF'
exit 0
EOF

cat > "$BIN/qrencode" <<'EOF'
salida=''
while [[ $# -gt 0 ]]; do
  if [[ $1 == -o ]]; then
    shift
    salida="${1:-}"
  fi
  shift
done
[[ -z $salida ]] || : > "$salida"
exit 0
EOF

cat > "$BIN/xclip" <<'EOF'
while IFS= read -r _linea; do
  :
done
exit 0
EOF

cat > "$BIN/realpath" <<'EOF'
exec /usr/bin/realpath "$@"
EOF

cat > "$BIN/diff" <<'EOF'
exec /usr/bin/diff "$@"
EOF

cat > "$BIN/meld" <<'EOF'
exit 0
EOF

cat > "$BIN/libreoffice" <<'EOF'
exit 0
EOF

chmod +x "$BIN"/*
export PATH="$BIN:$PATH"
SCRIPTS="$RAIZ/src/bin"
cd "$TMP" || exit 1

FALLOS=0
correcto() { printf 'CORRECTO: %s\n' "$1"; }
fallo() { printf 'FALLO: %s\n' "$1"; FALLOS=$((FALLOS + 1)); }

mkdir -p -- "$TMP/t1" "$TMP/t2" "$TMP/t3" "$TMP/t4/sub" "$TMP/t6" "$TMP/t7" "$TMP/t8" "$TMP/t10" "$TMP/t11" "$TMP/t12" "$TMP/t14" "$TMP/t15" "$TMP/t16" "$TMP/t17/sub" "$TMP/t18" "$TMP/t19"
printf 'contenido de prueba\n' > "$TMP/t1/origen.txt"
printf 'imagen' > "$TMP/t2/imagen.png"
printf 'secreto' > "$TMP/t3/secreto.txt"
printf 'x' > "$TMP/t6/MAYUS.TXT"
printf 'notas' > "$TMP/t7/notas.txt"
printf 'ruta' > "$TMP/t8/ruta.txt"
printf 'original' > "$TMP/t10/archivo.png"
printf 'uno' > "$TMP/t10/archivo.jpg"
printf 'dos' > "$TMP/t10/archivo-2.jpg"
printf 'video' > "$TMP/t11/video.png"
printf 'video' > "$TMP/t12/video.mkv"
printf 'cifrado' > "$TMP/t14/secreto.txt.gpg"
printf 'a' > "$TMP/t16/a.txt"
printf 'b' > "$TMP/t16/b.txt"
printf 'c' > "$TMP/t17/sub/c.txt"
printf 'a' > "$TMP/t19/a.txt"
printf 'b' > "$TMP/t19/b.txt"

if "$SCRIPTS/abuelazo-verificar-suma" "$TMP/t1/origen.txt" >/dev/null 2>&1; then
  correcto 'abuelazo-verificar-suma'
else
  fallo 'abuelazo-verificar-suma'
fi

if "$SCRIPTS/abuelazo-limpiar-exif" "$TMP/t2/imagen.png" >/dev/null 2>&1 && compgen -G "$TMP/t2/imagen_sin_exif*.png" >/dev/null; then
  correcto 'abuelazo-limpiar-exif'
else
  fallo 'abuelazo-limpiar-exif'
fi

if "$SCRIPTS/abuelazo-cifrar-archivo" "$TMP/t3/secreto.txt" >/dev/null 2>&1 && compgen -G "$TMP/t3/secreto.txt.gpg*" >/dev/null && [[ ! -f $TMP/t3/secreto.txt ]]; then
  correcto 'abuelazo-cifrar-archivo'
else
  fallo 'abuelazo-cifrar-archivo'
fi

if "$SCRIPTS/abuelazo-arbol-directorios" "$TMP/t4" >/dev/null 2>&1 && [[ -f $TMP/t4/estructura.txt ]]; then
  correcto 'abuelazo-arbol-directorios'
else
  fallo 'abuelazo-arbol-directorios'
fi

if "$SCRIPTS/abuelazo-contar-peso" "$TMP/t4" >/dev/null 2>&1; then
  correcto 'abuelazo-contar-peso'
else
  fallo 'abuelazo-contar-peso'
fi

if "$SCRIPTS/abuelazo-renombrar-case" lower "$TMP/t6/MAYUS.TXT" >/dev/null 2>&1 && [[ -f $TMP/t6/mayus.TXT ]] && [[ ! -e $TMP/t6/MAYUS.TXT ]]; then
  correcto 'abuelazo-renombrar-case lower'
else
  fallo 'abuelazo-renombrar-case lower'
fi

mkdir -p "$TMP/t7/proyecto"
if "$SCRIPTS/abuelazo-backup-fecha" "$TMP/t7/notas.txt" >/dev/null 2>&1 && compgen -G "$TMP/t7/notas_*.bak" >/dev/null && "$SCRIPTS/abuelazo-backup-fecha" "$TMP/t7/proyecto" >/dev/null 2>&1 && [[ -d $TMP/t7/proyecto_$(date +%F) ]]; then
  correcto 'abuelazo-backup-fecha'
else
  fallo 'abuelazo-backup-fecha'
fi

if "$SCRIPTS/abuelazo-copiar-ruta" "$TMP/t8/ruta.txt" >/dev/null 2>&1; then
  correcto 'abuelazo-copiar-ruta'
else
  fallo 'abuelazo-copiar-ruta'
fi

if "$SCRIPTS/abuelazo-imagen-jpg" "$TMP/t10/archivo.png" >/dev/null 2>&1 && [[ -f $TMP/t10/archivo-3.jpg ]] && [[ $(<"$TMP/t10/archivo.jpg") == 'uno' ]]; then
  correcto 'abuelazo-imagen-jpg sin sobrescribir'
else
  fallo 'abuelazo-imagen-jpg sin sobrescribir'
fi

if "$SCRIPTS/abuelazo-miniatura-youtube" "$TMP/t11/video.png" >/dev/null 2>&1 && compgen -G "$TMP/t11/video_miniatura*.jpg" >/dev/null; then
  correcto 'abuelazo-miniatura-youtube'
else
  fallo 'abuelazo-miniatura-youtube'
fi

if "$SCRIPTS/abuelazo-extraer-audio" "$TMP/t12/video.mkv" >/dev/null 2>&1 && compgen -G "$TMP/t12/video*.mp3" >/dev/null; then
  correcto 'abuelazo-extraer-audio'
else
  fallo 'abuelazo-extraer-audio'
fi

if "$SCRIPTS/abuelazo-mkv-mp4" "$TMP/t12/video.mkv" >/dev/null 2>&1 && compgen -G "$TMP/t12/video*.mp4" >/dev/null; then
  correcto 'abuelazo-mkv-mp4'
else
  fallo 'abuelazo-mkv-mp4'
fi

if "$SCRIPTS/abuelazo-descifrar-archivo" "$TMP/t14/secreto.txt.gpg" >/dev/null 2>&1 && [[ -f $TMP/t14/secreto.txt ]] && [[ ! -f $TMP/t14/secreto.txt.gpg ]]; then
  correcto 'abuelazo-descifrar-archivo'
else
  fallo 'abuelazo-descifrar-archivo'
fi

cd "$TMP/t15" || exit 1
if "$SCRIPTS/abuelazo-generar-qr" >/dev/null 2>&1 && [[ -f qr_serie.png ]]; then
  correcto 'abuelazo-generar-qr'
else
  fallo 'abuelazo-generar-qr'
fi
cd "$TMP" || exit 1

if "$SCRIPTS/abuelazo-renombrar-serie" "$TMP/t16/a.txt" "$TMP/t16/b.txt" >/dev/null 2>&1 && [[ -f $TMP/t16/Serie_001.txt ]] && [[ -f $TMP/t16/Serie_002.txt ]]; then
  correcto 'abuelazo-renombrar-serie'
else
  fallo 'abuelazo-renombrar-serie'
fi

if "$SCRIPTS/abuelazo-aplanar-carpeta" "$TMP/t17" >/dev/null 2>&1 && [[ -f $TMP/t17/c.txt ]] && [[ ! -e $TMP/t17/sub/c.txt ]]; then
  correcto 'abuelazo-aplanar-carpeta'
else
  fallo 'abuelazo-aplanar-carpeta'
fi

if "$SCRIPTS/abuelazo-nuevo-documento" odt "$TMP/t18" >/dev/null 2>&1 && [[ -f $TMP/t18/Nuevo_Documento.odt ]] && "$SCRIPTS/abuelazo-nuevo-documento" odg "$TMP/t18" >/dev/null 2>&1 && [[ -f $TMP/t18/Nuevo_Dibujo.odg ]] && "$SCRIPTS/abuelazo-nuevo-documento" odf "$TMP/t18" >/dev/null 2>&1 && [[ -f $TMP/t18/Nueva_Formula.odf ]] && "$SCRIPTS/abuelazo-nuevo-documento" odb "$TMP/t18" >/dev/null 2>&1 && [[ -f $TMP/t18/Nueva_Base_De_Datos.odb ]]; then
  correcto 'abuelazo-nuevo-documento'
else
  fallo 'abuelazo-nuevo-documento'
fi

if "$SCRIPTS/abuelazo-comparar-archivos" "$TMP/t19/a.txt" "$TMP/t19/b.txt" >/dev/null 2>&1; then
  correcto 'abuelazo-comparar-archivos'
else
  fallo 'abuelazo-comparar-archivos'
fi

if (( FALLOS == 0 )); then
  printf 'CORRECTO: todas las pruebas pasaron\n'
  exit 0
fi
printf 'FALLO: %d pruebas fallaron\n' "$FALLOS"
exit 1
