import importlib.machinery
import importlib.util
import json
import os
import pathlib
import sys
import tempfile
import unittest

ARCHIVO = pathlib.Path(__file__).resolve()
DIRECTORIO = ARCHIVO.parent
RAIZ = DIRECTORIO.parent
CATALOGO = os.environ.get('ABUELAZO_CATALOG', str(DIRECTORIO / '..' / 'catalog.json'))
CONFIGURADOR = RAIZ / 'src' / 'config' / 'abuelazo-nemo-config'

VALORES = [
    ('imagen-a-jpg', 'Convertir imagen a JPG', 'Multimedia', 'abuelazo-imagen-jpg', [], ['imagemagick'], 's', 'webp;png;tiff;tif;', '%F', True),
    ('miniatura-youtube', 'Crear miniatura para YouTube', 'Multimedia', 'abuelazo-miniatura-youtube', [], ['imagemagick'], 's', 'png;jpg;jpeg;webp;', '%F', True),
    ('documento-writer', 'Nuevo documento de Writer', 'Ofimática', 'abuelazo-nuevo-documento', ['odt'], ['libreoffice'], 'none', 'any;', '%P', True),
    ('documento-calc', 'Nueva hoja de cálculo de Calc', 'Ofimática', 'abuelazo-nuevo-documento', ['ods'], ['libreoffice'], 'none', 'any;', '%P', True),
    ('documento-impress', 'Nueva presentación de Impress', 'Ofimática', 'abuelazo-nuevo-documento', ['odp'], ['libreoffice'], 'none', 'any;', '%P', True),
    ('documento-draw', 'Nuevo dibujo de Draw', 'Ofimática', 'abuelazo-nuevo-documento', ['odg'], ['libreoffice'], 'none', 'any;', '%P', True),
    ('documento-math', 'Nueva fórmula de Math', 'Ofimática', 'abuelazo-nuevo-documento', ['odf'], ['libreoffice'], 'none', 'any;', '%P', True),
    ('documento-base', 'Nueva base de datos de Base', 'Ofimática', 'abuelazo-nuevo-documento', ['odb'], ['libreoffice'], 'none', 'any;', '%P', True),
    ('extraer-audio', 'Extraer audio a MP3', 'Multimedia', 'abuelazo-extraer-audio', [], ['ffmpeg'], 's', 'mp4;mkv;webm;avi;mov;', '%F', True),
    ('mkv-a-mp4', 'Convertir MKV a MP4', 'Multimedia', 'abuelazo-mkv-mp4', [], ['ffmpeg'], 's', 'mkv;', '%F', True),
    ('verificar-suma', 'Verificar SHA256 y MD5', 'Seguridad', 'abuelazo-verificar-suma', [], ['coreutils'], 's', 'iso;img;zip;tar;gz;xz;deb;', '%F', True),
    ('limpiar-exif', 'Limpiar metadatos EXIF', 'Seguridad', 'abuelazo-limpiar-exif', [], ['libimage-exiftool-perl'], 's', 'jpg;jpeg;png;tif;tiff;webp;', '%F', True),
    ('cifrar-archivo', 'Cifrar archivo', 'Seguridad', 'abuelazo-cifrar-archivo', [], ['gnupg', 'zenity'], 's', 'any;', '%F', True),
    ('descifrar-archivo', 'Descifrar archivo', 'Seguridad', 'abuelazo-descifrar-archivo', [], ['gnupg', 'zenity'], 's', 'gpg;asc;', '%F', True),
    ('aplanar-carpeta', 'Aplanar carpeta', 'Organización', 'abuelazo-aplanar-carpeta', [], ['coreutils', 'findutils'], 's', 'dir;', '%F', False),
    ('arbol-directorios', 'Mostrar árbol de directorios', 'Organización', 'abuelazo-arbol-directorios', [], ['tree'], 's', 'dir;', '%F', True),
    ('contar-peso', 'Contar el peso de la carpeta', 'Organización', 'abuelazo-contar-peso', [], ['coreutils', 'findutils'], 's', 'dir;', '%F', True),
    ('renombrar-serie', 'Renombrar serie', 'Organización', 'abuelazo-renombrar-serie', [], ['coreutils'], 'm', 'any;', '%F', False),
    ('renombrar-minusculas', 'Renombrar a minúsculas', 'Organización', 'abuelazo-renombrar-case', ['lower'], ['coreutils'], 'm', 'any;', '%F', True),
    ('renombrar-mayusculas', 'Renombrar a mayúsculas', 'Organización', 'abuelazo-renombrar-case', ['upper'], ['coreutils'], 'm', 'any;', '%F', False),
    ('unir-pdfs', 'Unir PDFs', 'Ofimática', 'abuelazo-unir-pdfs', [], ['poppler-utils'], 'm', 'pdf;', '%F', True),
    ('documento-a-pdf', 'Convertir documento a PDF', 'Ofimática', 'abuelazo-documento-a-pdf', [], ['libreoffice'], 'm', 'odt;ods;odp;odg;odf;odb;', '%F', True),
    ('pdf-a-imagenes', 'Convertir PDF a imágenes', 'Ofimática', 'abuelazo-pdf-a-imagenes', [], ['poppler-utils'], 's', 'pdf;', '%F', True),
    ('comprimir-webp', 'Comprimir a WebP', 'Multimedia', 'abuelazo-comprimir-webp', [], ['webp'], 'm', 'png;jpg;jpeg;tif;tiff;', '%F', True),
    ('video-a-gif', 'Convertir vídeo a GIF', 'Multimedia', 'abuelazo-video-a-gif', [], ['ffmpeg', 'zenity'], 's', 'mp4;mkv;webm;avi;mov;', '%F', False),
    ('extraer-frames', 'Extraer fotogramas', 'Multimedia', 'abuelazo-extraer-frames', [], ['ffmpeg', 'zenity'], 's', 'mp4;mkv;webm;avi;mov;', '%F', False),
    ('marca-agua', 'Añadir marca de agua', 'Multimedia', 'abuelazo-marca-agua', [], ['imagemagick', 'zenity'], 'm', 'png;jpg;jpeg;webp;', '%F', False),
    ('rotar-imagenes', 'Rotar imágenes', 'Multimedia', 'abuelazo-rotar-imagenes', [], ['imagemagick', 'zenity'], 'm', 'png;jpg;jpeg;tif;tiff;webp;', '%F', True),
    ('permisos-755', 'Aplicar permisos 755', 'Migración', 'abuelazo-permisos', ['755'], ['coreutils'], 'm', 'any;', '%F', True),
    ('permisos-644', 'Aplicar permisos 644', 'Migración', 'abuelazo-permisos', ['644'], ['coreutils'], 'm', 'any;', '%F', True),
    ('copiar-ruta', 'Copiar ruta', 'Migración', 'abuelazo-copiar-ruta', [], ['xclip'], 's', 'any;', '%F', True),
    ('generar-qr', 'Generar código QR', 'Utilidades', 'abuelazo-generar-qr', [], ['qrencode', 'zenity'], 'any', 'any;', '%F', True),
    ('backup-fecha', 'Copia de seguridad con fecha', 'Utilidades', 'abuelazo-backup-fecha', [], ['coreutils', 'zenity'], 's', 'any;', '%F', True),
    ('comparar-archivos', 'Comparar archivos', 'Utilidades', 'abuelazo-comparar-archivos', [], ['diffutils', 'zenity'], 'm', 'any;', '%F', True),
]

ICONOS_CATEGORIA = {
    'Multimedia': 'applications-multimedia',
    'Ofimática': 'applications-office',
    'Seguridad': 'security-high',
    'Organización': 'system-file-manager',
    'Migración': 'system-run',
    'Utilidades': 'applications-utilities',
}

ICONOS_PERMITIDOS = {
    'abuelazo-nemo-actions',
    'abuelazo-qr-code',
    'accessories-text-editor',
    'applications-multimedia',
    'applications-office',
    'applications-utilities',
    'application-pdf',
    'audio-x-generic',
    'camera-photo',
    'dialog-password',
    'document-open',
    'document-properties',
    'document-save-as',
    'edit-copy',
    'edit-find',
    'folder-open',
    'image-x-generic',
    'libreoffice-base',
    'libreoffice-calc',
    'libreoffice-draw',
    'libreoffice-impress',
    'libreoffice-math',
    'libreoffice-writer',
    'object-rotate-right',
    'preferences-system',
    'security-high',
    'system-file-manager',
    'system-lock-screen',
    'system-run',
    'video-x-generic',
}


def leer_catalogo():
    with open(CATALOGO, encoding='utf-8') as archivo:
        return json.load(archivo)


class PruebasCatalogo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.datos = leer_catalogo()
        cls.acciones = cls.datos['actions']

    def test_estructura_y_cantidad(self):
        self.assertEqual(self.datos['version'], 1)
        self.assertEqual(self.datos['package_version'], '1.3-16')
        self.assertEqual(len(self.acciones), 34)

    def test_ids_unicos(self):
        ids = [accion['id'] for accion in self.acciones]
        self.assertEqual(len(ids), len(set(ids)))

    def test_valores_exactos(self):
        self.assertEqual([accion['id'] for accion in self.acciones], [valor[0] for valor in VALORES])
        claves = ('name', 'category', 'exec', 'args', 'deps', 'selection', 'extensions', 'token', 'default')
        for accion, valor in zip(self.acciones, VALORES):
            for clave, esperado in zip(claves, valor[1:]):
                self.assertEqual(accion[clave], esperado, accion['id'] + ' / ' + clave)
            self.assertTrue(accion['description'])
            self.assertTrue(accion['comment'])
            self.assertTrue(accion['icon'])
            self.assertIn(accion['icon'], ICONOS_PERMITIDOS)

    def test_archivos_de_accion(self):
        for accion in self.acciones:
            ruta = RAIZ / 'src' / 'actions' / (accion['id'] + '.nemo_action')
            self.assertTrue(ruta.is_file(), accion['id'])
            lineas = ruta.read_text(encoding='utf-8').splitlines()
            self.assertEqual(lineas[0], '[Nemo Action]', accion['id'])
            ejecucion = [linea for linea in lineas if linea.startswith('Exec=')]
            self.assertEqual(len(ejecucion), 1, accion['id'])
            self.assertIn('/usr/bin/' + accion['exec'], ejecucion[0], accion['id'])
            self.assertIn(accion['token'], ejecucion[0], accion['id'])
            iconos = [linea for linea in lineas if linea.startswith('Icon-Name=')]
            self.assertEqual(len(iconos), 1, accion['id'])
            self.assertEqual(iconos[0], 'Icon-Name=' + accion['icon'], accion['id'])
            dependencias = [linea for linea in lineas if linea.startswith('Dependencies=')]
            self.assertEqual(len(dependencias), 1, accion['id'])
            self.assertTrue(dependencias[0].endswith(';'), accion['id'])
            paquetes = ('coreutils', 'findutils', 'poppler-utils',
                        'imagemagick', 'libimage-exiftool-perl', 'gnupg',
                        'webp', 'diffutils', 'meld',
                        'libnotify-bin', 'nemo')
            tokenes = dependencias[0][len('Dependencies='):].rstrip(';').split(';')
            for paquete in paquetes:
                self.assertNotIn(paquete, tokenes, accion['id'])
            self.assertIn('Terminal=false', lineas, accion['id'])
            self.assertEqual(len(lineas), 11, accion['id'])
        configuracion = (RAIZ / 'src' / 'actions' / 'configuracion.nemo_action').read_text(encoding='utf-8')
        self.assertIn('Icon-Name=preferences-system', configuracion)

    def test_sin_accesos_directos_lnk(self):
        self.assertNotIn('.lnk', json.dumps(self.datos, ensure_ascii=False))
        self.assertNotIn('lnk', [accion['id'] for accion in self.acciones])
        for ruta in (RAIZ / 'src' / 'actions').glob('*.nemo_action'):
            self.assertNotIn('.lnk', ruta.read_text(encoding='utf-8'), str(ruta))

    def test_zenity_en_acciones_de_video(self):
        for identificador in ('video-a-gif', 'extraer-frames'):
            accion = next(accion for accion in self.acciones if accion['id'] == identificador)
            self.assertIn('zenity', accion['deps'])

    def test_aplicar_con_home_temporal(self):
        temporal = tempfile.TemporaryDirectory()
        entorno = os.environ.copy()
        argv = sys.argv[:]
        try:
            os.environ['HOME'] = temporal.name
            os.environ['ABUELAZO_CATALOG'] = CATALOGO
            os.environ['ABUELAZO_ACTIONS_DIR'] = str(RAIZ / 'src' / 'actions')
            cargador = importlib.machinery.SourceFileLoader('config_abuelazo', str(CONFIGURADOR))
            especificacion = importlib.util.spec_from_file_location('config_abuelazo', CONFIGURADOR, loader=cargador)
            modulo = importlib.util.module_from_spec(especificacion)
            especificacion.loader.exec_module(modulo)
            esperados = {accion['id'] for accion in self.acciones if accion['default']}
            self.assertEqual(modulo.cargar_estado(modulo.cargar_catalogo()), esperados)
            self.assertFalse((pathlib.Path(temporal.name) / '.config' / 'abuelazo-nemo-actions' / 'estado.json').exists())

            seleccion = [accion['id'] for accion in self.acciones if accion['default']][:12]
            modulo.aplicar(seleccion)

            ruta_estado = pathlib.Path(temporal.name) / '.config' / 'abuelazo-nemo-actions' / 'estado.json'
            ruta_acciones = pathlib.Path(temporal.name) / '.local' / 'share' / 'nemo' / 'actions'
            ruta_arbol = pathlib.Path(temporal.name) / '.config' / 'nemo' / 'actions-tree.json'
            with open(ruta_estado, encoding='utf-8') as archivo:
                estado = json.load(archivo)
            self.assertEqual(estado, {'version': 1, 'enabled': sorted(seleccion)})
            for identificador in seleccion:
                enlace = ruta_acciones / (identificador + '.nemo_action')
                self.assertTrue(enlace.is_symlink(), identificador)
                self.assertEqual(os.readlink(enlace), str(RAIZ / 'src' / 'actions' / (identificador + '.nemo_action')))
            deshabilitada = ruta_acciones / 'aplanar-carpeta.nemo_action'
            self.assertFalse(deshabilitada.is_symlink())
            enlace_config = ruta_acciones / 'configuracion.nemo_action'
            self.assertTrue(enlace_config.is_symlink())
            self.assertEqual(os.readlink(enlace_config), str(RAIZ / 'src' / 'actions' / 'configuracion.nemo_action'))

            with open(ruta_arbol, encoding='utf-8') as archivo:
                arbol = json.load(archivo)
            self.assertIsInstance(arbol, dict)
            self.assertIn('toplevel', arbol)
            nodos = arbol['toplevel']
            propios = [nodo for nodo in nodos if nodo.get('uuid') == 'abuelazo-nemo-actions']
            self.assertEqual(len(propios), 1)
            submenu = propios[0]
            self.assertEqual(submenu['type'], 'submenu')
            self.assertEqual(submenu['user-label'], 'Abuelazo Nemo Actions')
            self.assertEqual(submenu['user-icon'], 'abuelazo-nemo-actions')
            hijos = submenu['children']
            self.assertEqual(hijos[0]['uuid'], 'configuracion.nemo_action')
            self.assertEqual(hijos[0]['type'], 'action')
            esperadas = {accion['category'] for accion in self.acciones if accion['id'] in seleccion}
            obtenidas = {nodo['user-label'] for nodo in hijos[1:]}
            self.assertEqual(obtenidas, esperadas)
            uuids = ['configuracion.nemo_action']
            for nodo_categoria in hijos[1:]:
                self.assertEqual(nodo_categoria['type'], 'submenu')
                self.assertEqual(nodo_categoria['user-icon'], ICONOS_CATEGORIA[nodo_categoria['user-label']])
                uuids.extend(hijo['uuid'] for hijo in nodo_categoria['children'])
                for hijo in nodo_categoria['children']:
                    self.assertEqual(hijo['type'], 'action')
                    self.assertIsNone(hijo['user-label'])
                    self.assertIsNone(hijo['user-icon'])
            self.assertEqual(set(uuids), {'configuracion.nemo_action'} | {identificador + '.nemo_action' for identificador in seleccion})

            with open(ruta_arbol, 'w', encoding='utf-8') as archivo:
                json.dump({'toplevel': [
                    {'uuid': 'otra-cosa', 'type': 'submenu', 'user-label': 'Otra cosa'},
                    {'uuid': 'abuelazo-nemo-actions', 'type': 'submenu', 'children': []},
                ]}, archivo)
            modulo.aplicar(seleccion)
            with open(ruta_arbol, encoding='utf-8') as archivo:
                arbol = json.load(archivo)
            nodos = arbol['toplevel']
            self.assertEqual(sum(1 for nodo in nodos if nodo.get('uuid') == 'abuelazo-nemo-actions'), 1)
            self.assertIn('otra-cosa', [nodo.get('uuid') for nodo in nodos])

            sys.argv = ['abuelazo-nemo-config', '--first-run']
            self.assertEqual(modulo.main(), 0)
            with open(ruta_estado, encoding='utf-8') as archivo:
                self.assertEqual(json.load(archivo), estado)
        finally:
            sys.argv = argv
            os.environ.clear()
            os.environ.update(entorno)
            temporal.cleanup()


if __name__ == '__main__':
    unittest.main()
