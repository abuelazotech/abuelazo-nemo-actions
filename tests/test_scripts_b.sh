#!/bin/bash
set -uo pipefail
RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BIN="$RAIZ/src/bin"
TMP=$(mktemp -d)
trap 'rm -rf -- "$TMP"' EXIT
STUBS="$TMP/bin"
DATOS="$TMP/datos"
mkdir -p "$STUBS" "$DATOS"
export ABUELAZO_LIB_DIR="$RAIZ/src/lib"
export PATH="$STUBS:$PATH"
export TMP
export FFMPEG_LOG="$TMP/ffmpeg.log"
export CHMOD_LOG="$TMP/chmod.log"
export MV_LOG="$TMP/mv.log"
export CP_LOG="$TMP/cp.log"
: >"$FFMPEG_LOG"
: >"$CHMOD_LOG"
: >"$MV_LOG"
: >"$CP_LOG"

fallo() {
  printf 'FALLO: %s\n' "$1" >&2
  exit 1
}

paso() {
  printf 'CORRECTO: %s\n' "$1"
}

comprobar() {
  [[ -e $1 ]] || fallo "$2"
}

ejecutar() {
  if ! "$@" >>"$TMP/salida.log" 2>&1; then
    printf 'FALLO: %s\n' "$*" >&2
    cat "$TMP/salida.log" >&2
    exit 1
  fi
}

cat >"$STUBS/notify-send" <<'EOF'
#!/bin/bash
printf '%s\n' "$*" >> "$TMP/notify.log"
exit 0
EOF

cat >"$STUBS/zenity" <<'EOF'
#!/bin/bash
TEXTO=''
for ARGUMENTO in "$@"; do
  case "$ARGUMENTO" in
    --text=*) TEXTO="${ARGUMENTO#--text=}" ;;
  esac
done
ARGUMENTOS=" $* "
if [[ $ARGUMENTOS == *' --question '* ]]; then
  exit 0
fi
if [[ $ARGUMENTOS == *' --entry '* ]]; then
  case "$TEXTO" in
    *Inicio*) printf '%s\n' '0' ;;
    *Duración*) printf '%s\n' '5' ;;
    *Duracion*) printf '%s\n' '5' ;;
    *intervalo*) printf '%s\n' '2' ;;
    *Intervalo*) printf '%s\n' '2' ;;
    *'Texto de la marca de agua'*) printf '%s\n' 'Abuelazo Tech' ;;
    *) printf '%s\n' '1' ;;
  esac
  exit 0
fi
if [[ $ARGUMENTOS == *' --list '* && $ARGUMENTOS == *' --radiolist '* ]]; then
  printf '%s\n' '90'
  exit 0
fi
exit 0
EOF

cat >"$STUBS/ffmpeg" <<'EOF'
#!/bin/bash
printf '%s\n' "$*" >> "$FFMPEG_LOG"
SALIDA="${@: -1}"
if [[ $SALIDA == *%04d* ]]; then
  SALIDA="${SALIDA//%04d/0001}"
fi
DIRECTORIO="${SALIDA%/*}"
if [[ $DIRECTORIO != "$SALIDA" ]]; then
  mkdir -p -- "$DIRECTORIO"
fi
printf 'contenido\n' > "$SALIDA"
exit 0
EOF

cat >"$STUBS/pdfunite" <<'EOF'
#!/bin/bash
SALIDA="${@: -1}"
printf 'contenido\n' > "$SALIDA"
exit 0
EOF

cat >"$STUBS/pdftoppm" <<'EOF'
#!/bin/bash
PREFIJO="${@: -1}"
printf 'contenido\n' > "${PREFIJO}-1.png"
exit 0
EOF

cat >"$STUBS/libreoffice" <<'EOF'
#!/bin/bash
OUTDIR=''
OMITIR=0
ARGOS=("$@")
for ((INDICE=0; INDICE<${#ARGOS[@]}; INDICE++)); do
  ARGUMENTO="${ARGOS[INDICE]}"
  if (( OMITIR > 0 )); then
    OMITIR=0
    continue
  fi
  case "$ARGUMENTO" in
    --outdir)
      OUTDIR="${ARGOS[INDICE+1]}"
      OMITIR=1
      ;;
    --convert-to)
      OMITIR=1
      ;;
    -env:*) ;;
    --headless) ;;
    pdf) ;;
    *)
      if [[ -n $OUTDIR && -f $ARGUMENTO ]]; then
        NOMBRE="${ARGUMENTO##*/}"
        BASE="${NOMBRE%.*}"
        printf 'contenido\n' > "$OUTDIR/$BASE.pdf"
      fi
      ;;
  esac
done
exit 0
EOF

cat >"$STUBS/cwebp" <<'EOF'
#!/bin/bash
SALIDA=''
ANTERIOR=''
for ARGUMENTO in "$@"; do
  if [[ $ANTERIOR == -o ]]; then
    SALIDA="$ARGUMENTO"
  fi
  ANTERIOR="$ARGUMENTO"
done
printf 'contenido\n' > "$SALIDA"
exit 0
EOF

cat >"$STUBS/convert" <<'EOF'
#!/bin/bash
SALIDA="${@: -1}"
printf 'contenido\n' > "$SALIDA"
exit 0
EOF

cat >"$STUBS/magick" <<'EOF'
#!/bin/bash
SALIDA="${@: -1}"
printf 'contenido\n' > "$SALIDA"
exit 0
EOF

cat >"$STUBS/chmod" <<'EOF'
#!/bin/bash
printf '%s\n' "$*" >> "$CHMOD_LOG"
exit 0
EOF

cat >"$STUBS/mv" <<'EOF'
#!/bin/bash
printf '%s\n' "$*" >> "$MV_LOG"
exec /bin/mv "$@"
EOF

cat >"$STUBS/cp" <<'EOF'
#!/bin/bash
printf '%s\n' "$*" >> "$CP_LOG"
exec /bin/cp "$@"
EOF

/bin/chmod +x "$STUBS"/*

: >"$DATOS/a.pdf"
: >"$DATOS/espacio pdf.pdf"
: >"$DATOS/combinado.pdf"
ejecutar "$BIN/abuelazo-unir-pdfs" "$DATOS/a.pdf" "file://$DATOS/espacio%20pdf.pdf"
comprobar "$DATOS/combinado-2.pdf" 'unir-pdfs no creó combinado-2.pdf'
paso 'abuelazo-unir-pdfs'

: >"$DATOS/doc1.odt"
: >"$DATOS/doc2.ods"
ejecutar "$BIN/abuelazo-documento-a-pdf" "$DATOS/doc1.odt" "$DATOS/doc2.ods"
comprobar "$DATOS/doc1.pdf" 'documento-a-pdf no creó doc1.pdf'
comprobar "$DATOS/doc2.pdf" 'documento-a-pdf no creó doc2.pdf'
paso 'abuelazo-documento-a-pdf'

: >"$DATOS/pdf1.pdf"
ejecutar "$BIN/abuelazo-pdf-a-imagenes" "$DATOS/pdf1.pdf"
comprobar "$DATOS/pdf1_imagenes/pagina-1.png" 'pdf-a-imagenes no creó la imagen'
paso 'abuelazo-pdf-a-imagenes'

: >"$DATOS/img1.png"
: >"$DATOS/img2.jpg"
ejecutar "$BIN/abuelazo-comprimir-webp" "$DATOS/img1.png" "$DATOS/img2.jpg"
comprobar "$DATOS/img1.webp" 'comprimir-webp no creó img1.webp'
comprobar "$DATOS/img2.webp" 'comprimir-webp no creó img2.webp'
paso 'abuelazo-comprimir-webp'

: >"$DATOS/video1.mp4"
ejecutar "$BIN/abuelazo-video-a-gif" "$DATOS/video1.mp4"
comprobar "$DATOS/video1.gif" 'video-a-gif no creó el GIF'
grep -F -- '-ss 0' "$FFMPEG_LOG" >/dev/null || fallo 'video-a-gif no pasó -ss 0'
grep -F -- '-t 5' "$FFMPEG_LOG" >/dev/null || fallo 'video-a-gif no pasó -t 5'
paso 'abuelazo-video-a-gif'

: >"$DATOS/video2.mkv"
ejecutar "$BIN/abuelazo-extraer-frames" "$DATOS/video2.mkv"
comprobar "$DATOS/video2_frames/frame_0001.png" 'extraer-frames no creó los fotogramas'
paso 'abuelazo-extraer-frames'

: >"$DATOS/img3.webp"
ejecutar "$BIN/abuelazo-marca-agua" "$DATOS/img1.png" "$DATOS/img3.webp"
comprobar "$DATOS/img1_marcada.jpg" 'marca-agua no creó la imagen JPG'
comprobar "$DATOS/img3_marcada.webp" 'marca-agua no creó la imagen WebP'
paso 'abuelazo-marca-agua'

ejecutar "$BIN/abuelazo-rotar-imagenes" "$DATOS/img2.jpg"
comprobar "$DATOS/img2_rotada.jpg" 'rotar-imagenes no creó la imagen rotada'
paso 'abuelazo-rotar-imagenes'

: >"$DATOS/perm1.txt"
: >"$DATOS/perm2.txt"
ejecutar "$BIN/abuelazo-permisos" 755 "$DATOS/perm1.txt" "$DATOS/perm2.txt"
grep -F -- '755' "$CHMOD_LOG" >/dev/null || fallo 'permisos no aplicó el modo 755'
paso 'abuelazo-permisos 755'

printf 'CORRECTO: todas las pruebas terminaron bien\n'
