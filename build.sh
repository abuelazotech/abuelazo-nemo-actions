#!/bin/bash
set -Eeuo pipefail

VERSION=1.3-16
PAQUETE=abuelazo-nemo-actions
RAIZ="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
TRABAJO="$RAIZ/build"
DESTINO="$RAIZ/dist"
ARBOL="$TRABAJO/$PAQUETE"
INSTALAR=(install)

if (( EUID == 0 )); then
  INSTALAR+=(-o root -g root)
fi

requerir() {
  local fuente
  for fuente in "$@"; do
    if [[ ! -f "$RAIZ/$fuente" ]]; then
      printf 'Falta archivo fuente: %s\n' "$fuente" >&2
      exit 1
    fi
  done
}

requerir catalog.json \
  src/lib/abuelazo-common.sh \
  src/config/abuelazo-nemo-config \
  debian/changelog \
  debian/control \
  debian/copyright \
  debian/rules \
  debian/abuelazo-nemo-actions.conffiles \
  debian/abuelazo-nemo-actions.lintian-overrides \
  debian/triggers

shopt -s nullglob
binarios=("$RAIZ"/src/bin/*)
acciones=("$RAIZ"/src/actions/*.nemo_action)
escritorios=("$RAIZ"/src/config/*.desktop)
iconos=("$RAIZ"/src/icons/hicolor/*/apps/*.png)

if (( ${#binarios[@]} == 0 )); then
  printf 'Falta archivo fuente: src/bin/*\n' >&2
  exit 1
fi
if (( ${#acciones[@]} == 0 )); then
  printf 'Falta archivo fuente: src/actions/*.nemo_action\n' >&2
  exit 1
fi
if (( ${#escritorios[@]} != 2 )); then
  printf 'Se esperan dos archivos .desktop en src/config\n' >&2
  exit 1
fi
if (( ${#iconos[@]} == 0 )); then
  printf 'Falta archivo fuente: src/icons/hicolor/*/apps/*.png\n' >&2
  exit 1
fi

PRIMER_INICIO=''
for escritorio in "${escritorios[@]}"; do
  if [[ $escritorio == *first-run* ]]; then
    PRIMER_INICIO=$escritorio
  fi
done
if [[ -z $PRIMER_INICIO ]]; then
  printf 'Falta el .desktop de primer inicio en src/config\n' >&2
  exit 1
fi

rm -rf -- "$TRABAJO" "$DESTINO"
mkdir -p -- \
  "$ARBOL/DEBIAN" \
  "$ARBOL/usr/bin" \
  "$ARBOL/usr/share/abuelazo-nemo-actions/lib" \
  "$ARBOL/usr/share/abuelazo-nemo-actions/datos" \
  "$ARBOL/usr/share/abuelazo-nemo-actions/actions" \
  "$ARBOL/usr/share/applications" \
  "$ARBOL/etc/xdg/autostart" \
  "$ARBOL/usr/share/doc/abuelazo-nemo-actions" \
  "$ARBOL/usr/share/lintian/overrides" \
  "$DESTINO"

for binario in "${binarios[@]}"; do
  [[ -f $binario ]] || continue
  "${INSTALAR[@]}" -m 0755 -- "$binario" "$ARBOL/usr/bin/"
done
"${INSTALAR[@]}" -m 0644 -- "$RAIZ/src/lib/abuelazo-common.sh" \
  "$ARBOL/usr/share/abuelazo-nemo-actions/lib/abuelazo-common.sh"
"${INSTALAR[@]}" -m 0644 -- "$RAIZ/catalog.json" \
  "$ARBOL/usr/share/abuelazo-nemo-actions/catalog.json"
for accion in "${acciones[@]}"; do
  "${INSTALAR[@]}" -m 0644 -- "$accion" \
    "$ARBOL/usr/share/abuelazo-nemo-actions/actions/"
done
for icono in "${iconos[@]}"; do
  ruta_icono=${icono#"$RAIZ/src/icons/"}
  "${INSTALAR[@]}" -D -m 0644 -- "$icono" \
    "$ARBOL/usr/share/icons/$ruta_icono"
done
"${INSTALAR[@]}" -m 0755 -- "$RAIZ/src/config/abuelazo-nemo-config" \
  "$ARBOL/usr/bin/abuelazo-nemo-config"
for escritorio in "${escritorios[@]}"; do
  "${INSTALAR[@]}" -m 0644 -- "$escritorio" "$ARBOL/usr/share/applications/"
done
"${INSTALAR[@]}" -m 0644 -- "$PRIMER_INICIO" "$ARBOL/etc/xdg/autostart/"
"${INSTALAR[@]}" -m 0644 -- "$RAIZ/debian/copyright" \
  "$ARBOL/usr/share/doc/abuelazo-nemo-actions/copyright"
gzip -n -9 -c "$RAIZ/debian/changelog" > \
  "$ARBOL/usr/share/doc/abuelazo-nemo-actions/changelog.Debian.gz"
"${INSTALAR[@]}" -m 0644 -- \
  "$RAIZ/debian/abuelazo-nemo-actions.lintian-overrides" \
  "$ARBOL/usr/share/lintian/overrides/$PAQUETE"
"${INSTALAR[@]}" -m 0644 -- \
  "$RAIZ/debian/abuelazo-nemo-actions.conffiles" \
  "$ARBOL/DEBIAN/conffiles"
"${INSTALAR[@]}" -m 0644 -- "$RAIZ/debian/triggers" \
  "$ARBOL/DEBIAN/triggers"

find "$ARBOL" -type d -exec chmod 0755 {} +
find "$ARBOL" -type f -exec chmod 0644 {} +
for binario in "$ARBOL"/usr/bin/*; do
  chmod 0755 "$binario"
done

awk -v version="$VERSION" '
  BEGIN { RS = ""; FS = "\n" }
  $1 == "Package: abuelazo-nemo-actions" {
    campo = ""
    descripcion = 0
    for (i = 1; i <= NF; i++) {
      linea = $i
      if (descripcion && linea ~ /^[[:space:]]+/) {
        print linea
        continue
      }
      if (linea ~ /^[[:space:]]+/) {
        sub(/^[[:space:]]+/, "", linea)
        campo = campo " " linea
        continue
      }
      if (campo != "") {
        print campo
      }
      campo = linea
      descripcion = 0
      if (campo ~ /^Package:/) {
        print campo
        print "Version: " version
        campo = ""
      } else if (campo ~ /^Description:/) {
        print campo
        campo = ""
        descripcion = 1
      }
    }
    if (campo != "") {
      print campo
    }
    exit
  }
' "$RAIZ/debian/control" > "$ARBOL/DEBIAN/control"

PAQUETE_DEB="$DESTINO/${PAQUETE}_${VERSION}_all.deb"
dpkg-deb --build --root-owner-group "$ARBOL" "$PAQUETE_DEB"
lintian --pedantic "$PAQUETE_DEB"
HASH="$(sha256sum "$PAQUETE_DEB" | cut -d ' ' -f 1)"
printf 'Paquete: %s\nSHA256: %s\n' "$PAQUETE_DEB" "$HASH"
