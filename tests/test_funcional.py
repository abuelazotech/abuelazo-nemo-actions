import datetime
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

ARCHIVO = pathlib.Path(__file__).resolve()
RAIZ = ARCHIVO.parent.parent
BIN = pathlib.Path(os.environ.get('ABUELAZO_BIN_PRUEBA', RAIZ / 'src' / 'bin'))
LIB = pathlib.Path(os.environ.get('ABUELAZO_LIB_PRUEBA', RAIZ / 'src' / 'lib'))
CONFIGURADOR = pathlib.Path(os.environ.get('ABUELAZO_CONFIG_PRUEBA', RAIZ / 'src' / 'config' / 'abuelazo-nemo-config'))
CATALOGO_PRUEBA = pathlib.Path(os.environ.get('ABUELAZO_CATALOGO_PRUEBA', RAIZ / 'catalog.json'))
ACCIONES_PRUEBA = pathlib.Path(os.environ.get('ABUELAZO_ACCIONES_PRUEBA', RAIZ / 'src' / 'actions'))
DEB = RAIZ / 'dist' / 'abuelazo-nemo-actions_1.3-16_all.deb'

STUB_ZENITY = '''#!/bin/bash
modo=''
for arg in "$@"; do
  case "$arg" in
    --entry) modo=entry ;;
    --password) modo=password ;;
    --question) modo=question ;;
    --list) modo=list ;;
    --text-info|--info) modo=text ;;
  esac
done
indice=1
contador="${ABUELO_ZENITY_CONTADOR:-}"
if [[ -n $contador && -f $contador ]]; then
  indice=$(<"$contador")
fi
texto=''
archivo=''
boton=''
for arg in "$@"; do
  case "$arg" in
    --text=*) texto="${arg#*=}" ;;
    --filename=*) archivo="${arg#*=}" ;;
    --ok-label=*) boton="${arg#*=}" ;;
  esac
done
estado=0
case "$modo" in
  entry)
    variable="ABUELO_ZENITY_ENTRY_$indice"
    valor="${!variable-}"
    [[ -n $valor ]] || valor="${ABUELO_ZENITY_ENTRY:-}"
    if [[ -z $valor ]]; then
      for arg in "$@"; do
        case "$arg" in --entry-text=*) valor="${arg#*=}" ;; esac
      done
    fi
    printf '%s\\n' "$valor"
    ;;
    password)
      printf '%s\n' "${ABUELO_ZENITY_PASSWORD:-clave-prueba}"
      ;;
    question)
      if [[ -n ${ABUELO_ZENITY_LOG:-} ]]; then
      printf '%s\\n' "$texto" >> "$ABUELO_ZENITY_LOG"
      [[ -z $boton ]] || printf 'BOTON=%s\\n' "$boton" >> "$ABUELO_ZENITY_LOG"
    fi
    [[ ${ABUELO_ZENITY_CONFIRM:-0} == 0 ]] || estado=1
    ;;
  list)
    printf '%s\\n' "${ABUELO_ZENITY_LIST:-90}"
    ;;
  text)
    if [[ -n ${ABUELO_ZENITY_LOG:-} ]]; then
      if [[ -n $archivo && -f $archivo ]]; then
        cat "$archivo" > "$ABUELO_ZENITY_LOG"
      elif [[ -n $texto ]]; then
        printf '%s\\n' "$texto" > "$ABUELO_ZENITY_LOG"
      else
        cat > "$ABUELO_ZENITY_LOG"
      fi
    else
      cat >/dev/null
    fi
    ;;
esac
if [[ -n $contador ]]; then
  printf '%s' "$((indice + 1))" > "$contador"
fi
exit "$estado"
'''

STUB_FFMPEG = '''#!/bin/bash
salida=''
anterior=''
for arg in "$@"; do
  [[ $anterior == -o ]] && salida=$arg
  anterior=$arg
done
[[ -n $salida ]] || salida="${!#}"
salida="${salida//%04d/0001}"
mkdir -p -- "$(dirname -- "$salida")"
printf 'stub-ffmpeg' > "$salida"
'''

STUB_IMAGEN = '''#!/bin/bash
salida="${!#}"
mkdir -p -- "$(dirname -- "$salida")"
printf 'stub-imagen' > "$salida"
'''

STUB_CON_OPCION = '''#!/bin/bash
salida=''
anterior=''
for arg in "$@"; do
  [[ $anterior == $OPCION ]] && salida=$arg
  anterior=$arg
done
[[ -n $salida ]] || salida="${!#}"
mkdir -p -- "$(dirname -- "$salida")"
printf "$CONTENIDO" > "$salida"
'''

STUB_PDFTOPPM = '''#!/bin/bash
prefijo="${!#}"
mkdir -p -- "$(dirname -- "$prefijo")"
printf 'stub-pagina' > "${prefijo}-1.png"
'''

STUB_LIBREOFFICE = '''#!/bin/bash
outdir=''
anterior=''
convertir=0
archivos=()
for arg in "$@"; do
  [[ $arg == --convert-to ]] && convertir=1
  [[ $anterior == --outdir ]] && outdir=$arg
  archivos+=("$arg")
  anterior=$arg
done
(( convertir == 1 )) || exit 0
[[ -n $outdir ]] || exit 0
for archivo in "${archivos[@]}"; do
  case "$archivo" in
    *.odt|*.ods|*.odp|*.odg)
      nombre="${archivo##*/}"
      nombre="${nombre%.*}"
      printf 'stub-pdf' > "$outdir/$nombre.pdf"
      ;;
  esac
done
'''

STUB_XCLIP = '''#!/bin/bash
cat > "${ABUELO_XCLIP_LOG:-/dev/null}"
'''

STUB_XDG_OPEN = '''#!/bin/bash
printf '%s\\n' "${1:-}" > "${ABUELO_OPEN_LOG:-/dev/null}"
'''

STUB_GDBUS = '''#!/bin/bash
uri=''
for arg in "$@"; do
  case "$arg" in
    *file://*) uri="$arg" ;;
  esac
done
uri="${uri#*file://}"
uri="${uri::-2}"
python3 -c 'import sys,urllib.parse; print(urllib.parse.unquote(sys.argv[1]))' "$uri" > "${ABUELO_OPEN_LOG:-/dev/null}"
'''

STUBS = {
    'zenity': STUB_ZENITY,
    'ffmpeg': STUB_FFMPEG,
    'magick': STUB_IMAGEN,
    'convert': STUB_IMAGEN,
    'cwebp': STUB_CON_OPCION.replace('$OPCION', '-o').replace('$CONTENIDO', 'stub-webp'),
    'qrencode': STUB_CON_OPCION.replace('$OPCION', '-o').replace('$CONTENIDO', 'stub-qr'),
    'tree': STUB_CON_OPCION.replace('$OPCION', '-o').replace('$CONTENIDO', 'stub-arbol\\n'),
    'gpg': STUB_CON_OPCION.replace('$OPCION', '--output').replace('$CONTENIDO', 'stub-gpg'),
    'pdftoppm': STUB_PDFTOPPM,
    'pdfunite': STUB_IMAGEN,
    'exiftool': '#!/bin/bash\nexit 0\n',
    'libreoffice': STUB_LIBREOFFICE,
    'xclip': STUB_XCLIP,
    'notify-send': '#!/bin/bash\nexit 0\n',
    'meld': '#!/bin/bash\nexit 0\n',
    'xdg-open': STUB_XDG_OPEN,
    'gdbus': STUB_GDBUS,
}


def escribir_stubs(destino, incluir_meld=True):
    destino.mkdir(parents=True, exist_ok=True)
    for nombre, contenido in STUBS.items():
        if nombre == 'meld' and not incluir_meld:
            continue
        ruta = destino / nombre
        ruta.write_text(contenido, encoding='utf-8')
        ruta.chmod(0o755)


class BaseFuncional(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporal = tempfile.TemporaryDirectory(prefix='abuelazo-funcional-')
        cls.raiz_temporal = pathlib.Path(cls.temporal.name)
        cls.stubs = cls.raiz_temporal / 'stubs'
        cls.stubs_sin_meld = cls.raiz_temporal / 'stubs-sin-meld'
        escribir_stubs(cls.stubs)
        escribir_stubs(cls.stubs_sin_meld, incluir_meld=False)
        cls.path_original = os.environ.get('PATH', '')
        cls.path_con_stubs = os.pathsep.join([str(cls.stubs), str(BIN), cls.path_original])
        cls.path_sin_meld = os.pathsep.join([str(cls.stubs_sin_meld), str(BIN), cls.path_original])

    @classmethod
    def tearDownClass(cls):
        cls.temporal.cleanup()

    def setUp(self):
        self.dir = pathlib.Path(tempfile.mkdtemp(dir=self.raiz_temporal))
        self.home = self.dir / 'home'
        self.tmp = self.dir / 'tmp'
        self.home.mkdir()
        self.tmp.mkdir()

    def crear_archivo(self, nombre, contenido='contenido'):
        ruta = self.dir / nombre
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(contenido, encoding='utf-8')
        return str(ruta)

    def crear_directorio(self, nombre):
        ruta = self.dir / nombre
        ruta.mkdir(parents=True, exist_ok=True)
        return str(ruta)

    def ejecutar(self, nombre, *argumentos, entorno=None, sin_meld=False):
        variables = os.environ.copy()
        for clave in list(variables):
            if clave.startswith('ABUELO_ZENITY_ENTRY') or clave in (
                'ABUELO_ZENITY_CONTADOR', 'ABUELO_ZENITY_LOG', 'ABUELO_XCLIP_LOG'
            ):
                del variables[clave]
        variables.update({
            'PATH': self.path_sin_meld if sin_meld else self.path_con_stubs,
            'HOME': str(self.home),
            'TMPDIR': str(self.tmp),
            'ABUELAZO_LIB_DIR': str(LIB),
            'ABUELO_ZENITY_CONFIRM': '0',
            'ABUELO_ZENITY_LIST': '90',
        })
        variables.update(entorno or {})
        contador = self.dir / 'zenity-contador'
        if any(clave.startswith('ABUELO_ZENITY_ENTRY_') for clave in variables):
            contador.unlink(missing_ok=True)
            variables['ABUELO_ZENITY_CONTADOR'] = str(contador)
        resultado = subprocess.run(
            [str(BIN / nombre), *[str(argumento) for argumento in argumentos]],
            env=variables,
            capture_output=True,
            text=True,
            cwd=str(self.dir),
        )
        self.assertEqual(resultado.returncode, 0, f'{nombre}: {resultado.stderr}')
        return resultado

    def afirmar_archivo(self, ruta):
        self.assertTrue(pathlib.Path(ruta).is_file(), ruta)

    def afirmar_no_sobrescribe(self, nombre, argumentos, original, segundo, entorno=None):
        self.ejecutar(nombre, *argumentos, entorno=entorno)
        self.afirmar_archivo(original)
        self.ejecutar(nombre, *argumentos, entorno=entorno)
        self.afirmar_archivo(segundo)


class PruebasAcciones(BaseFuncional):
    def test_imagen_a_jpg(self):
        origen = self.crear_archivo('foto.png')
        self.afirmar_no_sobrescribe('abuelazo-imagen-jpg', [origen], self.dir / 'foto.jpg', self.dir / 'foto-2.jpg')

    def test_miniatura_youtube(self):
        origen = self.crear_archivo('foto.png')
        self.afirmar_no_sobrescribe('abuelazo-miniatura-youtube', [origen], self.dir / 'foto_miniatura.jpg', self.dir / 'foto_miniatura-2.jpg')

    def test_documento_writer(self):
        carpeta = self.crear_directorio('docs-writer')
        self.afirmar_no_sobrescribe('abuelazo-nuevo-documento', ['odt', carpeta], pathlib.Path(carpeta) / 'Nuevo_Documento.odt', pathlib.Path(carpeta) / 'Nuevo_Documento-2.odt')

    def test_documento_calc(self):
        carpeta = self.crear_directorio('docs-calc')
        self.afirmar_no_sobrescribe('abuelazo-nuevo-documento', ['ods', carpeta], pathlib.Path(carpeta) / 'Nueva_Hoja_De_Calculo.ods', pathlib.Path(carpeta) / 'Nueva_Hoja_De_Calculo-2.ods')

    def test_documento_impress(self):
        carpeta = self.crear_directorio('docs-impress')
        self.afirmar_no_sobrescribe('abuelazo-nuevo-documento', ['odp', carpeta], pathlib.Path(carpeta) / 'Nueva_Presentacion.odp', pathlib.Path(carpeta) / 'Nueva_Presentacion-2.odp')

    def test_documento_draw(self):
        carpeta = self.crear_directorio('docs-draw')
        self.afirmar_no_sobrescribe('abuelazo-nuevo-documento', ['odg', carpeta], pathlib.Path(carpeta) / 'Nuevo_Dibujo.odg', pathlib.Path(carpeta) / 'Nuevo_Dibujo-2.odg')

    def test_documento_math(self):
        carpeta = self.crear_directorio('docs-math')
        self.afirmar_no_sobrescribe('abuelazo-nuevo-documento', ['odf', carpeta], pathlib.Path(carpeta) / 'Nueva_Formula.odf', pathlib.Path(carpeta) / 'Nueva_Formula-2.odf')

    def test_documento_base(self):
        carpeta = self.crear_directorio('docs-base')
        self.afirmar_no_sobrescribe('abuelazo-nuevo-documento', ['odb', carpeta], pathlib.Path(carpeta) / 'Nueva_Base_De_Datos.odb', pathlib.Path(carpeta) / 'Nueva_Base_De_Datos-2.odb')

    def test_extraer_audio(self):
        origen = self.crear_archivo('pelicula.mp4')
        self.afirmar_no_sobrescribe('abuelazo-extraer-audio', [origen], self.dir / 'pelicula.mp3', self.dir / 'pelicula-2.mp3')

    def test_mkv_a_mp4(self):
        origen = self.crear_archivo('pelicula.mkv')
        self.afirmar_no_sobrescribe('abuelazo-mkv-mp4', [origen], self.dir / 'pelicula.mp4', self.dir / 'pelicula-2.mp4')

    def test_verificar_suma(self):
        origen = self.crear_archivo('archivo.txt')
        registro = self.dir / 'zenity.txt'
        self.ejecutar('abuelazo-verificar-suma', origen, entorno={'ABUELO_ZENITY_LOG': str(registro)})
        contenido = registro.read_text(encoding='utf-8')
        self.assertIn('SHA256:', contenido)
        self.assertIn('MD5:', contenido)

    def test_limpiar_exif(self):
        origen = self.crear_archivo('foto.png')
        self.afirmar_no_sobrescribe('abuelazo-limpiar-exif', [origen], self.dir / 'foto_sin_exif.png', self.dir / 'foto_sin_exif-2.png')

    def test_cifrar_archivo(self):
        origen = pathlib.Path(self.crear_archivo('secreto.txt'))
        cifrado = self.dir / 'secreto.txt.gpg'
        registro = self.dir / 'zenity-cifrar.txt'
        self.ejecutar('abuelazo-cifrar-archivo', str(origen), entorno={'ABUELO_ZENITY_LOG': str(registro)})
        self.assertFalse(origen.exists())
        self.assertTrue(cifrado.is_file())
        self.assertIn('BOTON=Ir al archivo', registro.read_text(encoding='utf-8'))

    def test_descifrar_archivo(self):
        cifrado = pathlib.Path(self.crear_archivo('secreto.txt.gpg'))
        restaurado = self.dir / 'secreto.txt'
        self.ejecutar('abuelazo-descifrar-archivo', str(cifrado))
        self.assertFalse(cifrado.exists())
        self.assertTrue(restaurado.is_file())

    def test_aplanar_carpeta(self):
        carpeta = self.crear_directorio('carpeta')
        self.crear_archivo('carpeta/sub/archive.txt')
        self.ejecutar('abuelazo-aplanar-carpeta', carpeta)
        self.afirmar_archivo(self.dir / 'carpeta' / 'archive.txt')
        self.assertFalse((self.dir / 'carpeta' / 'sub').exists())

    def test_arbol_directorios(self):
        carpeta = self.crear_directorio('carpeta')
        registro = self.dir / 'zenity-arbol.txt'
        self.afirmar_no_sobrescribe('abuelazo-arbol-directorios', [carpeta], pathlib.Path(carpeta) / 'estructura.txt', pathlib.Path(carpeta) / 'estructura-2.txt', entorno={'ABUELO_ZENITY_LOG': str(registro)})
        self.assertIn('stub-arbol', registro.read_text(encoding='utf-8'))

    def test_contar_peso(self):
        carpeta = self.crear_directorio('carpeta')
        self.crear_archivo('carpeta/un.txt')
        registro = self.dir / 'zenity.txt'
        self.ejecutar('abuelazo-contar-peso', carpeta, entorno={'ABUELO_ZENITY_LOG': str(registro)})
        self.assertIn('Archivos:', registro.read_text(encoding='utf-8'))

    def test_renombrar_serie(self):
        primero = self.crear_archivo('uno.txt')
        segundo = self.crear_archivo('dos.txt')
        self.ejecutar('abuelazo-renombrar-serie', primero, segundo, entorno={'ABUELO_ZENITY_ENTRY_1': 'serie'})
        self.afirmar_archivo(self.dir / 'serie_001.txt')
        self.afirmar_archivo(self.dir / 'serie_002.txt')

    def test_renombrar_minusculas(self):
        origen = self.crear_archivo('Mezcla.TXT')
        self.ejecutar('abuelazo-renombrar-case', 'lower', origen)
        self.afirmar_archivo(self.dir / 'mezcla.TXT')

    def test_renombrar_mayusculas(self):
        origen = self.crear_archivo('Mezcla.TXT')
        self.ejecutar('abuelazo-renombrar-case', 'upper', origen)
        self.afirmar_archivo(self.dir / 'MEZCLA.TXT')

    def test_unir_pdfs(self):
        primero = self.crear_archivo('b.pdf')
        segundo = self.crear_archivo('a.pdf')
        self.afirmar_no_sobrescribe('abuelazo-unir-pdfs', [primero, segundo], self.dir / 'combinado.pdf', self.dir / 'combinado-2.pdf')

    def test_documento_a_pdf(self):
        origen = self.crear_archivo('informe.odt')
        self.afirmar_no_sobrescribe('abuelazo-documento-a-pdf', [origen], self.dir / 'informe.pdf', self.dir / 'informe-2.pdf')

    def test_pdf_a_imagenes(self):
        origen = self.crear_archivo('informe.pdf')
        self.ejecutar('abuelazo-pdf-a-imagenes', origen)
        self.afirmar_archivo(self.dir / 'informe_imagenes' / 'pagina-1.png')
        self.ejecutar('abuelazo-pdf-a-imagenes', origen)
        self.afirmar_archivo(self.dir / 'informe_imagenes-2' / 'pagina-1.png')

    def test_comprimir_webp(self):
        origen = self.crear_archivo('foto.png')
        self.afirmar_no_sobrescribe('abuelazo-comprimir-webp', [origen], self.dir / 'foto.webp', self.dir / 'foto-2.webp')

    def test_video_a_gif(self):
        origen = self.crear_archivo('clip.mp4')
        entorno = {'ABUELO_ZENITY_ENTRY_1': '0', 'ABUELO_ZENITY_ENTRY_2': '5'}
        self.afirmar_no_sobrescribe('abuelazo-video-a-gif', [origen], self.dir / 'clip.gif', self.dir / 'clip-2.gif', entorno=entorno)

    def test_extraer_frames(self):
        origen = self.crear_archivo('clip.mp4')
        entorno = {'ABUELO_ZENITY_ENTRY_1': '2'}
        self.ejecutar('abuelazo-extraer-frames', origen, entorno=entorno)
        self.afirmar_archivo(self.dir / 'clip_frames' / 'frame_0001.png')
        self.ejecutar('abuelazo-extraer-frames', origen, entorno=entorno)
        self.afirmar_archivo(self.dir / 'clip_frames-2' / 'frame_0001.png')

    def test_marca_agua(self):
        origen = self.crear_archivo('foto.png')
        entorno = {'ABUELO_ZENITY_ENTRY_1': 'Abuelazo Tech'}
        self.afirmar_no_sobrescribe('abuelazo-marca-agua', [origen], self.dir / 'foto_marcada.jpg', self.dir / 'foto_marcada-2.jpg', entorno=entorno)

    def test_rotar_imagenes(self):
        origen = self.crear_archivo('foto.png')
        self.afirmar_no_sobrescribe('abuelazo-rotar-imagenes', [origen], self.dir / 'foto_rotada.png', self.dir / 'foto_rotada-2.png')

    def test_permisos_755(self):
        origen = self.crear_archivo('script.sh')
        self.ejecutar('abuelazo-permisos', '755', origen)
        self.assertEqual(pathlib.Path(origen).stat().st_mode & 0o777, 0o755)

    def test_permisos_644(self):
        origen = self.crear_archivo('notas.txt')
        pathlib.Path(origen).chmod(0o755)
        self.ejecutar('abuelazo-permisos', '644', origen)
        self.assertEqual(pathlib.Path(origen).stat().st_mode & 0o777, 0o644)

    def test_copiar_ruta(self):
        origen = self.crear_archivo('ruta.txt')
        registro = self.dir / 'xclip.txt'
        self.ejecutar('abuelazo-copiar-ruta', origen, entorno={'ABUELO_XCLIP_LOG': str(registro)})
        self.assertEqual(registro.read_text(encoding='utf-8'), str(pathlib.Path(origen).resolve()))

    def test_generar_qr(self):
        entorno = {'ABUELO_ZENITY_ENTRY_1': 'Hola Mundo'}
        self.ejecutar('abuelazo-generar-qr', entorno=entorno)
        self.afirmar_archivo(self.dir / 'qr_hola_mundo.png')
        self.ejecutar('abuelazo-generar-qr', entorno=entorno)
        self.afirmar_archivo(self.dir / 'qr_hola_mundo-2.png')

    def test_backup_fecha(self):
        origen = self.crear_archivo('notas.txt')
        fecha = datetime.date.today().isoformat()
        registro = self.dir / 'zenity-backup.txt'
        apertura = self.dir / 'open-backup.txt'
        entorno = {'ABUELO_ZENITY_LOG': str(registro), 'ABUELO_OPEN_LOG': str(apertura)}
        self.afirmar_no_sobrescribe('abuelazo-backup-fecha', [origen], self.dir / f'notas_{fecha}.bak', self.dir / f'notas_{fecha}-2.bak', entorno=entorno)
        texto = registro.read_text(encoding='utf-8')
        self.assertIn(f'notas_{fecha}-2.bak', texto)
        self.assertIn('BOTON=Ir al archivo', texto)
        self.assertEqual(str(self.dir / f'notas_{fecha}-2.bak'), apertura.read_text(encoding='utf-8').strip())
        carpeta = self.crear_directorio('proyecto')
        registro_carpeta = self.dir / 'zenity-backup-carpeta.txt'
        apertura_carpeta = self.dir / 'open-backup-carpeta.txt'
        self.ejecutar('abuelazo-backup-fecha', carpeta, entorno={'ABUELO_ZENITY_LOG': str(registro_carpeta), 'ABUELO_OPEN_LOG': str(apertura_carpeta)})
        respaldo = self.dir / f'proyecto_{fecha}'
        self.assertTrue(respaldo.is_dir())
        self.assertIn(str(respaldo), registro_carpeta.read_text(encoding='utf-8'))
        self.assertIn('BOTON=Ir a la carpeta', registro_carpeta.read_text(encoding='utf-8'))
        self.assertEqual(str(respaldo), apertura_carpeta.read_text(encoding='utf-8').strip())

    def test_comparar_con_meld(self):
        primero = self.crear_archivo('uno.txt')
        segundo = self.crear_archivo('dos.txt')
        self.ejecutar('abuelazo-comparar-archivos', primero, segundo)

    @unittest.skipIf(shutil.which('meld') is not None, 'Meld instalado en el sistema')
    def test_comparar_sin_meld(self):
        primero = self.crear_archivo('uno.txt', 'a')
        segundo = self.crear_archivo('dos.txt', 'b')
        registro = self.dir / 'zenity.txt'
        self.ejecutar('abuelazo-comparar-archivos', primero, segundo, entorno={'ABUELO_ZENITY_LOG': str(registro)}, sin_meld=True)
        self.assertIn('-a', registro.read_text(encoding='utf-8'))

    def afirmar_no_sobrescribe(self, nombre, argumentos, original, segundo, entorno=None):
        self.ejecutar(nombre, *argumentos, entorno=entorno)
        self.afirmar_archivo(original)
        self.ejecutar(nombre, *argumentos, entorno=entorno)
        self.afirmar_archivo(segundo)


class PruebasConfigurador(BaseFuncional):
    def cargar_modulo(self):
        os.environ['HOME'] = str(self.home)
        os.environ['ABUELAZO_CATALOG'] = str(CATALOGO_PRUEBA)
        os.environ['ABUELAZO_ACTIONS_DIR'] = str(ACCIONES_PRUEBA)
        cargador = __import__('importlib.machinery', fromlist=['SourceFileLoader']).SourceFileLoader('config_funcional', str(CONFIGURADOR))
        import importlib.util
        especificacion = importlib.util.spec_from_file_location('config_funcional', CONFIGURADOR, loader=cargador)
        modulo = importlib.util.module_from_spec(especificacion)
        especificacion.loader.exec_module(modulo)
        return modulo

    def test_aplicar_todas_y_limpiar_huerfanas(self):
        modulo = self.cargar_modulo()
        acciones = modulo.cargar_catalogo()
        ids = [accion['id'] for accion in acciones]
        directorio = self.home / '.local' / 'share' / 'nemo' / 'actions'
        directorio.mkdir(parents=True)
        huerfana = directorio / 'convertir_a_jpg.nemo_action'
        huerfana.symlink_to('/usr/share/abuelazo-nemo-actions/actions/convertir_a_jpg.nemo_action')
        arbol_archivo = self.home / '.config' / 'nemo' / 'actions-tree.json'
        arbol_archivo.parent.mkdir(parents=True)
        arbol_archivo.write_text(json.dumps({'toplevel': [
            {'uuid': 'otra-cosa', 'type': 'submenu'},
            {'uuid': modulo.UUID_SUBMENU, 'type': 'submenu', 'children': [
                {'uuid': 'convertir_a_jpg.nemo_action', 'type': 'action'}
            ]},
        ]}), encoding='utf-8')
        modulo.aplicar(ids)
        self.assertEqual(len(list(directorio.iterdir())), 35)
        for identificador in ids:
            enlace = directorio / (identificador + '.nemo_action')
            self.assertTrue(enlace.is_symlink(), identificador)
        self.assertTrue((directorio / modulo.UUID_CONFIGURACION).is_symlink())
        self.assertFalse(huerfana.exists())
        arbol = json.loads(arbol_archivo.read_text(encoding='utf-8'))
        nodos = arbol['toplevel']
        propios = [nodo for nodo in nodos if nodo.get('uuid') == modulo.UUID_SUBMENU]
        self.assertEqual(len(propios), 1)
        hijos = propios[0]['children']
        self.assertEqual(hijos[0]['uuid'], modulo.UUID_CONFIGURACION)
        uuids = [modulo.UUID_CONFIGURACION]
        for categoria in hijos[1:]:
            uuids.extend(hijo['uuid'] for hijo in categoria['children'])
        self.assertEqual(set(uuids), {modulo.UUID_CONFIGURACION} | {identificador + '.nemo_action' for identificador in ids})
        self.assertIn('otra-cosa', [nodo.get('uuid') for nodo in nodos])
        argv_original = sys.argv[:]
        try:
            sys.argv = ['abuelazo-nemo-config', '--first-run']
            self.assertEqual(modulo.main(), 0)
        finally:
            sys.argv = argv_original

    def test_deshabilitar(self):
        modulo = self.cargar_modulo()
        acciones = modulo.cargar_catalogo()
        ids = [accion['id'] for accion in acciones]
        modulo.aplicar(ids)
        seleccion = ids[:5]
        modulo.aplicar(seleccion)
        directorio = self.home / '.local' / 'share' / 'nemo' / 'actions'
        self.assertEqual(len(list(directorio.iterdir())), 6)
        estado = json.loads((self.home / '.config' / 'abuelazo-nemo-actions' / 'estado.json').read_text(encoding='utf-8'))
        self.assertEqual(estado['enabled'], sorted(seleccion))


class PruebasPaquete(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporal = tempfile.TemporaryDirectory(prefix='abuelazo-deb-')
        cls.raiz = pathlib.Path(cls.temporal.name)
        cls.root = cls.raiz / 'root'
        cls.root.mkdir()
        cls.resultado = subprocess.run(['dpkg-deb', '-x', str(DEB), str(cls.root)], capture_output=True, text=True)
        if cls.resultado.returncode != 0:
            raise AssertionError(cls.resultado.stderr)

    @classmethod
    def tearDownClass(cls):
        cls.temporal.cleanup()

    def test_metadatos(self):
        control = subprocess.run(['dpkg-deb', '-I', str(DEB), 'control'], capture_output=True, text=True).stdout
        self.assertIn('Version: 1.3-16', control)
        self.assertIn('Maintainer: Angelino Santana (El Abuelazo Tech) <abuelazo@protonmail.com>', control)
        conffiles = subprocess.run(['dpkg-deb', '-I', str(DEB), 'conffiles'], capture_output=True, text=True).stdout
        self.assertIn('/etc/xdg/autostart/abuelazo-nemo-config-first-run.desktop', conffiles)
        disparadores = subprocess.run(['dpkg-deb', '-I', str(DEB), 'triggers'], capture_output=True, text=True).stdout
        self.assertIn('activate-noawait gtk-update-icon-cache', disparadores)

    def test_contenido(self):
        base = self.root / 'usr' / 'share' / 'abuelazo-nemo-actions'
        self.assertEqual(len(list((base / 'actions').glob('*.nemo_action'))), 35)
        self.assertEqual(len(list((self.root / 'usr' / 'bin').glob('abuelazo-*'))), 28)
        self.assertTrue((base / 'catalog.json').is_file())
        self.assertTrue((base / 'lib' / 'abuelazo-common.sh').is_file())
        self.assertTrue((self.root / 'etc' / 'xdg' / 'autostart' / 'abuelazo-nemo-config-first-run.desktop').is_file())
        self.assertTrue((self.root / 'usr' / 'share' / 'applications' / 'abuelazo-nemo-config.desktop').is_file())
        iconos = list((self.root / 'usr' / 'share' / 'icons' / 'hicolor').glob('*/apps/*.png'))
        self.assertEqual(len(iconos), 16)

    def test_permisos(self):
        for ruta in (self.root / 'usr' / 'bin').glob('abuelazo-*'):
            self.assertEqual(ruta.stat().st_mode & 0o777, 0o755, str(ruta))
        self.assertEqual((self.root / 'usr' / 'share' / 'abuelazo-nemo-actions' / 'lib' / 'abuelazo-common.sh').stat().st_mode & 0o777, 0o644)

    def test_lintian(self):
        resultado = subprocess.run(['lintian', '--pedantic', str(DEB)], capture_output=True, text=True)
        self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)


if __name__ == '__main__':
    unittest.main(verbosity=2)
