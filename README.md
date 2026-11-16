# Proyecto 2 AED — Disjoin Set Union (DSU) con Rollback

Video educativo animado que explica y demuestra visualmente el funcionamiento de la estructura de datos **Disjoin Set Union (DSU) con Rollback**.

## Descripción

El **DSU con Rollback** es una variante de la estructura de Conjuntos Disjuntos (*Union-Find*) que permite deshacer operaciones de unión anteriores (`join`) en orden inverso (LIFO), restaurando el estado previo de las componentes conexas en tiempo $O(1)$ por reversión y $O(\log n)$ por búsqueda/unión al prescindir de la compresión de caminos y emplear **Unión por Tamaño (*Union by Size*)** junto con una pila de historial.

Este proyecto implementa la estructura desde cero en Python puro y genera una animación (de 4 a 5 minutos) con [Manim Community Edition](https://www.manim.community/) que demuestra la lógica paso a paso. Toda la animación está guiada por la estructura de datos real mediante generadores (`yield`).

La animación está dividida en las siguientes secciones:

1. **Título del proyecto** (`Disjoin Set Union (DSU) con Rollback`)
2. **Introducción: Redes y Conectividad** (Qué es, motivación visual y reversión de enlaces)
3. **¿Por qué NO usar Compresión de Caminos?** (Comparación con *Union by Size* + Pila)
4. **Creación de Conjuntos: `make_set(x)` en $O(1)$** sobre 6 elementos (`0..5`)
5. **Operaciones `join(u, v)` y `snapshot()` paso a paso**
6. **Búsqueda `find(x)` sin compresión de caminos** (`find(3)` y `find(5)` en $O(\log n)$)
7. **Reversión de Estado (`rollback()` y `rollback_to(snap)`)** en tiempo $O(1)$
8. **Aplicación Clásica: Conectividad Dinámica Offline** (Árbol de Segmentos sobre el Tiempo + DFS)
9. **Conclusión y Resumen de Complejidades** (`make_set`, `find`, `join`, `snapshot`, `rollback`, `rollback_to`)

## Integrantes

| # | Nombre |
|---|--------|
| 1 | Axel Roberth Portal Ruiz |
| 2 | Dayron Saiyuk Cueva Loayza |
| 3 | Mariel Azucena Reyes Neyra |

## Estructura del Proyecto

```
proyecto2_aed/
├── dsu_rollback.py          # Implementación del DSU con Rollback (lógica pura)
├── dsu_rollback_scene.py    # Escena de Manim (animación)
├── README.md                # Este archivo
└── media/                   # Videos generados (creado automáticamente)
```

## Software Requerido

| Software | Versión mínima | Instalación |
|----------|---------------|-------------|
| **Python** | 3.10+ | [python.org](https://www.python.org/downloads/) |
| **Manim Community Edition** | 0.18+ | `pip install manim` |
| **Matplotlib** | 3.7+ | `pip install matplotlib` (renderiza texto y fórmulas LaTeX *Computer Modern* sin requerir MiKTeX/TeX Live) |
| **FFmpeg** | 4.0+ | Incluido con Manim/PyAV en Windows, o [ffmpeg.org](https://ffmpeg.org/) |

### Instalación rápida

```bash
# 1. Clonar el repositorio
git clone https://github.com/AxelPortal/proyecto2_aed.git
cd proyecto2_aed

# 2. Crear entorno virtual (recomendado)
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 3. Instalar dependencias
pip install manim matplotlib
```

## Comandos de Ejecución

### Ejecutar tests del DSU con Rollback (sin Manim)

```bash
python dsu_rollback.py
```

Esto ejecuta pruebas unitarias de inicialización y `make_set(x)`, `join` con *Union by Size*, búsqueda `find` sin compresión de caminos, `snapshot`, `rollback`, `rollback_to` y los casos borde (unión redundante y reversión con pila vacía).

### Generar el video

```bash
# Baja calidad (480p, rápido para desarrollo)
manim -pql dsu_rollback_scene.py DSURollbackScene

# Calidad media (720p)
manim -pqm dsu_rollback_scene.py DSURollbackScene

# Alta calidad (1080p, para entrega final)
manim -pqh dsu_rollback_scene.py DSURollbackScene
```

El flag `-p` abre el video automáticamente después de renderizar. El video se guarda en el directorio de salida (ej. `media/videos/dsu_rollback_scene/1080p60/DSURollbackScene.mp4`).

## Arquitectura del Código

La lógica algorítmica emite eventos paso a paso mediante generadores (`yield`). La escena de Manim consume estos eventos y los traduce en animaciones visuales, garantizando que toda la animación está impulsada por la lógica real del algoritmo.
