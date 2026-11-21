# Abuelazo Nemo Actions

Conjunto de acciones para el menú contextual de Nemo en Linux Mint y otras
distribuciones que usan este gestor de archivos. El paquete instala las
acciones en una ubicación centralizada y ofrece un configurador para elegir
cuáles están disponibles. Las operaciones sobre archivos no sobrescriben
resultados anteriores: cuando ya existe la salida, crean una versión
numerada. Al terminar, ofrecen ir al archivo resultante y seleccionarlo, o ir a
la carpeta resultante y seleccionarla, según corresponda.

## Instalación

Descarga el paquete e instálalo con:

```
sudo apt install ./abuelazo-nemo-actions_1.3-16_all.deb
```

## Primer inicio

Después de instalar, el configurador aparece una sola vez al iniciar sesión.
Para abrirlo de nuevo manualmente:

```
abuelazo-nemo-config
```

## Cómo se activan las acciones

Solo las acciones activadas se enlazan en `~/.local/share/nemo/actions`.
También se agrupan en `~/.config/nemo/actions-tree.json` bajo el nodo
"Abuelazo Nemo Actions" para que aparezcan juntas en un submenú propio.
Ese submenú incluye siempre una primera entrada llamada "Configuración" que
abre el configurador de la aplicación. El submenú usa el logo de El Abuelazo
Tech como icono y cada categoría muestra un icono acorde con su contenido. La
opción Generar código QR usa un icono de código QR.
Si el submenú no aparece, cierra y vuelve a abrir Nemo; si persiste,
reinicia la sesión.

## Acciones incluidas

El catálogo contiene 34 acciones repartidas en seis categorías. No existe
ninguna acción para archivos `.lnk`: los accesos directos de Windows no se
convierten ni se abren desde este paquete.

| Categoría | Acción | Descripción |
| --- | --- | --- |
| Seguridad | Verificar SHA256 y MD5 | Calcula ambas sumas del archivo seleccionado con coreutils para ayudar a comprobar su integridad. |
| Seguridad | Limpiar metadatos EXIF | Elimina los metadatos de la imagen seleccionada con ExifTool para reducir la información personal compartida. |
| Seguridad | Cifrar archivo | Cifra el archivo seleccionado con GnuPG, pide la contraseña con zenity y sustituye el original por el archivo .gpg. |
| Seguridad | Descifrar archivo | Descifra el archivo GPG o ASC seleccionado con GnuPG, pide la contraseña con zenity y restaura el archivo original. |
| Organización | Aplanar carpeta | Mueve los archivos de las subcarpetas de la carpeta seleccionada a un solo nivel usando coreutils y findutils. |
| Organización | Mostrar árbol de directorios | Muestra en forma de árbol el contenido de la carpeta seleccionada usando tree. |
| Organización | Contar el peso de la carpeta | Suma el tamaño de los archivos de la carpeta seleccionada usando du y find. |
| Organización | Renombrar serie | Renombra en lote los archivos seleccionados con una numeración correlativa usando coreutils. |
| Organización | Renombrar a minúsculas | Pasa a minúsculas los nombres de los archivos seleccionados usando coreutils. |
| Organización | Renombrar a mayúsculas | Pasa a mayúsculas los nombres de los archivos seleccionados usando coreutils. |
| Ofimática | Nuevo documento de Writer | Crea un documento ODT en blanco en la carpeta indicada y lo abre con LibreOffice Writer. |
| Ofimática | Nueva hoja de cálculo de Calc | Crea una hoja de cálculo ODS en blanco en la carpeta indicada y la abre con LibreOffice Calc. |
| Ofimática | Nueva presentación de Impress | Crea una presentación ODP en blanco en la carpeta indicada y la abre con LibreOffice Impress. |
| Ofimática | Nuevo dibujo de Draw | Crea un dibujo ODG en blanco en la carpeta indicada y lo abre con LibreOffice Draw. |
| Ofimática | Nueva fórmula de Math | Crea una fórmula ODF en blanco en la carpeta indicada y la abre con LibreOffice Math. |
| Ofimática | Nueva base de datos de Base | Crea una base de datos ODB en blanco en la carpeta indicada y la abre con LibreOffice Base. |
| Ofimática | Unir PDFs | Combina los archivos PDF seleccionados en un único documento usando pdfunite de poppler-utils. |
| Ofimática | Convertir documento a PDF | Exporta los documentos ODT, ODS, ODP, ODG, ODF u ODB seleccionados a PDF con LibreOffice. |
| Ofimática | Convertir PDF a imágenes | Convierte cada página del PDF seleccionado en una imagen usando pdftoppm de poppler-utils. |
| Multimedia | Convertir imagen a JPG | Convierte la imagen seleccionada a JPG con ImageMagick, con fondo blanco si tiene transparencia y sin sobrescribir el original. |
| Multimedia | Crear miniatura para YouTube | Recorta y ajusta la imagen a 1280x720 píxeles para crear una miniatura de YouTube sin deformarla. |
| Multimedia | Extraer audio a MP3 | Extrae la pista de audio del vídeo seleccionado y la guarda como MP3 con FFmpeg, sin sobrescribir archivos. |
| Multimedia | Convertir MKV a MP4 | Convierte el archivo MKV seleccionado a MP4 con FFmpeg; intenta copia rápida y recodifica el audio a AAC si hace falta. |
| Multimedia | Comprimir a WebP | Convierte las imágenes seleccionadas a formato WebP con cwebp para reducir su tamaño. |
| Multimedia | Convertir vídeo a GIF | Crea un GIF animado a partir del vídeo seleccionado con FFmpeg; zenity permite ajustar las opciones. |
| Multimedia | Extraer fotogramas | Extrae fotogramas del vídeo seleccionado con FFmpeg; zenity permite elegir los parámetros. |
| Multimedia | Añadir marca de agua | Superpone una marca de agua en las imágenes seleccionadas con ImageMagick; zenity solicita el texto. |
| Multimedia | Rotar imágenes | Gira las imágenes seleccionadas con ImageMagick; zenity permite elegir el sentido y el ángulo. |
| Migración | Aplicar permisos 755 | Asigna permisos 755 a los archivos y carpetas seleccionados con chmod de coreutils. |
| Migración | Aplicar permisos 644 | Asigna permisos 644 a los archivos seleccionados con chmod de coreutils, sin permiso de ejecución. |
| Migración | Copiar ruta | Copia la ruta del archivo o carpeta seleccionado al portapapeles con xclip. |
| Utilidades | Generar código QR | Genera una imagen con un código QR a partir del texto introducido, con qrencode y zenity. |
| Utilidades | Copia de seguridad con fecha | Crea una copia del archivo o carpeta seleccionada añadiendo la fecha actual al nombre, usando coreutils. |
| Utilidades | Comparar archivos | Compara los dos primeros archivos seleccionados con Meld si está disponible o con diff; guarda el resultado en un TXT. |


## Dependencias

Los paquetes básicos son `nemo`, `bash`, `coreutils`, `findutils`,
`libnotify-bin`, `python3`, `python3-gi`, `zenity` y `xclip`.
Se recomiendan `ffmpeg`, `imagemagick`, `libreoffice`, `poppler-utils`,
`tree`, `webp`, `gnupg`, `libimage-exiftool-perl` y `qrencode`.
También se sugiere `meld`.
El configurador puede instalar las dependencias que falten mediante
`pkexec apt-get install`, por lo que pedirá autorización.

## Construcción

Con `dpkg-deb`, `lintian` y las dependencias de empaquetado instaladas:

```
./build.sh
```

El paquete se genera en `dist/abuelazo-nemo-actions_1.3-16_all.deb` y se
verifica con `lintian --pedantic`. La validación funcional completa, que cubre
las 33 acciones y el configurador sin ventanas ni privilegios, se ejecuta con:

```
./tests/test_scripts_a.sh
./tests/test_scripts_b.sh
python3 tests/test_catalog.py
python3 tests/test_funcional.py
```

## Desinstalación

```
sudo apt remove abuelazo-nemo-actions
```

Después elimina manualmente:

- `~/.config/abuelazo-nemo-actions`
- los symlinks del paquete en `~/.local/share/nemo/actions/*`
- el nodo "Abuelazo Nemo Actions" de `~/.config/nemo/actions-tree.json`

## Licencia y repositorio

Licencia MIT; consulta el archivo `LICENSE`.
Código fuente: https://github.com/abuelazotech/abuelazo-nemo-actions
