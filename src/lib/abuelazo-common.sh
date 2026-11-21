ABA_TITULO='El Abuelazo Tech'

aba_notificar() {
  local titulo="${1:-$ABA_TITULO}"
  local mensaje="${2:-}"
  if command -v notify-send >/dev/null 2>&1; then
    if ! notify-send "$titulo" "$mensaje"; then
      printf '%s: %s\n' "$titulo" "$mensaje" >&2
    fi
  else
    printf '%s: %s\n' "$titulo" "$mensaje" >&2
  fi
}

aba_error() {
  local mensaje="${1:-Error}"
  printf 'Error: %s\n' "$mensaje" >&2
  aba_notificar "$ABA_TITULO" "Error: $mensaje"
  exit 1
}

aba_requerir() {
  local faltantes=()
  local programa
  for programa in "$@"; do
    command -v "$programa" >/dev/null 2>&1 || faltantes+=("$programa")
  done
  if (( ${#faltantes[@]} > 0 )); then
    aba_error "Faltan programas necesarios: ${faltantes[*]}"
  fi
}

aba_decodificar_uri() {
  local valor="${1:-}"
  if [[ $valor == file://* ]]; then
    python3 -c 'import sys,urllib.parse; print(urllib.parse.unquote(sys.argv[1][7:]))' "$valor"
  else
    printf '%s\n' "$valor"
  fi
}

aba_log_temporal() {
  local prefijo="${1:-accion}"
  mktemp "${TMPDIR:-/tmp}/abuelazo-${prefijo}-XXXXXX.log"
}

aba_salida_unica() {
  local base="$1"
  local extension="$2"
  local salida="$base"
  [[ -n $extension ]] && salida="${base}.${extension}"
  local numero=2
  while [[ -e $salida ]]; do
    if [[ -n $extension ]]; then
      salida="${base}-${numero}.${extension}"
    else
      salida="${base}-${numero}"
    fi
    numero=$((numero + 1))
  done
  printf '%s\n' "$salida"
}

aba_salida_unica_sufijo() {
  local base="$1"
  local sufijo="$2"
  local extension="$3"
  local nombre="${base}${sufijo}"
  local salida="$nombre"
  [[ -n $extension ]] && salida="${nombre}.${extension}"
  local numero=2
  while [[ -e $salida ]]; do
    if [[ -n $extension ]]; then
      salida="${nombre}-${numero}.${extension}"
    else
      salida="${nombre}-${numero}"
    fi
    numero=$((numero + 1))
  done
  printf '%s\n' "$salida"
}

aba_requerir_args() {
  local minimo="$1"
  local maximo="$2"
  local cantidad="$3"
  if (( cantidad < minimo || cantidad > maximo )); then
    aba_error "Esta acción necesita entre ${minimo} y ${maximo} elementos seleccionados."
  fi
}

aba_confirmar() {
  local texto="$1"
  command -v zenity >/dev/null 2>&1 || return 2
  zenity --question --title="$ABA_TITULO" --text="$texto" --ok-label='Aceptar' --cancel-label='Cancelar'
}

aba_entrada() {
  local texto="$1"
  local inicial="${2:-}"
  command -v zenity >/dev/null 2>&1 || return 2
  zenity --entry --title="$ABA_TITULO" --text="$texto" --entry-text="$inicial"
}

aba_contrasena() {
  local texto="$1"
  command -v zenity >/dev/null 2>&1 || return 2
  zenity --password --title="$ABA_TITULO" --text="$texto"
}

aba_mensaje() {
  local texto="$1"
  command -v zenity >/dev/null 2>&1 || return 2
  zenity --info --title="$ABA_TITULO" --text="$texto"
}

aba_mostrar_elemento() {
  local ruta="$1"
  local uri=''
  if command -v gdbus >/dev/null 2>&1 && command -v python3 >/dev/null 2>&1; then
    uri=$(python3 -c 'import pathlib,sys; print(pathlib.Path(sys.argv[1]).resolve().as_uri())' "$ruta") || uri=''
    if [[ -n $uri ]] && gdbus call --session --dest org.freedesktop.FileManager1 --object-path /org/freedesktop/FileManager1 --method org.freedesktop.FileManager1.ShowItems "['$uri']" '' >/dev/null 2>&1; then
      return 0
    fi
  fi
  if command -v nemo >/dev/null 2>&1; then
    if [[ -d $ruta ]]; then
      nemo "$ruta" >/dev/null 2>&1
    else
      nemo "$(dirname -- "$ruta")" >/dev/null 2>&1
    fi
  elif command -v xdg-open >/dev/null 2>&1; then
    if [[ -d $ruta ]]; then
      xdg-open "$ruta" >/dev/null 2>&1
    else
      xdg-open "$(dirname -- "$ruta")" >/dev/null 2>&1
    fi
  fi
}

aba_resultado() {
  local mensaje="$1"
  local ruta="$2"
  local etiqueta='Ir al archivo'
  local pregunta='¿Deseas ir al archivo?'
  if [[ -d $ruta ]]; then
    etiqueta='Ir a la carpeta'
    pregunta='¿Deseas ir a la carpeta?'
  fi
  local texto="Hecho: $mensaje
Ubicación: $ruta

$pregunta"
  if command -v zenity >/dev/null 2>&1; then
    if zenity --question --title="$ABA_TITULO" --text="$texto" --ok-label="$etiqueta" --cancel-label='Cerrar'; then
      aba_mostrar_elemento "$ruta"
      return 0
    fi
  fi
  aba_notificar "$ABA_TITULO" "$mensaje - $ruta"
}

aba_cargar() {
  local directorio="${ABUELAZO_LIB_DIR:-/usr/share/abuelazo-nemo-actions/lib}"
  if [[ ! -f ${directorio}/abuelazo-common.sh ]]; then
    printf 'No se encontró la librería común de Abuelazo.\n' >&2
    return 1
  fi
  return 0
}
