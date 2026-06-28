# MKGIF
Create gifs from videos in command line.

------------------------------
## MKGIF - Video & WebP to GIF Converter
Una herramienta de línea de comandos (CLI) potente, eficiente y personalizable escrita en Python para convertir videos y archivos WebP animados en GIFs optimizados. Cuenta con barras de progreso interactivas, personalización de tamaño/velocidad y la capacidad de cancelar el proceso en tiempo real.
## Características

* Compatibilidad amplia: Soporta formatos .mp4, .avi, .mov, .wmv, .rm, .gif y .webp.
* Control de rendimiento: Procesamiento eficiente de fotogramas mediante generadores para moderar el uso de memoria RAM.
* Cancelación en vivo: Presiona la Barra Espaciadora en cualquier momento para abortar la conversión de manera segura.
* Personalización total: Ajusta la velocidad (speed), escala de resolución (size) y rango de fotogramas (from_frame / to_frame).
* Interfaz colorida: Salida estilizada en la terminal usando arte ASCII y colores dinámicos.

------------------------------
## Requisitos Previos
El script utiliza las siguientes librerías de Python. Asegúrate de tenerlas instaladas antes de ejecutarlo:

pip install opencv-python pillow numpy tqdm colorama pynput pyfiglet pyglet

------------------------------
## Instalación

### Opción 1: comando global (recomendado)

```bash
git clone https://github.com/antonioam82/MKGIF.git
cd MKGIF
pip install -e .
```

Esto instala las dependencias **y** registra el comando `mkgif`, disponible desde cualquier carpeta:

```bash
mkgif -src video.mp4 -shw
```

### Opción 2: ejecutar el script directamente

Si no quieres instalar el comando global, solo necesitas las dependencias:

```bash
pip install -r requirements.txt
python mkgif.py -src video.mp4 -shw
```

| | ¿Obligatorio? | Para qué sirve |
|---|---|---|
| `pip install -r requirements.txt` | ✅ Sí | Instala las librerías que el script necesita para funcionar |
| `pip install -e .` | ❌ No, es comodidad | Instala las dependencias y además crea el comando global `mkgif`, para no usar `python` ni rutas |

------------------------------
## Modo de uso

```
mkgif -src <archivo_origen> [opciones]
```

| Opción | Descripción | Por defecto |
|---|---|---|
| `-src`, `--source` | Video o WebP animado de origen (obligatorio). Formatos: `.mp4`, `.avi`, `.mov`, `.wmv`, `.rm`, `.gif`, `.webp` | — |
| `-dest`, `--destination` | Nombre del `.gif` de salida | nombre autogenerado (hash SHA-1) |
| `-sz`, `--size` | Escala relativa de tamaño, en % (ej. `50` = mitad de tamaño) | 100 |
| `-spd`, `--speed` | Velocidad relativa, en % (ej. `200` = doble de velocidad) | 100 |
| `-fps`, `--frames_per_second` | Fotogramas por segundo del GIF resultante | el del vídeo original |
| `-from`, `--from_frame` | Fotograma inicial desde el que capturar | 0 |
| `-to`, `--to_frame` | Fotograma final donde detener la captura | último fotograma |
| `-opt`, `--optimize` | Optimiza paleta/compresión al guardar (más lento) | desactivado |
| `-shw`, `--show` | Muestra el GIF resultante en una ventana al terminar | desactivado |
| `-delsrc`, `--delete_source` | Elimina el archivo de origen tras generar el GIF | desactivado |

### Ejemplo

```bash
mkgif -src video.mp4 -dest resultado.gif -sz 50 -spd 200 -opt -shw
```

Durante el proceso, puedes pulsar la **Barra Espaciadora** en cualquier momento para cancelar la conversión de forma segura.

------------------------------
## Estructura del Código
El script está diseñado modularmente bajo las siguientes funciones clave:

* AppState: Dataclass que gestiona el estado global de la aplicación y la detención por teclado.
* read_video(): Extrae los fotogramas del archivo multimedia de origen de forma eficiente.
* frame_generator(): Generador intermedio que entrega fotogramas uno a uno para evitar saturar la memoria.
* create_gif(): Redimensiona, procesa la barra de progreso y exporta el archivo GIF final.
* on_press(): Escucha en segundo plano la tecla espacio mediante pynput para detener los bucles de manera asíncrona.

------------------------------
## Licencia
Este proyecto está bajo la licencia MIT. Siéntete libre de clonarlo, modificarlo y mejorar el código.
------------------------------

