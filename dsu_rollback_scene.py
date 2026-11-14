# -*- coding: utf-8 -*-
"""
dsu_rollback_scene.py — Animación Manim CE para DSU con Rollback.
Proyecto 2 AED — UTEC 2026-2

Ejecución:
    manim -pql dsu_rollback_scene.py DSURollbackScene   # 480p rápido
    manim -pqh dsu_rollback_scene.py DSURollbackScene   # 1080p entrega
"""

import hashlib
import os
from manim import *
import matplotlib
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties
from matplotlib.path import Path as MplPath
import numpy as np

from dsu_rollback import DSURollback

# === CONFIGURACIÓN DE ESCENA Y MOTOR LATEX (COMPUTER MODERN) ===
config.background_color = "#000000"
matplotlib.rcParams["mathtext.fontset"] = "cm"

# === DATOS DEL PROYECTO ===
INTEGRANTES = [
    "Axel Roberth Portal Ruiz",
    "Dayron Saiyuk Cueva Loayza",
    "Mariel Azucena Reyes Neyra",
]
TITULO = "Disjoin Set Union (DSU) con Rollback"
SUBTITULO = "Conjuntos Disjuntos con Reversión de Estado"
UNIVERSIDAD = "Universidad de Ingeniería y Tecnología - UTEC"

# === PALETA DE COLORES ===
C_TEXT = "#FFFFFF"
C_TEXT2 = "#CCCCCC"
C_ACCENT = "#58a6ff"
C_GREEN = "#3fb950"
C_RED = "#f85149"
C_ORANGE = "#d29922"
C_ROOT = "#da3633"
C_INTERNAL = "#1f6feb"
C_LEAF = "#238636"
C_EDGE = "#888888"
C_ELABEL = "#79c0ff"
CODE_FONT = "Consolas"


def MyText(text: str, font_size: float = 24, color=WHITE, weight="normal", font=None):
    """Renderiza texto y fórmulas LaTeX ($...$) con tipografía Serif / Computer Modern."""
    if not text:
        return VGroup()
    w = "bold" if str(weight).upper() == "BOLD" else "normal"
    fam = "Times New Roman"
    prop = FontProperties(family=fam, weight=w, size=font_size)
    tp = TextPath((0, 0), text, size=font_size, prop=prop)
    ext = tp.get_extents()

    cmds = []
    for pts, code in tp.iter_segments():
        if code == MplPath.MOVETO:
            cmds.append(f"M {pts[0]:.3f} {-pts[1]:.3f}")
        elif code == MplPath.LINETO:
            cmds.append(f"L {pts[0]:.3f} {-pts[1]:.3f}")
        elif code == MplPath.CURVE3:
            cmds.append(f"Q {pts[0]:.3f} {-pts[1]:.3f} {pts[2]:.3f} {-pts[3]:.3f}")
        elif code == MplPath.CURVE4:
            cmds.append(
                f"C {pts[0]:.3f} {-pts[1]:.3f} {pts[2]:.3f} {-pts[3]:.3f} {pts[4]:.3f} {-pts[5]:.3f}"
            )
        elif code == MplPath.CLOSEPOLY:
            cmds.append("Z")

    if not cmds:
        return VGroup()

    h_key = hashlib.md5(f"v2_{text}_{font_size}_{w}_{fam}".encode("utf-8")).hexdigest()
    tex_dir = os.path.join("media", "Tex")
    os.makedirs(tex_dir, exist_ok=True)
    svg_path = os.path.join(tex_dir, f"{h_key}.svg")

    if not os.path.exists(svg_path):
        q = chr(34)
        d_str = " ".join(cmds)
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(f"<svg xmlns={q}http://www.w3.org/2000/svg{q}><path d={q}{d_str}{q}/></svg>")

    mob = SVGMobject(svg_path, fill_color=color, fill_opacity=1.0, stroke_width=0)
    target_h = max(ext.height, 1.0) * 0.0132
    mob.scale_to_fit_height(target_h)
    return mob


# =====================================================================
# FUNCIONES DE LAYOUT DEL BOSQUE DSU
# =====================================================================

def forest_layout(dsu: DSURollback, xl=-1.35, xr=6.25, yt=1.62, ys=1.22):
    """Calcula coordenadas (x, y, 0) para cada nodo activo del bosque DSU."""
    n = dsu.n
    active_nodes = [i for i in range(n) if dsu.active[i]]
    if not active_nodes:
        return {i: np.array([xl + (xr - xl) * (i + 0.5) / n, yt, 0.0]) for i in range(n)}

    children = {i: [] for i in active_nodes}
    roots = []
    for i in active_nodes:
        p = dsu.parent[i]
        if p == i or p < 0:
            roots.append(i)
        else:
            children[p].append(i)

    widths = {}

    def calc_w(u):
        if not children[u]:
            widths[u] = 1.0
            return 1.0
        t = sum(calc_w(c) for c in children[u])
        widths[u] = max(1.15, t)
        return widths[u]

    for r in roots:
        calc_w(r)

    pos = {}
    total_w = sum(widths[r] for r in roots) if roots else 1.0

    def assign(u, left, right, depth):
        pos[u] = np.array([(left + right) / 2.0, yt - depth * ys, 0.0])
        if not children[u]:
            return
        tw = sum(widths[c] for c in children[u])
        cl = left
        for c in children[u]:
            cw = widths[c]
            cr = cl + (right - left) * cw / tw
            assign(c, cl, cr, depth + 1)
            cl = cr

    cl = xl
    for r in roots:
        rw = widths[r]
        cr = cl + (xr - xl) * rw / total_w
        assign(r, cl, cr, 0)
        cl = cr

    for i in range(n):
        if i not in pos:
            pos[i] = np.array([xl + (xr - xl) * (i + 0.5) / n, yt, 0.0])

    return pos


def make_arrow_between(p_child: np.ndarray, p_par: np.ndarray, par_is_root: bool = True):
    """Crea una flecha limpia entre el borde del nodo hijo y el borde del nodo padre."""
    r_child = 0.25
    r_par = 0.27 if par_is_root else 0.25
    d = p_par - p_child
    ln = np.linalg.norm(d)
    if ln > 0:
        u = d / ln
        ls = p_child + u * (r_child + 0.04)
        le = p_par - u * (r_par + 0.04)
    else:
        ls, le = p_child, p_par
    return Arrow(
        ls,
        le,
        buff=0,
        stroke_width=2.6,
        color=C_EDGE,
        max_tip_length_to_length_ratio=0.22,
    )


# =====================================================================
# ESCENA PRINCIPAL CON TRANSICIONES FLUIDAS
# =====================================================================

class DSURollbackScene(Scene):

    def construct(self):
        self.current_time = 0.0
        self._title()                 # 0:00 -> 0:14 (14 s)
        self._intro()                 # 0:14 -> 0:50 (36 s)
        self._why_no_compression()    # 0:50 -> 1:25 (35 s)
        self._make_set_and_unions()   # 1:25 -> 2:38 (73 s: 20s make_set + 53s join/snapshot)
        self._find_query()            # 2:38 -> 3:05 (27 s)
        self._rollback_demo()         # 3:05 -> 3:39 (34 s)
        self._edge_cases()            # 3:39 -> 4:04 (25 s)
        self._complexity()            # 4:04 -> 4:14 (10 s)
        self._credits()               # 4:14 -> 4:22 (8 s)

    # ── Helpers de Tiempo y Encabezados ──────────────────────────────

    def _play(self, *anims, run_time=1.0, rate_func=smooth):
        self.play(*anims, run_time=run_time, rate_func=rate_func)
        self.current_time += run_time

    def _wait(self, duration):
        if duration > 0.01:
            self.wait(duration)
            self.current_time += duration

    def _wait_until(self, target_sec):
        rem = target_sec - self.current_time
        if rem > 0.01:
            self.wait(rem)
            self.current_time = target_sec

    def _header(self, text):
        h = MyText(text, font_size=28, color=WHITE, weight=BOLD).to_edge(UP, buff=0.42)
        ln = Line(
            h.get_left() + DOWN * 0.18,
            h.get_right() + DOWN * 0.18,
            color=C_ACCENT,
            stroke_width=2,
        )
        g = VGroup(h, ln)
        self._play(Write(h), Create(ln), run_time=1.1)
        return g

    def _fade(self, *m):
        if m:
            self._play(*[FadeOut(x, shift=DOWN * 0.1) for x in m], run_time=0.85)
        self._wait(0.35)

    def _set_status(self, text: str, color=C_ACCENT, run_time=0.45):
        new_lbl = MyText(text, font_size=17, color=color).to_edge(DOWN, buff=0.38)
        if new_lbl.width > 12.8:
            new_lbl.scale_to_fit_width(12.8)
            new_lbl.to_edge(DOWN, buff=0.38)
        if getattr(self, "_status_lbl", None) is None:
            self._status_lbl = new_lbl
            self._play(FadeIn(new_lbl, shift=UP * 0.12), run_time=run_time)
        else:
            old = self._status_lbl
            self._status_lbl = new_lbl
            self._play(
                FadeOut(old, shift=UP * 0.1),
                FadeIn(new_lbl, shift=UP * 0.1),
                run_time=run_time,
            )

    # ── 1. TÍTULO (0:00 -> 0:14) ─────────────────────────────────────

    def _title(self):
        t1 = MyText(TITULO, font_size=40, color=WHITE, weight=BOLD)
        if t1.width > 12.0:
            t1.scale_to_fit_width(12.0)
        t2 = MyText(SUBTITULO, font_size=25, color=C_TEXT2).next_to(t1, DOWN, buff=0.28)
        t3 = MyText(UNIVERSIDAD, font_size=19, color=C_ACCENT).next_to(t2, DOWN, buff=0.48)
        deco = Line(LEFT * 3.5, RIGHT * 3.5, color=C_ACCENT, stroke_width=1.6).next_to(t3, DOWN, buff=0.4)

        self._play(Write(t1), run_time=2.0)
        self._play(FadeIn(t2, shift=UP * 0.18), run_time=1.0)
        self._wait(0.8)
        self._play(FadeIn(t3, shift=UP * 0.15), Create(deco), run_time=1.3)
        self._wait_until(12.8)
        self._fade(t1, t2, t3, deco)

    # ── 2. INTRODUCCIÓN (0:14 -> 0:50) ───────────────────────────────

    def _intro(self):
        hg = self._header(r"¿Qué es un DSU con Rollback?")

        lines = VGroup(
            MyText(r"Es una variante de Disjoint Set Union ($\mathrm{Union\text{-}Find}$) que mantiene", font_size=21, color=C_TEXT),
            MyText(r"una colección de conjuntos disjuntos dinámicos y permite revertir", font_size=21, color=C_TEXT),
            MyText(r"operaciones de unión anteriores en tiempo constante $\mathcal{O}(1)$,", font_size=21, color=C_TEXT),
            MyText(r"restaurando exactamente el estado previo de las componentes.", font_size=21, color=C_TEXT),
        )
        lines.arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        lines.next_to(hg, DOWN, buff=0.5).to_edge(LEFT, buff=0.95)

        self._play(
            LaggedStart(*[FadeIn(l, shift=RIGHT * 0.2) for l in lines], lag_ratio=0.22),
            run_time=3.0,
        )
        self._wait(3.2)

        tda_h = MyText(r"Tipo de Dato Abstracto (TDA):", font_size=21, color=C_ACCENT, weight=BOLD)
        tda_h.next_to(lines, DOWN, buff=0.45, aligned_edge=LEFT)

        tda_lines = VGroup(
            MyText(
                r"• Operaciones: $\mathrm{make\_set}(x)$, $\mathrm{find}(x)$, $\mathrm{join}(u, v)$, $\mathrm{snapshot}()$ y $\mathrm{rollback}()$",
                font_size=19,
                color=C_TEXT,
            ),
            MyText(
                r"• Estructura: Bosque de árboles enraizados + Pila $\mathrm{LIFO}$ de historial",
                font_size=19,
                color=C_TEXT,
            ),
        )
        tda_lines.arrange(DOWN, buff=0.16, aligned_edge=LEFT)
        tda_lines.next_to(tda_h, DOWN, buff=0.22, aligned_edge=LEFT)

        self._play(Write(tda_h), run_time=0.8)
        self._play(LaggedStart(*[FadeIn(tl, shift=RIGHT * 0.18) for tl in tda_lines], lag_ratio=0.25), run_time=1.4)
        self._wait(3.5)

        ah = MyText(r"Aplicaciones prácticas:", font_size=21, color=C_ACCENT, weight=BOLD)
        ah.next_to(tda_lines, DOWN, buff=0.45, aligned_edge=LEFT)
        apps = VGroup(
            MyText(r"• Conectividad dinámica offline en grafos (aristas que aparecen y desaparecen)", font_size=19, color=C_TEXT2),
            MyText(r"• Divide y Vencerás sobre árbol de segmentos temporal", font_size=19, color=C_TEXT2),
            MyText(r"• Verificación de bipartición dinámica con puntos de control ($\mathrm{snapshots}$)", font_size=19, color=C_TEXT2),
        )
        apps.arrange(DOWN, buff=0.15, aligned_edge=LEFT)
        apps.next_to(ah, DOWN, buff=0.22, aligned_edge=LEFT)

        self._play(Write(ah), run_time=0.8)
        self._play(
            LaggedStart(*[FadeIn(a, shift=RIGHT * 0.18) for a in apps], lag_ratio=0.22),
            run_time=2.5,
        )
        self._wait_until(48.8)
        self._fade(hg, lines, tda_h, tda_lines, ah, apps)

    # ── 3. ¿POR QUÉ SIN COMPRESIÓN DE CAMINOS? (0:50 -> 1:25) ────────

    def _why_no_compression(self):
        hg = self._header(r"¿Por qué NO usar Compresión de Caminos?")

        t_left = MyText(r"1. Con Compresión de Caminos", font_size=22, color=C_RED, weight=BOLD)
        t_left.move_to(np.array([-3.4, 2.0, 0.0]))

        c_coords = [
            np.array([-3.4, 1.25, 0.0]),
            np.array([-4.2, 0.45, 0.0]),
            np.array([-3.4, -0.35, 0.0]),
            np.array([-2.6, -1.05, 0.0]),
        ]
        l_nodes = VGroup()
        for idx, pt in enumerate(c_coords):
            c = Circle(
                radius=0.23,
                color=WHITE if idx == 0 else C_ACCENT,
                fill_color=C_ROOT if idx == 0 else C_INTERNAL,
                fill_opacity=0.92,
                stroke_width=2.4,
            ).move_to(pt)
            l = MyText(f"${idx}$", font_size=16, color=WHITE, weight=BOLD).move_to(pt)
            l_nodes.add(VGroup(c, l))

        l_edges = VGroup(
            make_arrow_between(c_coords[1], c_coords[0], True),
            make_arrow_between(c_coords[2], c_coords[1], False),
            make_arrow_between(c_coords[3], c_coords[2], False),
        )

        self._play(Write(t_left), FadeIn(l_nodes, shift=UP * 0.15), Create(l_edges), run_time=1.6)
        self._wait(1.8)

        # Transición fluida de la cadena hacia la estrella comprimida
        s_coords = [
            np.array([-3.4, 1.25, 0.0]),
            np.array([-4.65, 0.0, 0.0]),
            np.array([-3.4, 0.0, 0.0]),
            np.array([-2.15, 0.0, 0.0]),
        ]
        new_l_edges = VGroup(
            make_arrow_between(s_coords[1], s_coords[0], True).set_color(C_RED),
            make_arrow_between(s_coords[2], s_coords[0], True).set_color(C_RED),
            make_arrow_between(s_coords[3], s_coords[0], True).set_color(C_RED),
        )

        desc_l = VGroup(
            MyText(r"$\mathrm{find}(3)$ reconecta todos los nodos", font_size=17, color=C_TEXT2),
            MyText(r"visitados directo a la raíz $0$.", font_size=17, color=C_TEXT2),
            MyText(r"Se pierde la historia de enlaces:", font_size=17, color=C_RED),
            MyText(r"¡imposible revertir en $\mathcal{O}(1)$!", font_size=17, color=C_RED),
        ).arrange(DOWN, buff=0.14, aligned_edge=LEFT).move_to(np.array([-3.4, -1.75, 0.0]))

        self._play(
            l_nodes[1][0].animate.move_to(s_coords[1]).set_stroke(C_RED),
            l_nodes[1][1].animate.move_to(s_coords[1]),
            l_nodes[2][0].animate.move_to(s_coords[2]).set_stroke(C_RED),
            l_nodes[2][1].animate.move_to(s_coords[2]),
            l_nodes[3][0].animate.move_to(s_coords[3]).set_stroke(C_RED),
            l_nodes[3][1].animate.move_to(s_coords[3]),
            ReplacementTransform(l_edges, new_l_edges),
            FadeIn(desc_l, shift=UP * 0.15),
            run_time=1.6,
        )
        self._wait(3.8)

        # Panel derecho: Unión por Tamaño + Pila
        div = Line(np.array([0.0, 2.2, 0.0]), np.array([0.0, -2.5, 0.0]), color="#333333", stroke_width=1.5)
        t_right = MyText(r"2. Unión por Tamaño + Pila", font_size=22, color=C_GREEN, weight=BOLD)
        t_right.move_to(np.array([3.4, 2.0, 0.0]))

        u_coords = [
            np.array([3.4, 1.25, 0.0]),
            np.array([2.35, 0.2, 0.0]),
            np.array([4.45, 0.2, 0.0]),
            np.array([4.45, -0.82, 0.0]),
        ]
        u_nodes = VGroup()
        for idx, pt in enumerate(u_coords):
            c = Circle(
                radius=0.23,
                color=WHITE if idx == 0 else C_GREEN,
                fill_color=C_ROOT if idx == 0 else C_LEAF,
                fill_opacity=0.92,
                stroke_width=2.4,
            ).move_to(pt)
            l = MyText(f"${idx}$", font_size=16, color=WHITE, weight=BOLD).move_to(pt)
            u_nodes.add(VGroup(c, l))

        u_edges = VGroup(
            make_arrow_between(u_coords[1], u_coords[0], True).set_color(C_GREEN),
            make_arrow_between(u_coords[2], u_coords[0], True).set_color(C_GREEN),
            make_arrow_between(u_coords[3], u_coords[2], False).set_color(C_GREEN),
        )

        desc_r = VGroup(
            MyText(r"Cuelga el árbol menor bajo el mayor.", font_size=17, color=C_TEXT2),
            MyText(r"Altura máxima garantizada: $\leq \log_2(n)$.", font_size=17, color=C_GREEN),
            MyText(r"Cada $\mathrm{join}$ modifica $1$ padre y $1$ tamaño:", font_size=17, color=C_TEXT2),
            MyText(r"¡se guarda en la pila y revierte en $\mathcal{O}(1)$!", font_size=17, color=C_ACCENT),
        ).arrange(DOWN, buff=0.14, aligned_edge=LEFT).move_to(np.array([3.4, -1.75, 0.0]))

        self._play(
            Create(div),
            Write(t_right),
            LaggedStart(*[GrowFromCenter(un) for un in u_nodes], lag_ratio=0.15),
            Create(u_edges),
            FadeIn(desc_r, shift=UP * 0.15),
            run_time=1.9,
        )
        self._wait_until(83.8)
        self._fade(hg, t_left, desc_l, l_nodes, new_l_edges, div, t_right, u_nodes, u_edges, desc_r)

    # ── MOTOR VISUAL FLUIDO PARA LAS SECCIONES INTERACTIVAS (4, 5, 6 y 7) ──

    def _init_interactive_dashboard(self, dsu: DSURollback):
        """Inicializa los paneles fijos de arreglos y pila para animar cambios sin parpadeos."""
        self.static_ui = VGroup()

        arr_title = MyText(r"Arreglos internos:", font_size=18, color=C_ACCENT, weight=BOLD)
        arr_title.move_to(np.array([-4.45, 2.15, 0.0]))

        y_rows = [1.72, 1.33, 0.94]
        h_i = MyText(r"$i$", font_size=16, color=C_TEXT2).move_to(np.array([-5.85, y_rows[0], 0.0]))
        h_p = MyText(r"$\mathrm{parent}[i]$", font_size=15, color=C_ACCENT).move_to(np.array([-5.85, y_rows[1], 0.0]))
        h_s = MyText(r"$\mathrm{size}[i]$", font_size=15, color=C_GREEN).move_to(np.array([-5.85, y_rows[2], 0.0]))

        comp_lbl = MyText(r"Componentes:", font_size=16, color=C_ORANGE, weight=BOLD)
        comp_lbl.move_to(np.array([-4.75, 0.50, 0.0]))
        self.comp_val_mob = MyText(r"$0$", font_size=17, color=C_ORANGE, weight=BOLD)
        self.comp_val_mob.next_to(comp_lbl, RIGHT, buff=0.18)

        st_title = MyText(r"Pila $\mathrm{history}$:", font_size=17, color=C_ORANGE, weight=BOLD)
        st_title.move_to(np.array([-4.65, 0.02, 0.0]))
        self.empty_stack_lbl = MyText(r"$[\ \text{vacía}\ ]$", font_size=15, color=C_TEXT2)
        self.empty_stack_lbl.move_to(np.array([-4.35, -0.42, 0.0]))

        div = Line(np.array([-1.85, 2.35, 0.0]), np.array([-1.85, -2.45, 0.0]), color="#333333", stroke_width=1.5)

        self.idx_cells = []
        self.parent_cells = []
        self.size_cells = []
        for i in range(dsu.n):
            cx = -4.75 + i * 0.48
            ti = MyText(f"${i}$", font_size=15, color=C_TEXT2).move_to(np.array([cx, y_rows[0], 0.0]))
            tp = MyText(r"$-$", font_size=15, color="#555555").move_to(np.array([cx, y_rows[1], 0.0]))
            ts = MyText(r"$0$", font_size=15, color="#555555").move_to(np.array([cx, y_rows[2], 0.0]))
            self.idx_cells.append(ti)
            self.parent_cells.append(tp)
            self.size_cells.append(ts)

        self.static_ui.add(
            arr_title, h_i, h_p, h_s, comp_lbl, st_title, div,
            *self.idx_cells,
        )
        self.stack_entries = []
        self.snap_line_group = None
        self.node_mobs = {}
        self.sz_mobs = {}
        self.edge_mobs = {}
        self._status_lbl = None

        self._play(
            FadeIn(self.static_ui),
            FadeIn(self.comp_val_mob),
            FadeIn(self.empty_stack_lbl),
            FadeIn( VGroup(*self.parent_cells, *self.size_cells) ),
            run_time=1.0,
        )

    def _animate_forest_and_cells(
        self,
        dsu: DSURollback,
        changed_child: int = -1,
        changed_root: int = -1,
        new_edge: tuple[int, int] | None = None,
        removed_edge_child: int = -1,
        push_rec: tuple | None = None,
        pop_stack: bool = False,
        run_time: float = 0.9,
    ):
        """Anima de forma fluida y simultánea el movimiento de nodos, aristas, celdas y pila."""
        new_pos = forest_layout(dsu)
        anims = []

        children_count = {i: 0 for i in range(dsu.n)}
        for i in range(dsu.n):
            if dsu.active[i] and dsu.parent[i] != i:
                children_count[dsu.parent[i]] += 1

        # 1. Deslizar cada nodo hacia su nueva posición y actualizar su color y etiqueta sz
        new_sz_map = {}
        for i in range(dsu.n):
            if i not in self.node_mobs:
                continue
            target_pt = new_pos[i]
            is_root = dsu.parent[i] == i
            if is_root:
                fill_c, stroke_c = C_ROOT, WHITE
            elif children_count[i] > 0:
                fill_c, stroke_c = C_INTERNAL, C_ACCENT
            else:
                fill_c, stroke_c = C_LEAF, C_GREEN

            nvg = self.node_mobs[i]
            anims.append(
                nvg[0].animate.move_to(target_pt).set_fill(fill_c, opacity=0.92).set_stroke(stroke_c, width=2.5)
            )
            anims.append(nvg[1].animate.move_to(target_pt))

            old_sz_mob = self.sz_mobs[i]
            if is_root:
                nsz = MyText(f"$\\mathrm{{sz}}={dsu.size[i]}$", font_size=13, color=C_ELABEL)
                nsz.move_to(target_pt + UP * 0.42)
            else:
                nsz = MyText("", font_size=10).move_to(target_pt + UP * 0.35)
            anims.append(ReplacementTransform(old_sz_mob, nsz))
            new_sz_map[i] = nsz

        # 2. Actualizar aristas existentes, crecer arista nueva o desvanecer arista revertida
        if removed_edge_child in self.edge_mobs:
            old_arr = self.edge_mobs.pop(removed_edge_child)
            anims.append(FadeOut(old_arr))

        for ch_id, arr_mob in list(self.edge_mobs.items()):
            par_id = dsu.parent[ch_id]
            if par_id != ch_id:
                new_arr = make_arrow_between(
                    new_pos[ch_id],
                    new_pos[par_id],
                    dsu.parent[par_id] == par_id,
                )
                anims.append(Transform(arr_mob, new_arr))

        created_arr = None
        if new_edge is not None:
            ch_id, par_id = new_edge
            created_arr = make_arrow_between(
                new_pos[ch_id],
                new_pos[par_id],
                dsu.parent[par_id] == par_id,
            )
            self.edge_mobs[ch_id] = created_arr
            anims.append(GrowArrow(created_arr))

        # 3. Actualizar únicamente las celdas modificadas de parent[i], size[i] y Componentes
        y_rows = [1.72, 1.33, 0.94]
        for i in range(dsu.n):
            cx = -4.75 + i * 0.48
            p_col = YELLOW if i == changed_child else C_TEXT
            new_p = MyText(f"${dsu.parent[i]}$", font_size=15, color=p_col, weight=BOLD).move_to(np.array([cx, y_rows[1], 0.0]))
            anims.append(ReplacementTransform(self.parent_cells[i], new_p))
            self.parent_cells[i] = new_p

            s_col = C_GREEN if i == changed_root else C_TEXT2
            new_s = MyText(f"${dsu.size[i]}$", font_size=15, color=s_col, weight=BOLD if i == changed_root else "normal").move_to(np.array([cx, y_rows[2], 0.0]))
            anims.append(ReplacementTransform(self.size_cells[i], new_s))
            self.size_cells[i] = new_s

        new_comp = MyText(f"${dsu.num_components}$", font_size=17, color=C_ORANGE, weight=BOLD)
        new_comp.move_to(self.comp_val_mob.get_center())
        anims.append(ReplacementTransform(self.comp_val_mob, new_comp))
        self.comp_val_mob = new_comp

        # 4. Animar apilado (push) o desapilado (pop) fluido en la pila history
        if push_rec is not None:
            if len(self.stack_entries) == 0 and self.empty_stack_lbl is not None:
                anims.append(FadeOut(self.empty_stack_lbl))
                self.empty_stack_lbl = None

            # Atenuar color del tope anterior
            if self.stack_entries:
                prev_idx = len(self.stack_entries) - 1
                prev_rec = dsu.history[prev_idx]
                prev_y = -0.38 - prev_idx * 0.36
                dim_entry = MyText(
                    f"$\\#{prev_idx + 1}:\\ u={prev_rec[0]}(p={prev_rec[1]}) \\to r={prev_rec[2]}(\\mathrm{{sz}}={prev_rec[3]})$",
                    font_size=13,
                    color=C_TEXT2,
                ).move_to(np.array([-4.15, prev_y, 0.0]))
                anims.append(ReplacementTransform(self.stack_entries[-1], dim_entry))
                self.stack_entries[-1] = dim_entry

            idx = len(self.stack_entries)
            ch, old_p, rt, old_sz, _ = push_rec
            y_pos = -0.38 - idx * 0.36
            entry_mob = MyText(
                f"$\\#{idx + 1}:\\ u={ch}(p={old_p}) \\to r={rt}(\\mathrm{{sz}}={old_sz})$",
                font_size=13,
                color=YELLOW,
            ).move_to(np.array([-4.15, y_pos, 0.0]))
            self.stack_entries.append(entry_mob)
            anims.append(FadeIn(entry_mob, shift=DOWN * 0.2))

        if pop_stack and self.stack_entries:
            top_mob = self.stack_entries.pop()
            anims.append(FadeOut(top_mob, shift=UP * 0.2))
            if self.stack_entries:
                new_top_idx = len(self.stack_entries) - 1
                rec = dsu.history[new_top_idx]
                y_pos = -0.38 - new_top_idx * 0.36
                hi_entry = MyText(
                    f"$\\#{new_top_idx + 1}:\\ u={rec[0]}(p={rec[1]}) \\to r={rec[2]}(\\mathrm{{sz}}={rec[3]})$",
                    font_size=13,
                    color=YELLOW,
                ).move_to(np.array([-4.15, y_pos, 0.0]))
                anims.append(ReplacementTransform(self.stack_entries[-1], hi_entry))
                self.stack_entries[-1] = hi_entry
            else:
                self.empty_stack_lbl = MyText(r"$[\ \text{vacía}\ ]$", font_size=15, color=C_TEXT2)
                self.empty_stack_lbl.move_to(np.array([-4.35, -0.42, 0.0]))
                anims.append(FadeIn(self.empty_stack_lbl))

        self._play(*anims, run_time=run_time)
        self.sz_mobs = new_sz_map
        self._pos = new_pos

    # ── 4 y 5. MAKE_SET, JOIN Y SNAPSHOT (1:25 -> 2:38) ──────────────

    def _make_set_and_unions(self):
        hg = self._header(r"Inicialización: $\mathrm{make\_set}(x)$ en $\mathcal{O}(1)$")

        dsu = DSURollback(6, auto_init=False)
        self._init_interactive_dashboard(dsu)
        self._set_status(r"Estructura vacía: ejecutando $\mathrm{make\_set}(x)$ para $x \in \{0, 1, 2, 3, 4, 5\}$", C_ACCENT)

        init_pos = forest_layout(dsu)
        y_rows = [1.72, 1.33, 0.94]

        # Animar make_set(0) .. make_set(5) de forma fluida
        for x in range(6):
            list(dsu.make_set(x))
            pt = init_pos[x]
            circ = Circle(
                radius=0.27,
                color=WHITE,
                fill_color=C_ROOT,
                fill_opacity=0.92,
                stroke_width=2.5,
            ).move_to(pt)
            lbl = MyText(f"${x}$", font_size=17, color=WHITE, weight=BOLD).move_to(pt)
            nvg = VGroup(circ, lbl)
            sz_lbl = MyText(r"$\mathrm{sz}=1$", font_size=13, color=C_ELABEL).move_to(pt + UP * 0.42)

            self.node_mobs[x] = nvg
            self.sz_mobs[x] = sz_lbl

            cx = -4.75 + x * 0.48
            new_p = MyText(f"${x}$", font_size=15, color=YELLOW, weight=BOLD).move_to(np.array([cx, y_rows[1], 0.0]))
            new_s = MyText(r"$1$", font_size=15, color=C_GREEN, weight=BOLD).move_to(np.array([cx, y_rows[2], 0.0]))
            new_comp = MyText(f"${dsu.num_components}$", font_size=17, color=C_ORANGE, weight=BOLD).move_to(self.comp_val_mob.get_center())

            self._play(
                GrowFromCenter(nvg),
                FadeIn(sz_lbl, shift=UP * 0.1),
                ReplacementTransform(self.parent_cells[x], new_p),
                ReplacementTransform(self.size_cells[x], new_s),
                ReplacementTransform(self.comp_val_mob, new_comp),
                run_time=0.55,
            )
            self.parent_cells[x] = new_p
            self.size_cells[x] = new_s
            self.comp_val_mob = new_comp

        self._pos = init_pos
        self._set_status(
            r"$\mathrm{make\_set}(0..5)$ completado: $6$ conjuntos unitarios con $\mathrm{parent}[i]=i$ y $\mathrm{size}[i]=1$",
            C_GREEN,
        )
        self._wait_until(105.0)

        # Cambiar encabezado suavemente a Operaciones join(u, v) y snapshot()
        new_hg = MyText(r"Operaciones: $\mathrm{join}(u, v)$ y $\mathrm{snapshot}()$", font_size=28, color=WHITE, weight=BOLD).to_edge(UP, buff=0.42)
        new_ln = Line(new_hg.get_left() + DOWN * 0.18, new_hg.get_right() + DOWN * 0.18, color=C_ACCENT, stroke_width=2)
        new_header_group = VGroup(new_hg, new_ln)
        self._play(ReplacementTransform(hg, new_header_group), run_time=0.7)
        hg = new_header_group

        operations = [
            ("join", 0, 1, 114.0),
            ("join", 2, 3, 123.0),
            ("join", 1, 3, 133.0),
            ("snapshot", 140.0),
            ("join", 4, 5, 149.0),
            ("join", 5, 3, 158.0),
        ]

        snap_val = None
        for op in operations:
            if op[0] == "snapshot":
                target_t = op[1]
                snap_val = dsu.snapshot()
                self._set_status(
                    f"$\\mathrm{{snapshot}}() \\to$ guarda marca temporal en $\\mathrm{{tam\\_pila}} = {snap_val}$",
                    C_ACCENT,
                )
                snap_y = -0.38 - (snap_val - 0.5) * 0.36
                s_line = DashedLine(
                    np.array([-6.2, snap_y, 0.0]),
                    np.array([-2.1, snap_y, 0.0]),
                    color=C_ACCENT,
                    stroke_width=2.2,
                )
                s_lbl = MyText(f"$\\mathrm{{snap}}={snap_val}$", font_size=12, color=C_ACCENT).next_to(s_line, LEFT, buff=0.06)
                self.snap_line_group = VGroup(s_line, s_lbl)
                self._play(Create(s_line), FadeIn(s_lbl, shift=RIGHT * 0.1), run_time=0.8)
                self._wait_until(target_t)
                continue

            _, u, v, target_t = op
            evts = list(dsu.join(u, v))
            merged_child, merged_root, new_sz, comps = -1, -1, 0, dsu.num_components
            for e in evts:
                if e[0] == "join_merged":
                    merged_child, merged_root, new_sz, comps = e[1], e[2], e[3], e[4]

            self._play(
                Flash(self.node_mobs[u][0], color=YELLOW, flash_radius=0.38),
                Flash(self.node_mobs[v][0], color=YELLOW, flash_radius=0.38),
                run_time=0.75,
            )

            self._set_status(
                f"$\\mathrm{{join}}({u}, {v}) \\to$ une raíz ${merged_child}$ bajo raíz ${merged_root}$ "
                f"$(\\mathrm{{size}}[{merged_root}]={new_sz},\\ \\mathrm{{grupos}}={comps})$",
                C_GREEN,
                run_time=0.4,
            )

            self._animate_forest_and_cells(
                dsu,
                changed_child=merged_child,
                changed_root=merged_root,
                new_edge=(merged_child, merged_root),
                push_rec=dsu.history[-1],
                run_time=1.05,
            )
            self._wait_until(target_t)

        self._dsu = dsu
        self._snap_val = snap_val
        self._hg_unions = hg

    # ── 6. BÚSQUEDA FIND SIN COMPRESIÓN (2:38 -> 3:05) ───────────────

    def _find_query(self):
        new_hg = MyText(r"Búsqueda sin Compresión: $\mathrm{find}(x)$ en $\mathcal{O}(\log n)$", font_size=28, color=WHITE, weight=BOLD).to_edge(UP, buff=0.42)
        new_ln = Line(new_hg.get_left() + DOWN * 0.18, new_hg.get_right() + DOWN * 0.18, color=C_ACCENT, stroke_width=2)
        hg = VGroup(new_hg, new_ln)
        self._play(ReplacementTransform(self._hg_unions, hg), run_time=0.7)

        dsu = self._dsu
        pos = self._pos

        # Consulta 1: find(3) recorre 3 -> 2 -> 0
        self._set_status(r"Consulta 1: $\mathrm{find}(3)$ recorre $[3 \to 2 \to 0]$ sin alterar $\mathrm{parent}[3]=2$", C_ACCENT)
        tracker = Dot(color=C_ORANGE, radius=0.14).move_to(pos[3])
        self._play(FadeIn(tracker, scale=1.8), run_time=0.55)

        for ev in dsu.find(3):
            if ev[0] == "find_step":
                curr, nxt = ev[1], ev[2]
                self._play(Flash(self.node_mobs[curr][0], color=C_ORANGE, flash_radius=0.36), run_time=0.55)
                self._play(tracker.animate.move_to(pos[nxt]), run_time=0.65)
            elif ev[0] == "find_root":
                root_id = ev[2]
                self._play(Flash(self.node_mobs[root_id][0], color=C_GREEN, flash_radius=0.40), run_time=0.75)

        self._set_status(r"$\mathrm{find}(3) = 0$  ($\mathrm{parent}[3]$ se mantiene en $2$)", C_GREEN)
        self._wait_until(171.0)

        # Consulta 2: find(5) recorre 5 -> 4 -> 0
        self._set_status(r"Consulta 2: $\mathrm{find}(5)$ recorre $[5 \to 4 \to 0]$ hasta la misma raíz $0$", C_ACCENT)
        self._play(tracker.animate.move_to(pos[5]), run_time=0.65)

        for ev in dsu.find(5):
            if ev[0] == "find_step":
                curr, nxt = ev[1], ev[2]
                self._play(Flash(self.node_mobs[curr][0], color=C_ORANGE, flash_radius=0.36), run_time=0.55)
                self._play(tracker.animate.move_to(pos[nxt]), run_time=0.65)
            elif ev[0] == "find_root":
                root_id = ev[2]
                self._play(Flash(self.node_mobs[root_id][0], color=C_GREEN, flash_radius=0.40), run_time=0.75)

        self._set_status(r"$\mathrm{find}(3) = \mathrm{find}(5) = 0 \Rightarrow$ Pertenecen a la misma componente", C_GREEN)
        self._play(FadeOut(tracker), run_time=0.45)
        self._wait_until(185.0)
        self._hg_find = hg

    # ── 7. DEMOSTRACIÓN DE ROLLBACK (3:05 -> 3:39) ───────────────────

    def _rollback_demo(self):
        new_hg = MyText(r"Reversión de Estado: $\mathrm{rollback}()$ en $\mathcal{O}(1)$", font_size=28, color=WHITE, weight=BOLD).to_edge(UP, buff=0.42)
        new_ln = Line(new_hg.get_left() + DOWN * 0.18, new_hg.get_right() + DOWN * 0.18, color=C_ACCENT, stroke_width=2)
        hg = VGroup(new_hg, new_ln)
        self._play(ReplacementTransform(self._hg_find, hg), run_time=0.7)

        dsu = self._dsu
        snap_val = self._snap_val

        self._set_status(
            f"Objetivo: $\\mathrm{{rollback\\_to}}(\\mathrm{{snap}} = {snap_val})$ desapilando en orden $\\mathrm{{LIFO}}$",
            C_ORANGE,
        )
        self._wait(1.2)

        # Revertir las 2 uniones posteriores al snapshot
        for _ in range(2):
            evts = list(dsu.rollback())
            ch, old_p, rt, old_sz, comps = -1, -1, -1, 0, dsu.num_components
            for e in evts:
                if e[0] == "rollback_restored":
                    ch, old_p, rt, old_sz, comps = e[1], e[2], e[3], e[4], e[5]

            self._set_status(
                f"$\\mathrm{{rollback}}() \\to$ restaura $\\mathrm{{parent}}[{ch}]={old_p},\\ \\mathrm{{size}}[{rt}]={old_sz}$ "
                f"$(\\mathrm{{grupos}}={comps})$",
                C_RED,
                run_time=0.4,
            )
            self._animate_forest_and_cells(
                dsu,
                changed_child=ch,
                changed_root=rt,
                removed_edge_child=ch,
                pop_stack=True,
                run_time=1.05,
            )
            self._play(Flash(self.node_mobs[ch][0], color=C_RED, flash_radius=0.38), run_time=0.6)
            self._wait(1.6)

        self._set_status(
            f"¡Estado exacto del $\\mathrm{{snapshot}} = {snap_val}$ restaurado! Ahora revertimos hasta el inicio...",
            C_GREEN,
        )
        self._wait_until(201.0)

        if self.snap_line_group is not None:
            self._play(FadeOut(self.snap_line_group), run_time=0.4)
            self.snap_line_group = None

        # Revertir las 3 uniones restantes hasta dejar los 6 nodos aislados
        while len(dsu.history) > 0:
            evts = list(dsu.rollback())
            ch, old_p, rt, old_sz, comps = -1, -1, -1, 0, dsu.num_components
            for e in evts:
                if e[0] == "rollback_restored":
                    ch, old_p, rt, old_sz, comps = e[1], e[2], e[3], e[4], e[5]

            self._set_status(
                f"$\\mathrm{{rollback}}() \\to$ restaura $\\mathrm{{parent}}[{ch}]={old_p},\\ \\mathrm{{size}}[{rt}]={old_sz}$ "
                f"$(\\mathrm{{grupos}}={comps})$",
                C_RED,
                run_time=0.35,
            )
            self._animate_forest_and_cells(
                dsu,
                changed_child=ch,
                changed_root=rt,
                removed_edge_child=ch,
                pop_stack=True,
                run_time=0.95,
            )
            self._wait(0.9)

        self._wait_until(217.8)

        all_dashboard = [
            hg,
            self.static_ui,
            self.comp_val_mob,
            *self.parent_cells,
            *self.size_cells,
            *self.node_mobs.values(),
            *self.sz_mobs.values(),
            *self.edge_mobs.values(),
        ]
        if self.empty_stack_lbl is not None:
            all_dashboard.append(self.empty_stack_lbl)
        if self._status_lbl is not None:
            all_dashboard.append(self._status_lbl)

        self._fade(*all_dashboard)

    # ── 8. CASOS BORDE (3:39 -> 4:04) ────────────────────────────────

    def _edge_cases(self):
        hg = self._header(r"Casos Borde")

        # -- Caso 1: Unión redundante en la misma componente --
        c1t = MyText(r"Caso 1: Unión redundante ($\mathrm{find}(u) = \mathrm{find}(v)$)", font_size=24, color=C_ORANGE, weight=BOLD)
        c1t.next_to(hg, DOWN, buff=0.6).to_edge(LEFT, buff=0.9)

        l1 = VGroup(
            MyText(r"• Si $u$ y $v$ ya pertenecen al mismo conjunto, sus raíces coinciden.", font_size=20, color=C_TEXT2),
            MyText(r"• Si se unieran de nuevo, se crearía un ciclo o se duplicaría $\mathrm{size}[\mathrm{raíz}]$.", font_size=20, color=C_RED),
            MyText(r"• Solución: detectar $\mathrm{root}_u = \mathrm{root}_v$ y retornar $\mathrm{False}$ sin apilar en $\mathrm{history}$.", font_size=20, color=C_GREEN),
        ).arrange(DOWN, buff=0.22, aligned_edge=LEFT).next_to(c1t, DOWN, buff=0.38, aligned_edge=LEFT)

        demo_dsu = DSURollback(4)
        list(demo_dsu.join(0, 1))
        red_evts = list(demo_dsu.join(0, 1))
        ev_name1 = red_evts[-1][0].replace("_", r"\_")
        demo_code1 = MyText(
            f"$\\mathrm{{join}}(0, 1)$ por segunda vez $\\to$ evento: $\\mathrm{{{ev_name1}}}$ | $\\mathrm{{tam\\_pila}} = {len(demo_dsu.history)}$",
            font_size=18,
            color=C_ACCENT,
        ).next_to(l1, DOWN, buff=0.42, aligned_edge=LEFT)

        self._play(Write(c1t), run_time=0.8)
        self._play(LaggedStart(*[FadeIn(x, shift=RIGHT * 0.18) for x in l1], lag_ratio=0.22), run_time=1.8)
        self._play(FadeIn(demo_code1, shift=UP * 0.12), run_time=0.7)
        self._wait_until(231.2)
        self._play(FadeOut(VGroup(c1t, l1, demo_code1), shift=UP * 0.1), run_time=0.65)

        # -- Caso 2: Rollback con la pila vacía --
        c2t = MyText(r"Caso 2: Invocar $\mathrm{rollback}()$ con la pila vacía", font_size=24, color=C_ORANGE, weight=BOLD)
        c2t.next_to(hg, DOWN, buff=0.6).to_edge(LEFT, buff=0.9)

        l2 = VGroup(
            MyText(r"• Cuando $\mathrm{history}$ está vacía (sin uniones previas o tras revertir todo),", font_size=20, color=C_TEXT2),
            MyText(r"• intentar desapilar causaría un error de subdesbordamiento ($\mathrm{underflow}$).", font_size=20, color=C_RED),
            MyText(r"• Solución: verificar $\mathrm{if\ not\ self.history}$ en $\mathcal{O}(1)$ y mantener el estado intacto.", font_size=20, color=C_GREEN),
        ).arrange(DOWN, buff=0.22, aligned_edge=LEFT).next_to(c2t, DOWN, buff=0.38, aligned_edge=LEFT)

        empty_dsu = DSURollback(4)
        emp_evts = list(empty_dsu.rollback())
        ev_name2 = emp_evts[-1][0].replace("_", r"\_")
        demo_code2 = MyText(
            f"$\\mathrm{{rollback}}()$ con $\\mathrm{{history}}=[] \\to$ evento: $\\mathrm{{{ev_name2}}}$ | $\\mathrm{{componentes}} = {empty_dsu.num_components}$",
            font_size=18,
            color=C_ACCENT,
        ).next_to(l2, DOWN, buff=0.42, aligned_edge=LEFT)

        self._play(Write(c2t), run_time=0.8)
        self._play(LaggedStart(*[FadeIn(x, shift=RIGHT * 0.18) for x in l2], lag_ratio=0.22), run_time=1.8)
        self._play(FadeIn(demo_code2, shift=UP * 0.12), run_time=0.7)
        self._wait_until(242.8)
        self._fade(hg, c2t, l2, demo_code2)

    # ── 9. COMPLEJIDAD TEMPORAL (4:04 -> 4:14) ───────────────────────

    def _complexity(self):
        hg = self._header(r"Complejidad Temporal")

        vn = MyText(
            r"$n =$ número de elementos   |   Altura máxima con Union by Size $\leq \log_2(n)$",
            font_size=18,
            color=C_TEXT2,
        )
        vn.next_to(hg, DOWN, buff=0.32)
        self._play(FadeIn(vn), run_time=0.5)

        data = [
            (r"Operación", r"Complejidad", r"Justificación"),
            (r"$\mathrm{make\_set}(x)$", r"$\mathcal{O}(1)$", r"Inicializa $\mathrm{parent}[x]=x$ y $\mathrm{size}[x]=1$"),
            (r"$\mathrm{find}(x)$", r"$\mathcal{O}(\log n)$", r"Sube a lo más $\log_2(n)$ niveles hasta la raíz"),
            (r"$\mathrm{join}(u, v)$", r"$\mathcal{O}(\log n)$  [enlace $\mathcal{O}(1)$]", r"$2$ búsquedas $\mathrm{find}$ + enlace y $\mathrm{push}$ en $\mathcal{O}(1)$"),
            (r"$\mathrm{snapshot}()$", r"$\mathcal{O}(1)$", r"Retorna $\mathrm{len(history)}$ en tiempo constante"),
            (r"$\mathrm{rollback}()$", r"$\mathcal{O}(1)$", r"Desapila el tope y restaura $\mathrm{parent}$ y $\mathrm{size}$"),
        ]
        cw = [2.8, 3.3, 5.5]
        rows = VGroup()
        for ri, row in enumerate(data):
            rv = VGroup()
            xo = 0
            for ci, cell in enumerate(row):
                if ri == 0:
                    t = MyText(cell, font_size=18, color=C_ACCENT, weight=BOLD)
                elif ci == 1:
                    c = C_GREEN if (r"\mathcal{O}(1)" in cell and r"\log" not in cell) else C_ORANGE
                    t = MyText(cell, font_size=17, color=c, weight=BOLD)
                else:
                    t = MyText(cell, font_size=16, color=C_TEXT2)
                t.move_to(np.array([xo + cw[ci] / 2.0, 0.0, 0.0]))
                xo += cw[ci]
                rv.add(t)
            rows.add(rv)
        rows.arrange(DOWN, buff=0.25)
        rows.next_to(vn, DOWN, buff=0.35).center().shift(DOWN * 0.25)

        sep = Line(
            rows[0].get_left() + DOWN * 0.16,
            rows[0].get_right() + DOWN * 0.16,
            color=C_TEXT2,
            stroke_width=1,
        )

        self._play(FadeIn(rows[0]), Create(sep), run_time=0.7)
        self._play(LaggedStart(*[FadeIn(r, shift=UP * 0.1) for r in rows[1:]], lag_ratio=0.18), run_time=1.8)
        self._wait_until(252.8)
        self._fade(hg, vn, rows, sep)

    # ── 10. CRÉDITOS (4:14 -> 4:22) ──────────────────────────────────

    def _credits(self):
        th = MyText(r"Integrantes", font_size=34, color=WHITE, weight=BOLD)
        th.shift(UP * 1.6)
        self._play(Write(th), run_time=0.8)

        names = VGroup()
        for name in INTEGRANTES:
            names.add(MyText(name, font_size=24, color=C_ACCENT))
        names.arrange(DOWN, buff=0.24)
        names.next_to(th, DOWN, buff=0.42)
        self._play(
            LaggedStart(*[FadeIn(n, shift=LEFT * 0.25) for n in names], lag_ratio=0.22),
            run_time=1.3,
        )

        uni = MyText(UNIVERSIDAD, font_size=18, color=C_TEXT2)
        uni.next_to(names, DOWN, buff=0.45)
        gracias = MyText(r"¡Gracias!", font_size=42, color=C_ACCENT, weight=BOLD)
        gracias.next_to(uni, DOWN, buff=0.45)
        self._play(FadeIn(uni, shift=UP * 0.1), Write(gracias), run_time=1.1)
        self._wait_until(260.8)
        self._fade(th, names, uni, gracias)
