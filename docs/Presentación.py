from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
import copy

# ─── Color palette (DARK THEME) ───────────────────────────────────────────────
NAVY      = RGBColor(0x0B, 0x0F, 0x1A)   # Ultra-deep navy
NAVY_ALT  = RGBColor(0x0F, 0x17, 0x2A)   # Slightly lighter navy for alternating slides
HEADER_BG = RGBColor(0x06, 0x0B, 0x18)   # Darkest header band
BLUE_MID  = RGBColor(0x3B, 0x82, 0xF6)   # Blue 500 — vibrant
SKY       = RGBColor(0x38, 0xBD, 0xF8)   # Sky 400
CYAN      = RGBColor(0x22, 0xD3, 0xEE)   # Cyan 400 — electric
GOLD      = RGBColor(0xFB, 0xBF, 0x24)   # Amber 400 — brighter gold
WHITE     = RGBColor(0xFF, 0xFF, 0xFF)
OFFWHITE  = RGBColor(0xE2, 0xE8, 0xF0)   # Slate 200 — body text on dark
DARK_TEXT = RGBColor(0xF1, 0xF5, 0xF9)   # Slate 100 — primary text on dark
MID_GRAY  = RGBColor(0x94, 0xA3, 0xB8)   # Slate 400 — secondary text
LIGHT_BG  = RGBColor(0x0D, 0x12, 0x22)   # Deep dark bg
CARD_BG   = RGBColor(0x10, 0x1B, 0x30)   # Dark card fill
CARD_ALT  = RGBColor(0x14, 0x20, 0x3A)   # Slightly lighter card variant
GLASS     = RGBColor(0x1A, 0x27, 0x44)   # Glassmorphism card
GREEN_OK  = RGBColor(0x34, 0xD3, 0x99)   # Emerald 400 — vibrant on dark
RED_ERR   = RGBColor(0xF8, 0x71, 0x71)   # Red 400 — softer red on dark
PURPLE    = RGBColor(0xA7, 0x8B, 0xFA)   # Violet 400

def hex_to_rgb(h):
    return RGBColor(int(h[0:2],16), int(h[2:4],16), int(h[4:6],16))

prs = Presentation()
prs.slide_width  = Inches(13.333)
prs.slide_height = Inches(7.5)

W = 13.333
H = 7.5

def blank_slide():
    blank = prs.slide_layouts[6]
    return prs.slides.add_slide(blank)

def bg(slide, color):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color

def rect(slide, x, y, w, h, fill_rgb, radius=False):
    from pptx.util import Inches
    shape = slide.shapes.add_shape(
        1 if not radius else 5,  # MSO_SHAPE_TYPE RECTANGLE=1, ROUNDED_RECT=5
        Inches(x), Inches(y), Inches(w), Inches(h)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_rgb
    shape.line.fill.background()
    return shape

def add_text(slide, text, x, y, w, h,
             size=16, color=OFFWHITE, bold=False, italic=False,
             align=PP_ALIGN.LEFT, valign=None, wrap=True, font="Calibri"):
    from pptx.util import Inches, Pt
    txb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = txb.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.color.rgb = color
    run.font.bold = bold
    run.font.italic = italic
    run.font.name = font
    return txb

def add_rich_text(slide, runs, x, y, w, h, align=PP_ALIGN.LEFT, wrap=True, line_spacing=None):
    """runs = list of (text, size, color, bold, italic, breakline)"""
    from pptx.util import Inches, Pt
    from pptx.oxml.ns import qn
    from lxml import etree
    txb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = txb.text_frame
    tf.word_wrap = wrap
    first = True
    for item in runs:
        if first:
            p = tf.paragraphs[0]
            first = False
        else:
            p = tf.add_paragraph()
        p.alignment = align
        text, size, color, bold, italic = item[:5]
        run = p.add_run()
        run.text = text
        run.font.size = Pt(size)
        run.font.color.rgb = color
        run.font.bold = bold
        run.font.italic = italic
        run.font.name = "Calibri"
    return txb

def card(slide, x, y, w, h, fill=CARD_BG, shadow=True):
    from pptx.util import Inches
    from pptx.dml.color import RGBColor
    if shadow:
        try:
            hex_str = str(fill)
            r, g, b = int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16)
            is_dark = (r + g + b) < 384
        except:
            is_dark = False
        shadow_color = RGBColor(0x03, 0x05, 0x0A) if is_dark else RGBColor(0x05, 0x0A, 0x15)
        sh = slide.shapes.add_shape(5, Inches(x+0.05), Inches(y+0.05), Inches(w), Inches(h))
        sh.fill.solid()
        sh.fill.fore_color.rgb = shadow_color
        sh.line.fill.background()
        sh.adjustments[0] = 0.06
    shape = slide.shapes.add_shape(5, Inches(x), Inches(y), Inches(w), Inches(h))  # ROUNDED_RECTANGLE
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.fill.background()
    shape.adjustments[0] = 0.06
    return shape

def divider(slide, x, y, w, color=SKY, thickness=0.025):
    from pptx.util import Inches
    shape = slide.shapes.add_shape(1, Inches(x), Inches(y), Inches(w), Inches(thickness))
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 1 — PORTADA
# ══════════════════════════════════════════════════════════════════════════════
s = blank_slide()
bg(s, NAVY)

# Decorative left panel
r = rect(s, 0, 0, 3.8, H, RGBColor(0x05, 0x0C, 0x1E))

# Vertical accent
r2 = rect(s, 3.8, 0, 0.08, H, SKY)

# Dot grid decoration (simulated with small rects)
for i in range(8):
    for j in range(12):
        dot = rect(s, 0.35 + j*0.27, 0.5 + i*0.7, 0.07, 0.07, RGBColor(0x1E, 0x40, 0x6E))

# Plane silhouette shape (abstract)
r3 = rect(s, 0.6, 2.8, 2.6, 0.18, SKY)   # fuselage
r4 = rect(s, 1.0, 2.25, 0.18, 1.3, SKY)   # tail
r5 = rect(s, 0.95, 2.62, 1.9, 0.12, CYAN)  # wing
r6 = rect(s, 2.8, 2.75, 0.7, 0.09, CYAN)  # nose

# 3D box decorations on right side
boxes = [
    (9.8, 2.2, 1.2, 0.9, RGBColor(0x2D, 0x9C, 0xCD)),
    (11.1, 2.6, 1.0, 0.8, RGBColor(0x0D, 0x6E, 0xFD)),
    (10.3, 3.3, 1.4, 0.8, RGBColor(0x05, 0x96, 0x69)),
    (11.9, 3.1, 0.9, 0.7, RGBColor(0xF5, 0x9E, 0x0B)),
    (10.8, 4.0, 1.1, 0.75, RGBColor(0x7C, 0x3A, 0xED)),
    (12.1, 4.1, 0.8, 0.8, RGBColor(0xE1, 0x1D, 0x48)),
]
for bx,by,bw,bh,bc in boxes:
    card(s, bx, by, bw, bh, fill=bc)

# Title
add_text(s, "OPTIMIZACIÓN TRIDIMENSIONAL", 4.2, 1.3, 8.8, 0.85,
         size=30, color=WHITE, bold=True, font="Cambria",
         align=PP_ALIGN.LEFT)
add_text(s, "DE CARGA AEROPORTUARIA", 4.2, 2.05, 8.8, 0.75,
         size=30, color=WHITE, bold=True, font="Cambria",
         align=PP_ALIGN.LEFT)

# Subtitle
add_text(s, "3D Bin Packing con restricciones físicas y balance estático", 4.2, 2.85,
         8.8, 0.55, size=16, color=SKY, bold=False, italic=True, align=PP_ALIGN.LEFT)

divider(s, 4.2, 3.5, 6.5, color=SKY)

# Authors & info
add_text(s, "Leonardo Duran Cuenca  |  Diego Villazón Arce", 4.2, 3.65, 8.8, 0.45,
         size=13, color=RGBColor(0xCB, 0xD5, 0xE1), align=PP_ALIGN.LEFT)
add_text(s, "Universidad Católica Boliviana 'San Pablo'", 4.2, 4.1, 8.8, 0.4,
         size=12, color=MID_GRAY, align=PP_ALIGN.LEFT)

# Tags
tags = ["MILP", "Pyomo + CPLEX", "3D BPP", "Knapsack", "Centro de Gravedad"]
tx = 4.2
for tag in tags:
    tw = len(tag) * 0.12 + 0.3
    r_tag = rect(s, tx, 4.65, tw, 0.33, RGBColor(0x1E, 0x3A, 0x5F))
    add_text(s, tag, tx+0.08, 4.67, tw-0.1, 0.28, size=10, color=WHITE, bold=True, align=PP_ALIGN.LEFT)
    tx += tw + 0.18

add_text(s, "Materia: Optimización  |  11 de junio de 2026", 4.2, 5.15, 8.8, 0.4,
         size=11, color=MID_GRAY, italic=True, align=PP_ALIGN.LEFT)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 2 — EL PROBLEMA
# ══════════════════════════════════════════════════════════════════════════════
s = blank_slide()
bg(s, NAVY_ALT)

# Header band
rect(s, 0, 0, W, 1.15, HEADER_BG)
add_text(s, "El Problema", 0.5, 0.15, 8, 0.85, size=34, color=WHITE, bold=True,
         font="Cambria", align=PP_ALIGN.LEFT)
add_text(s, "Logística aeroportuaria moderna", 8.8, 0.35, 4.2, 0.5,
         size=12, color=SKY, italic=True, align=PP_ALIGN.RIGHT)

# Left column - description
add_text(s, "¿Qué buscamos resolver?", 0.5, 1.35, 6.0, 0.4,
         size=18, color=SKY, bold=True)

paras = [
    "Cargar mercancía en una aeronave no es un problema trivial. Cada vuelo exige tomar decisiones simultáneas sobre:",
    "  → Qué cajas viajan y cuáles se quedan en tierra (Knapsack)",
    "  → En qué compartimiento va cada caja (Bin Packing)",
    "  → Las coordenadas exactas (x, y, z) de cada pieza",
    "  → Que el peso distribuido mantenga el Centro de Gravedad en rango seguro",
]
cy = 1.82
for i, p in enumerate(paras):
    sz = 13 if i == 0 else 12
    bold = False
    col = OFFWHITE if i == 0 else RGBColor(0xCB, 0xD5, 0xE1)
    add_text(s, p, 0.5 if i==0 else 0.65, cy, 6.0, 0.38, size=sz, color=col, bold=bold)
    cy += 0.42

add_text(s, "El objetivo es maximizar el valor económico del flete, garantizando viabilidad geométrica y seguridad de vuelo.",
         0.5, 4.18, 6.0, 0.7, size=13, color=MID_GRAY, italic=True)

# Divider
divider(s, 6.9, 1.2, 0.06, color=RGBColor(0x1E, 0x40, 0x6E), thickness=5.8)

# Right column - 3 challenge cards
challenges = [
    ("NP-hard", "Espacio de soluciones crece factorialmente con el número de cajas", GOLD, "⚡"),
    ("Multi-restricción", "Dimensiones, peso, no traslape y balance acoplados simultáneamente", SKY, "🔗"),
    ("Tiempo real", "La aerolínea necesita respuestas en segundos, no horas", GREEN_OK, "⏱"),
]
cy2 = 1.3
for title, desc, color, icon in challenges:
    card(s, 7.3, cy2, 5.5, 1.2, fill=CARD_BG)
    add_text(s, title, 7.6, cy2+0.1, 4.8, 0.4, size=16, color=color, bold=True)
    add_text(s, desc, 7.6, cy2+0.5, 4.8, 0.6, size=12, color=OFFWHITE)
    cy2 += 1.35

# Bottom stat callouts
stats = [("2", "aeronaves de prueba"), ("13", "cajas en inventario"), ("40+", "variables binarias"), ("120s", "límite de cómputo")]
sx = 0.55
for val, label in stats:
    rect(s, sx, 5.35, 2.8, 1.8, HEADER_BG)
    add_text(s, val, sx+0.1, 5.5, 2.6, 0.75, size=36, color=SKY, bold=True, align=PP_ALIGN.CENTER, font="Cambria")
    add_text(s, label, sx+0.1, 6.2, 2.6, 0.4, size=11, color=RGBColor(0xCB,0xD5,0xE1), align=PP_ALIGN.CENTER)
    sx += 3.1

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 3 — MARCO TEÓRICO
# ══════════════════════════════════════════════════════════════════════════════
s = blank_slide()
bg(s, NAVY)

rect(s, 0, 0, W, 1.15, HEADER_BG)
add_text(s, "Marco Teórico", 0.5, 0.15, 8, 0.85, size=34, color=WHITE, bold=True, font="Cambria")
add_text(s, "Fundamentos computacionales del modelo", 8.0, 0.35, 5.0, 0.5, size=12, color=SKY, italic=True, align=PP_ALIGN.RIGHT)

# Two main theory blocks
# Left: 3D BPP
card(s, 0.4, 1.3, 5.9, 2.6, fill=RGBColor(0x0D, 0x22, 0x45))
add_text(s, "3D Bin Packing Problem", 0.7, 1.45, 5.3, 0.5, size=17, color=SKY, bold=True)
add_text(s, "Dado un conjunto de cajas con dimensiones (dx, dy, dz) y un conjunto de contenedores (compartimientos), asignar cada caja a un contenedor tal que ningún par se traslape y todos quepan dentro de los límites.",
         0.7, 1.98, 5.3, 1.0, size=12, color=RGBColor(0xCB,0xD5,0xE1))
add_text(s, "Complejidad: NP-hard", 0.7, 3.05, 3.5, 0.35, size=12, color=GOLD, bold=True)
add_text(s, "El espacio de soluciones crece O(n!) con n cajas", 0.7, 3.35, 5.3, 0.35, size=11, color=MID_GRAY, italic=True)

# Right: Knapsack
card(s, 6.85, 1.3, 5.9, 2.6, fill=RGBColor(0x0D, 0x22, 0x45))
add_text(s, "Knapsack Problem", 7.15, 1.45, 5.3, 0.5, size=17, color=GREEN_OK, bold=True)
add_text(s, "Seleccionar un subconjunto de artículos con valores v_i y pesos w_i que maximice la suma de valores, sin exceder la capacidad total de la mochila.",
         7.15, 1.98, 5.3, 1.0, size=12, color=RGBColor(0xCB,0xD5,0xE1))
add_text(s, "Complejidad: NP-hard", 7.15, 3.05, 3.5, 0.35, size=12, color=GOLD, bold=True)
add_text(s, "Subconjunto óptimo en O(2^n) sin DP o MILP", 7.15, 3.35, 5.3, 0.35, size=11, color=MID_GRAY, italic=True)

# Union indicator
add_text(s, "+", 6.1, 2.3, 0.7, 0.9, size=42, color=SKY, bold=True, align=PP_ALIGN.CENTER)

# MILP section
card(s, 0.4, 4.1, 12.35, 2.1, fill=RGBColor(0x06, 0x1A, 0x40))
add_text(s, "Programación Lineal Entera Mixta (MILP) — La solución exacta", 0.7, 4.2, 11.0, 0.45, size=16, color=WHITE, bold=True)

cols = [
    ("Optimalidad Global", "A diferencia de heurísticas (First-Fit, algoritmos genéticos), MILP garantiza la solución óptima global o una solución con GAP controlado.", RGBColor(0x0D,0x4F,0x8C)),
    ("Restricciones Duras", "Permite modelar restricciones físicas acopladas (traslape, CG, contención) que las heurísticas suelen violar o ignorar.", RGBColor(0x05,0x60,0x5E)),
    ("Linealización Big-M", "La técnica 'M Grande' convierte condiciones lógicas no lineales en restricciones lineales, manteniendo el solver en territorio polinomial.", RGBColor(0x4C,0x1D,0x95)),
]
cx = 0.6
for title, desc, col in cols:
    add_text(s, title, cx, 4.72, 3.9, 0.35, size=13, color=SKY, bold=True)
    add_text(s, desc, cx, 5.08, 3.9, 0.95, size=11, color=RGBColor(0xCB,0xD5,0xE1))
    cx += 4.1

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 4 — MODELO MILP: VARIABLES Y CONJUNTOS
# ══════════════════════════════════════════════════════════════════════════════
s = blank_slide()
bg(s, NAVY_ALT)

rect(s, 0, 0, W, 1.15, HEADER_BG)
add_text(s, "Formulación MILP", 0.5, 0.15, 9, 0.85, size=34, color=WHITE, bold=True, font="Cambria")
add_text(s, "Conjuntos, parámetros y variables", 9.0, 0.35, 4.0, 0.5, size=12, color=SKY, italic=True, align=PP_ALIGN.RIGHT)

# Three column layout
# Col 1: Conjuntos
card(s, 0.35, 1.3, 3.8, 5.6, fill=CARD_BG)
add_text(s, "Conjuntos", 0.55, 1.42, 3.4, 0.4, size=15, color=SKY, bold=True)
divider(s, 0.55, 1.88, 3.4, color=SKY)

sets_data = [
    ("I", "Cajas disponibles en inventario  i = 1...n"),
    ("J", "Compartimientos del avión  j = 1...m"),
    ("Pares", "Pares únicos (i,k) con i < k para no traslape — elimina redundancia simétrica"),
]
cy = 2.05
for name, desc in sets_data:
    bw = 0.9 if name == "Pares" else 0.6
    rect(s, 0.55, cy, bw, 0.42, BLUE_MID)
    add_text(s, name, 0.55, cy+0.01, bw, 0.4, size=13, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
    add_text(s, desc, 0.55 + bw + 0.1, cy+0.03, 3.4 - bw, 0.7, size=11, color=OFFWHITE)
    cy += 0.88

# Col 2: Parámetros
card(s, 4.4, 1.3, 4.15, 5.6, fill=CARD_BG)
add_text(s, "Parámetros", 4.6, 1.42, 3.75, 0.4, size=15, color=SKY, bold=True)
divider(s, 4.6, 1.88, 3.75, color=SKY)

params = [
    ("Cajas:", "dx_i, dy_i, dz_i — Dimensiones (ancho, largo, alto)"),
    ("",       "w_i — Peso de la caja"),
    ("",       "val_i — Valor económico"),
    ("Comp.:", "L_X_j, L_Y_j, L_Z_j — Dimensiones máximas del compartimiento"),
    ("",       "Wmax_j — Capacidad máxima de peso"),
    ("",       "Ycomp_j — Distancia nariz → inicio del compartimiento"),
    ("Global:", "CG_min, CG_max — Rango seguro de Centro de Gravedad"),
    ("",        "M = 50 — Constante Big-M"),
]
cy = 2.05
for cat, desc in params:
    if cat:
        add_text(s, cat, 4.6, cy, 0.85, 0.3, size=10, color=GOLD, bold=True)
    add_text(s, desc, 4.6, cy + 0.28, 3.75, 0.35, size=10.5, color=OFFWHITE)
    cy += 0.63

# Col 3: Variables
card(s, 8.8, 1.3, 4.2, 5.6, fill=CARD_BG)
add_text(s, "Variables de Decisión", 9.0, 1.42, 3.8, 0.4, size=15, color=SKY, bold=True)
divider(s, 9.0, 1.88, 3.8, color=SKY)

vars_data = [
    (NAVY, "Binaria Principal", "V[i,j] ∈ {0,1}", "1 si caja i está en compartimiento j"),
    (RGBColor(0x4C,0x1D,0x95), "Direccionales", "left, right, front,\nback, below, above\n∈ {0,1}", "Garantizan no traslape entre par (i,k)"),
    (GREEN_OK, "Coordenadas", "x_i, y_i, z_i ≥ 0", "Posición exacta de la esquina inferior-izq de la caja"),
    (RGBColor(0xDC,0x26,0x26), "Balance", "Y_abs_i ≥ 0", "Brazo de palanca longitudinal absoluto desde la nariz"),
]
cy = 2.05
for col, vtype, formula, desc in vars_data:
    rect(s, 9.0, cy, 3.7, 1.15, CARD_ALT)
    add_text(s, vtype, 9.1, cy+0.03, 3.4, 0.3, size=11, color=col, bold=True)
    add_text(s, formula, 9.1, cy+0.32, 3.4, 0.38, size=11, color=WHITE, bold=True)
    add_text(s, desc, 9.1, cy+0.72, 3.4, 0.38, size=10, color=MID_GRAY)
    cy += 1.32

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 5 — FUNCIÓN OBJETIVO Y GRAVEDAD ARTIFICIAL
# ══════════════════════════════════════════════════════════════════════════════
s = blank_slide()
bg(s, NAVY)

rect(s, 0, 0, W, 1.15, HEADER_BG)
add_text(s, "Función Objetivo", 0.5, 0.15, 9, 0.85, size=34, color=WHITE, bold=True, font="Cambria")
add_text(s, "Maximización económica + gravedad artificial", 8.5, 0.35, 4.5, 0.5, size=12, color=SKY, italic=True, align=PP_ALIGN.RIGHT)

# Formula box
card(s, 0.5, 1.3, 12.3, 1.25, fill=RGBColor(0x06, 0x1A, 0x40))
add_text(s, "Max Z  =  Σ Σ (val_i · V_ij)  −  λ · Σ (x_i + y_i + z_i)",
         0.8, 1.38, 11.8, 0.8, size=22, color=WHITE, bold=True,
         align=PP_ALIGN.CENTER, font="Cambria")
add_text(s, "donde  λ = 0.001",
         0.8, 2.1, 11.8, 0.35, size=14, color=GOLD, italic=True, align=PP_ALIGN.CENTER)

# Two component columns
card(s, 0.4, 2.7, 5.9, 3.85, fill=RGBColor(0x0D, 0x22, 0x45))
add_text(s, "① Maximización Económica", 0.65, 2.82, 5.4, 0.42, size=15, color=SKY, bold=True)
add_text(s, "Σ Σ (val_i · V_ij)",
         0.65, 3.3, 5.4, 0.5, size=16, color=GOLD, bold=True, font="Cambria")
add_text(s,
    "El solver activa V_ij = 1 para las cajas con mayor valor económico. "
    "Corresponde a la lógica clásica del Knapsack Problem: seleccionar el subconjunto "
    "de ítems que maximiza la ganancia bajo restricciones de capacidad.",
    0.65, 3.85, 5.4, 1.5, size=12, color=RGBColor(0xCB,0xD5,0xE1))
add_text(s, "Prioridad: ALTA — decisiones económicas", 0.65, 5.35, 5.4, 0.35, size=11, color=GREEN_OK, bold=True)
add_text(s, "La ganancia de cualquier caja siempre supera su penalización de posición → λ garantiza que el sistema jamás sacrifique valor por posición.", 0.65, 5.7, 5.4, 0.62, size=10.5, color=MID_GRAY, italic=True)

card(s, 6.9, 2.7, 5.9, 3.85, fill=RGBColor(0x0D, 0x22, 0x45))
add_text(s, "② Gravedad Artificial", 7.15, 2.82, 5.4, 0.42, size=15, color=RGBColor(0xF0,0x8C,0x00), bold=True)
add_text(s, "−  0.001 · Σ (x_i + y_i + z_i)",
         7.15, 3.3, 5.4, 0.5, size=16, color=GOLD, bold=True, font="Cambria")
add_text(s,
    "Sin esta penalización, un solver algebraico no tiene físicas: las cajas 'flotarían' "
    "en el centro del compartimiento o pegadas al techo. Esto genera múltiples óptimos "
    "degenerados inviables en la realidad operativa.",
    7.15, 3.85, 5.4, 1.5, size=12, color=RGBColor(0xCB,0xD5,0xE1))
add_text(s, "Prioridad: BAJA — solo desempata posiciones", 7.15, 5.35, 5.4, 0.35, size=11, color=GOLD, bold=True)
add_text(s, "Efecto: compacta automáticamente la carga hacia el suelo (z=0), pared frontal (y=0) y lateral (x=0).", 7.15, 5.7, 5.4, 0.62, size=10.5, color=MID_GRAY, italic=True)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 6 — RESTRICCIONES CRÍTICAS
# ══════════════════════════════════════════════════════════════════════════════
s = blank_slide()
bg(s, NAVY_ALT)

rect(s, 0, 0, W, 1.15, HEADER_BG)
add_text(s, "Restricciones del Modelo", 0.5, 0.15, 9, 0.85, size=34, color=WHITE, bold=True, font="Cambria")
add_text(s, "Cuatro grupos de restricciones que garantizan una solución físicamente viable",
         0.5, 6.9, 12.3, 0.5, size=11, color=MID_GRAY, italic=True, align=PP_ALIGN.CENTER)

constraints = [
    (
        "A",
        "Unicidad y Capacidad de Peso",
        "Cada caja puede ir en máximo un compartimiento (o quedarse en tierra). El peso total asignado al compartimiento j no puede superar su límite estructural Wmax_j.",
        "Σ V_ij ≤ 1   ∀i\nΣ w_i · V_ij ≤ Wmax_j   ∀j",
        RGBColor(0x3B,0x82,0xF6), CARD_BG
    ),
    (
        "B",
        "Contención Geométrica (Big-M)",
        "Las dimensiones de una caja más su posición no pueden superar el tamaño del compartimiento. Solo activa si V_ij = 1; si V_ij = 0, la restricción se 'desactiva' sumando M.",
        "x_i + dx_i ≤ L_X_j + M(1−V_ij)\ny_i + dy_i ≤ L_Y_j + M(1−V_ij)\nz_i + dz_i ≤ L_Z_j + M(1−V_ij)",
        RGBColor(0x14,0xB8,0xA6), CARD_BG
    ),
    (
        "C",
        "No Traslape (Restricción Disyuntiva)",
        "Para cualquier par (i,k) en el mismo compartimiento, al menos una relación espacial exclusiva debe cumplirse: izquierda, derecha, frente, atrás, debajo, encima.",
        "left + right + front + back\n  + below + above ≥ V_ij + V_kj − 1",
        PURPLE, CARD_BG
    ),
    (
        "D",
        "Balance Estático (Centro de Gravedad)",
        "El momento estático longitudinal (suma de peso × brazo de palanca) debe estar dentro del rango CG_min–CG_max definido por el fabricante. Se linealiza multiplicando en cruz.",
        "Σ w_i·Y_abs_i ≥ CG_min · Σ Σ w_i·V_ij\nΣ w_i·Y_abs_i ≤ CG_max · Σ Σ w_i·V_ij",
        RED_ERR, CARD_BG
    ),
]

cx, cy = 0.35, 1.3
for i, (letter, title, desc, formula, col, bg_col) in enumerate(constraints):
    w = 6.1 if i % 2 == 0 else 6.1
    x = 0.35 if i % 2 == 0 else 6.9
    y = 1.3 if i < 2 else 4.1

    card(s, x, y, 6.1, 2.65, fill=bg_col)

    # Letter badge
    rect(s, x+0.1, y+0.12, 0.5, 0.5, col)
    add_text(s, letter, x+0.1, y+0.12, 0.5, 0.5, size=16, color=WHITE, bold=True, align=PP_ALIGN.CENTER)

    add_text(s, title, x+0.72, y+0.15, 5.2, 0.42, size=14, color=col, bold=True)
    add_text(s, desc, x+0.15, y+0.7, 5.7, 1.0, size=11, color=OFFWHITE)
    add_text(s, formula, x+0.15, y+1.78, 5.7, 0.78, size=10.5, color=col, bold=True, font="Courier New")

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 7 — CENTRO DE GRAVEDAD Y SEGURIDAD DE VUELO
# ══════════════════════════════════════════════════════════════════════════════
s = blank_slide()
bg(s, NAVY)

rect(s, 0, 0, W, 1.15, HEADER_BG)
add_text(s, "Centro de Gravedad", 0.5, 0.15, 9, 0.85, size=34, color=WHITE, bold=True, font="Cambria")
add_text(s, "Condición crítica de aeronavegabilidad", 8.5, 0.35, 4.5, 0.5, size=12, color=SKY, italic=True, align=PP_ALIGN.RIGHT)

# CG meter visualization
# Fuselage bar
rect(s, 1.0, 2.5, 11.2, 0.55, RGBColor(0x1E, 0x3A, 0x5F))
# CG zone (green)
rect(s, 5.0, 2.3, 3.5, 0.95, RGBColor(0x05, 0x96, 0x69))
add_text(s, "ZONA SEGURA", 5.0, 2.33, 3.5, 0.35, size=10, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
# CG indicator (arrow) — placed in safe zone
rect(s, 6.55, 1.95, 0.12, 1.3, GOLD)
add_text(s, "▼", 6.43, 1.68, 0.36, 0.4, size=16, color=GOLD, bold=True, align=PP_ALIGN.CENTER)
add_text(s, "CG", 6.35, 1.38, 0.55, 0.3, size=11, color=GOLD, bold=True, align=PP_ALIGN.CENTER)

# Labels
add_text(s, "NARIZ", 0.8, 3.15, 1.2, 0.3, size=11, color=MID_GRAY, align=PP_ALIGN.CENTER)
add_text(s, "COLA", 11.2, 3.15, 1.0, 0.3, size=11, color=MID_GRAY, align=PP_ALIGN.CENTER)
add_text(s, "CG_min", 4.75, 3.15, 1.0, 0.3, size=10, color=GREEN_OK)
add_text(s, "CG_max", 8.25, 3.15, 1.0, 0.3, size=10, color=GREEN_OK)

# Two danger cases
# Left: nose heavy
card(s, 0.35, 3.7, 5.9, 2.85, fill=RGBColor(0x2A, 0x0A, 0x0A))
add_text(s, "⚠  CG Adelantado  (< CG_min)", 0.55, 3.8, 5.5, 0.42, size=14, color=RED_ERR, bold=True)
add_text(s, "Avión pesado de nariz:", 0.55, 4.27, 5.3, 0.3, size=12, color=WHITE, bold=True)
add_text(s,
    "→ Los elevadores generan fuerza descendente masiva\n"
    "→ Mayor resistencia aerodinámica y consumo de combustible\n"
    "→ Riesgo: sin autoridad de cabeceo para rotar en el despegue",
    0.55, 4.6, 5.3, 1.4, size=11.5, color=RGBColor(0xFF,0xC5,0xC5))

# Right: tail heavy
card(s, 6.9, 3.7, 5.9, 2.85, fill=RGBColor(0x2A, 0x0A, 0x0A))
add_text(s, "⚠  CG Atrasado  (> CG_max)", 7.1, 3.8, 5.5, 0.42, size=14, color=RED_ERR, bold=True)
add_text(s, "Avión pesado de cola:", 7.1, 4.27, 5.3, 0.3, size=12, color=WHITE, bold=True)
add_text(s,
    "→ Estabilidad longitudinal estática reducida drásticamente\n"
    "→ Tendencia peligrosa al encabritamiento descontrolado\n"
    "→ Riesgo: entrada en pérdida (stall) irrecuperable",
    7.1, 4.6, 5.3, 1.4, size=11.5, color=RGBColor(0xFF,0xC5,0xC5))

# Bottom: how the model linearizes
card(s, 0.35, 6.65, 12.5, 0.68, fill=RGBColor(0x0D, 0x22, 0x45))
add_text(s,
    "Linealización: En lugar de calcular CG = Σ(w·Y_abs) / Σ(w·V) — que introduce no-linealidad por división — se multiplica en cruz, "
    "manteniendo el modelo estrictamente lineal para CPLEX.",
    0.55, 6.72, 12.0, 0.52, size=11.5, color=RGBColor(0xCB,0xD5,0xE1))

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 8 — ARQUITECTURA DEL SISTEMA
# ══════════════════════════════════════════════════════════════════════════════
s = blank_slide()
bg(s, NAVY_ALT)

rect(s, 0, 0, W, 1.15, HEADER_BG)
add_text(s, "Arquitectura del Sistema", 0.5, 0.15, 9, 0.85, size=34, color=WHITE, bold=True, font="Cambria")
add_text(s, "Backend desacoplado + Frontend interactivo 3D", 8.0, 0.35, 5.0, 0.5, size=12, color=SKY, italic=True, align=PP_ALIGN.RIGHT)

# Three layer pipeline
layers = [
    (
        "1",
        "Ingesta de Datos",
        "CSV → Pandas",
        [
            "inventario_de_cajas.csv",
            "base_de_aviones.csv",
            "Filtrado, validación y mapeo",
            "Conversión a diccionarios Pyomo",
        ],
        BLUE_MID, CARD_BG
    ),
    (
        "2",
        "Optimización Backend",
        "Pyomo + CPLEX",
        [
            "pyo.ConcreteModel()",
            "Conjuntos, parámetros, variables",
            "Restricciones MILP + Big-M",
            "Solver: cplex_direct (120s limit)",
        ],
        GREEN_OK, CARD_BG
    ),
    (
        "3",
        "Visualización Frontend",
        "JSON → Three.js / WebGL",
        [
            "resultado_optimizacion.json",
            "Renderizado 3D de compartimientos",
            "Cajas en posición exacta (x,y,z)",
            "Área de carga rechazada en pista",
        ],
        PURPLE, CARD_BG
    ),
]

bx = 0.4
for layer in layers:
    num, title, subtitle, items, col, bg_col = layer
    card(s, bx, 1.3, 3.95, 5.5, fill=bg_col)

    # Number badge
    rect(s, bx+0.15, 1.45, 0.65, 0.65, col)
    add_text(s, num, bx+0.15, 1.45, 0.65, 0.65, size=22, color=WHITE, bold=True, align=PP_ALIGN.CENTER)

    add_text(s, title, bx+0.95, 1.52, 2.85, 0.42, size=15, color=col, bold=True)
    add_text(s, subtitle, bx+0.95, 1.98, 2.85, 0.38, size=12, color=MID_GRAY, italic=True)
    divider(s, bx+0.2, 2.48, 3.55, color=col)

    cy_i = 2.65
    for item in items:
        add_text(s, "→  " + item, bx+0.2, cy_i, 3.55, 0.38, size=12, color=OFFWHITE)
        cy_i += 0.44

    bx += 4.35

# Arrow connectors
for ax in [4.35, 8.7]:
    rect(s, ax, 3.9, 0.35, 0.12, SKY)  # horizontal arrow body
    add_text(s, "▶", ax+0.2, 3.75, 0.4, 0.4, size=18, color=SKY, bold=True, align=PP_ALIGN.CENTER)

# JSON contract detail
card(s, 0.35, 7.0, 12.5, 0.65, fill=GLASS)
add_text(s,
    "Contrato de API: resultado_optimizacion.json — incluye geometría de compartimientos, "
    "coordenadas (x,y,z) de cajas cargadas y lista de carga rechazada para renderizado correcto.",
    0.55, 7.08, 12.0, 0.48, size=12, color=OFFWHITE)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 9 — CASO 1: FALLO GEOMÉTRICO
# ══════════════════════════════════════════════════════════════════════════════
s = blank_slide()
bg(s, NAVY)

rect(s, 0, 0, W, 1.15, HEADER_BG)
add_text(s, "Caso de Estudio 1", 0.5, 0.15, 7, 0.85, size=34, color=WHITE, bold=True, font="Cambria")
add_text(s, "Fallo Geométrico Exitoso — AirbusA330", 7.0, 0.35, 6.0, 0.5, size=13, color=SKY, italic=True, align=PP_ALIGN.RIGHT)

# Rejected box panel
card(s, 0.35, 1.3, 4.5, 5.6, fill=RGBColor(0x2A, 0x0A, 0x0A))
add_text(s, "❌  Caja C10 — RECHAZADA", 0.55, 1.42, 4.1, 0.45, size=14, color=RED_ERR, bold=True)
divider(s, 0.55, 1.93, 4.1, color=RED_ERR)

c10_data = [
    ("Peso", "1,200 kg"),
    ("Valor", "$3,000 USD  ← MÁXIMO del inventario"),
    ("Dimensión dx", "4.0 m"),
    ("L_X del avión", "3.5 m  ← INFERIOR al ancho de la caja"),
]
cy = 2.1
for label, val in c10_data:
    add_text(s, label + ":", 0.55, cy, 1.8, 0.32, size=11, color=MID_GRAY)
    add_text(s, val, 2.45, cy, 2.25, 0.32, size=11, color=WHITE, bold=True)
    cy += 0.5

# Warning visual
rect(s, 0.55, 4.35, 4.0, 1.4, RGBColor(0x3A, 0x0E, 0x0E))
add_text(s, "4.0 m", 0.7, 4.48, 1.5, 0.35, size=13, color=RED_ERR, bold=True)
add_text(s, "dx caja", 0.7, 4.85, 1.5, 0.3, size=10, color=MID_GRAY)
add_text(s, ">", 2.3, 4.6, 0.4, 0.55, size=24, color=RED_ERR, bold=True, align=PP_ALIGN.CENTER)
add_text(s, "3.5 m", 2.75, 4.48, 1.5, 0.35, size=13, color=GREEN_OK, bold=True)
add_text(s, "L_X avión", 2.75, 4.85, 1.5, 0.3, size=10, color=MID_GRAY)
add_text(s, "Restricción de contención detectada antes de asignación", 0.55, 5.4, 4.0, 0.4, size=10.5, color=RED_ERR, italic=True)

# Results panel
card(s, 5.1, 1.3, 7.9, 5.6, fill=RGBColor(0x0D, 0x22, 0x45))
add_text(s, "Resultado de la Optimización", 5.35, 1.42, 7.4, 0.45, size=15, color=SKY, bold=True)

# Stat callouts
stats2 = [
    ("$10,249.98", "Ganancia neta optimizada"),
    ("15.00", "Centro de Gravedad final\n(límite superior AirbusA330)"),
    ("12 / 13", "Cajas admitidas vs inventario total"),
]
sy2 = 2.0
for val, label in stats2:
    rect(s, 5.35, sy2, 7.45, 1.1, RGBColor(0x06, 0x1A, 0x40))
    add_text(s, val, 5.5, sy2+0.05, 7.0, 0.58, size=26, color=GOLD, bold=True, font="Cambria")
    add_text(s, label, 5.5, sy2+0.62, 7.0, 0.42, size=11, color=RGBColor(0xCB,0xD5,0xE1))
    sy2 += 1.3

divider(s, 5.35, 5.95, 7.45, color=SKY)
add_text(s,
    "La caja con mayor valor económico fue excluida porque su ancho físico (4.0 m) "
    "supera la apertura del compartimiento (3.5 m). El solver lo detectó mediante la "
    "restricción de contención geométrica — sin necesitar intervención humana.",
    5.35, 6.12, 7.45, 0.9, size=11.5, color=RGBColor(0xCB,0xD5,0xE1), italic=True)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 10 — CASO 2: BALANCE ESTÁTICO / CG
# ══════════════════════════════════════════════════════════════════════════════
s = blank_slide()
bg(s, NAVY_ALT)

rect(s, 0, 0, W, 1.15, HEADER_BG)
add_text(s, "Caso de Estudio 2", 0.5, 0.15, 7, 0.85, size=34, color=WHITE, bold=True, font="Cambria")
add_text(s, "Estrés de Balance Estático — Boeing 747", 7.0, 0.35, 6.0, 0.5, size=13, color=SKY, italic=True, align=PP_ALIGN.RIGHT)

# Setup
card(s, 0.35, 1.3, 6.0, 2.6, fill=CARD_BG)
add_text(s, "Configuración del Escenario", 0.55, 1.42, 5.5, 0.4, size=14, color=SKY, bold=True)
divider(s, 0.55, 1.88, 5.5, color=SKY)
add_text(s,
    "Boeing 747  |  CG_min = 10.0  |  CG_max = 18.0\n\n"
    "Cajas críticas introducidas:\n"
    "  C6: 800 kg  (Ycomp_Frontal = 4.0)\n"
    "  C8: 400 kg  (Ycomp_Frontal = 4.0)",
    0.55, 2.0, 5.5, 1.75, size=12, color=OFFWHITE)

# Problem
card(s, 0.35, 4.05, 6.0, 2.5, fill=RGBColor(0x2A, 0x0A, 0x0A))
add_text(s, "Heurística First-Fit (sin MILP):", 0.55, 4.17, 5.5, 0.38, size=13, color=RED_ERR, bold=True)
add_text(s,
    "Habría llenado el compartimiento Frontal (Ycomp = 4.0) con C6 y C8, "
    "generando un Y_abs promedio de ~4.3 → muy por debajo de CG_min = 10.0.\n\n"
    "Resultado: avión peligrosamente pesado de nariz. ❌",
    0.55, 4.6, 5.5, 1.75, size=12, color=RED_ERR)

# Solution
card(s, 6.75, 1.3, 6.15, 5.25, fill=CARD_BG)
add_text(s, "Solución MILP:", 6.95, 1.42, 5.75, 0.38, size=14, color=GREEN_OK, bold=True)
divider(s, 6.95, 1.88, 5.75, color=GREEN_OK)
add_text(s,
    "El modelo distribuyó estratégicamente las cargas hacia el "
    "compartimiento Trasero (Ycomp = 14.0), compensando el brazo de palanca.",
    6.95, 2.0, 5.75, 0.95, size=12, color=OFFWHITE)

# Visual balance bar
add_text(s, "Momento Estático Resultante:", 6.95, 3.05, 5.75, 0.35, size=12, color=WHITE, bold=True)

rect(s, 6.95, 3.48, 5.6, 0.38, RGBColor(0x1E, 0x29, 0x3B))
rect(s, 6.95, 3.48, 3.7, 0.38, GREEN_OK)
add_text(s, "CG final: 14.2", 6.95, 3.52, 3.6, 0.28, size=11, color=WHITE, bold=True, align=PP_ALIGN.CENTER)

add_text(s, "Nariz (10.0)", 6.95, 3.95, 2.2, 0.3, size=10, color=MID_GRAY)
add_text(s, "Cola (18.0)", 10.3, 3.95, 2.3, 0.3, size=10, color=MID_GRAY, align=PP_ALIGN.RIGHT)

add_text(s, "✓  CG = 14.2 está dentro del rango [10.0 — 18.0]", 6.95, 4.35, 5.75, 0.4, size=13, color=GREEN_OK, bold=True)
add_text(s,
    "El solver reposicionó las cargas pesadas al compartimiento trasero para "
    "elevar el brazo de palanca promedio, manteniendo la aeronave en equilibrio seguro y operable.",
    6.95, 4.85, 5.75, 1.0, size=12, color=MID_GRAY, italic=True)
add_text(s, "✈ Aeronave lista para despegue", 6.95, 5.95, 5.75, 0.4, size=13, color=GREEN_OK, bold=True)

# Bottom insight
add_text(s,
    "Este caso demuestra que la restricción de CG no es solo un 'chequeo de validación': "
    "es un motor activo de reposicionamiento de carga que ninguna heurística tradicional puede garantizar.",
    0.35, 6.65, 12.5, 0.68, size=12, color=MID_GRAY, italic=True)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 11 — CASO 3: ALTA DENSIDAD DE VALOR
# ══════════════════════════════════════════════════════════════════════════════
s = blank_slide()
bg(s, NAVY)

rect(s, 0, 0, W, 1.15, HEADER_BG)
add_text(s, "Caso de Estudio 3", 0.5, 0.15, 7, 0.85, size=34, color=WHITE, bold=True, font="Cambria")
add_text(s, "Alta Densidad de Valor — 3D BPP + Knapsack", 7.0, 0.35, 6.0, 0.5, size=13, color=SKY, italic=True, align=PP_ALIGN.RIGHT)

# Inventory table
card(s, 0.35, 1.3, 7.0, 4.6, fill=RGBColor(0x0D, 0x22, 0x45))
add_text(s, "Inventario del Escenario", 0.55, 1.42, 6.6, 0.4, size=14, color=SKY, bold=True)
divider(s, 0.55, 1.88, 6.6, color=SKY)

# Table header
headers = ["Caja", "Dimensiones (m)", "Valor ($)", "Densidad val/vol", "Decisión"]
hx = 0.55
for j, h in enumerate(headers):
    widths = [0.7, 2.0, 1.0, 1.5, 1.0]
    add_text(s, h, hx, 2.05, widths[j], 0.32, size=10, color=MID_GRAY, bold=True)
    hx += widths[j] + 0.05

rows = [
    ("C4", "3.0 × 2.0 × 2.0", "$150", "~6.25", "❌ Excluida", RED_ERR),
    ("C3", "0.5 × 0.5 × 0.5", "$1,200", "~19,200", "✓ Cargada", GREEN_OK),
    ("C11","0.6 × 0.6 × 0.5", "$2,000", "~22,222", "✓ Cargada", GREEN_OK),
]
cy = 2.45
for row in rows:
    caja, dims, val, density, decision, dcol = row
    vals_row = [caja, dims, val, density, decision]
    rx = 0.55
    for j, v in enumerate(vals_row):
        widths = [0.7, 2.0, 1.0, 1.5, 1.0]
        col = dcol if j == 4 else (GOLD if j == 2 else WHITE)
        add_text(s, v, rx, cy, widths[j], 0.38, size=11, color=col, bold=(j==4))
        rx += widths[j] + 0.05
    cy += 0.52

add_text(s,
    "Densidad = valor / volumen. El solver optimizó la densidad de carga, "
    "priorizando cajas pequeñas de alto valor sobre cajas voluminosas baratas.",
    0.55, 3.82, 6.6, 0.75, size=11.5, color=RGBColor(0xCB,0xD5,0xE1), italic=True)

add_text(s, "Efecto de la gravedad artificial:", 0.55, 4.65, 6.6, 0.35, size=12, color=GOLD, bold=True)
add_text(s,
    "C3 y C11 fueron ancladas algorítmicamente en las esquinas inferiores "
    "(x=0, y=0, z=0), liberando volumen útil para el resto del inventario.",
    0.55, 5.02, 6.6, 0.72, size=11.5, color=RGBColor(0xCB,0xD5,0xE1))

# Visual: box packing diagram (abstract)
card(s, 7.6, 1.3, 5.4, 4.6, fill=RGBColor(0x06, 0x1A, 0x40))
add_text(s, "Comportamiento de Compactación", 7.8, 1.42, 5.0, 0.4, size=13, color=SKY, bold=True)

# Compartimento outline
rect(s, 7.8, 2.0, 4.8, 2.8, RGBColor(0x1E, 0x3A, 0x5F))

# C3 (small, high value, anchored corner)
rect(s, 7.85, 4.15, 0.55, 0.5, GREEN_OK)
add_text(s, "C3", 7.85, 4.18, 0.55, 0.35, size=8, color=WHITE, bold=True, align=PP_ALIGN.CENTER)

# C11 (small, high value, next to C3)
rect(s, 8.48, 4.05, 0.65, 0.58, RGBColor(0x00, 0x87, 0xAB))
add_text(s, "C11", 8.48, 4.1, 0.65, 0.38, size=8, color=WHITE, bold=True, align=PP_ALIGN.CENTER)

# Large C4 (excluded - shown outside)
rect(s, 10.8, 3.5, 1.8, 1.2, RGBColor(0x3A, 0x0E, 0x0E))
add_text(s, "C4", 10.8, 3.62, 1.8, 0.35, size=11, color=RED_ERR, bold=True, align=PP_ALIGN.CENTER)
add_text(s, "Vol grande\nbajo valor", 10.8, 3.98, 1.8, 0.55, size=9, color=MID_GRAY, align=PP_ALIGN.CENTER)

# Arrow
add_text(s, "→  excluida", 10.0, 3.85, 0.75, 0.35, size=9, color=RED_ERR)

add_text(s, "↙ Ancladas en esquina inferior\n   por gravedad artificial", 7.8, 4.72, 4.8, 0.6, size=10, color=GOLD, italic=True)

# Key insight
card(s, 0.35, 6.15, 12.5, 0.9, fill=RGBColor(0x0D, 0x22, 0x45))
add_text(s, "Insight clave:", 0.55, 6.25, 1.6, 0.3, size=12, color=GOLD, bold=True)
add_text(s,
    "El modelo combina la lógica del Knapsack (selección por densidad de valor) con la del 3D BPP (posición compacta), "
    "resultando en una solución que ninguno de los dos enfoques por separado podría alcanzar.",
    2.2, 6.25, 10.4, 0.62, size=12, color=RGBColor(0xCB,0xD5,0xE1))

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 12 — EXPLOITS MITIGADOS
# ══════════════════════════════════════════════════════════════════════════════
s = blank_slide()
bg(s, NAVY_ALT)

rect(s, 0, 0, W, 1.15, HEADER_BG)
add_text(s, "Exploits Matemáticos Mitigados", 0.5, 0.15, 9, 0.85, size=34, color=WHITE, bold=True, font="Cambria")
add_text(s, "Comportamientos indeseados del solver detectados y corregidos",
         0.5, 6.9, 12.3, 0.5, size=11, color=MID_GRAY, italic=True, align=PP_ALIGN.CENTER)

# Bug 1
card(s, 0.35, 1.3, 6.0, 4.85, fill=CARD_BG)
rect(s, 0.35, 1.3, 6.0, 0.52, RED_ERR)
add_text(s, "Bug 1  —  Error de Tolerancia de Variables Continuas", 0.55, 1.36, 5.6, 0.38, size=12, color=WHITE, bold=True)

add_text(s, "Descripción del problema:", 0.55, 1.95, 5.6, 0.32, size=12, color=WHITE, bold=True)
add_text(s,
    "Con M = 100,000, CPLEX explotaba la tolerancia numérica fraccional del solver "
    "permitiendo un traslape infinitesimal (ε ≈ 0.0001 m) entre cajas. "
    "En la práctica, esto corrompía silenciosamente la geometría 3D.",
    0.55, 2.3, 5.6, 1.0, size=12, color=OFFWHITE)

add_text(s, "Diagnóstico:", 0.55, 3.38, 5.6, 0.32, size=12, color=RED_ERR, bold=True)
add_text(s, "M demasiado grande → las restricciones Big-M se vuelven numéricamente 'flojas'", 0.55, 3.72, 5.6, 0.4, size=12, color=OFFWHITE)

add_text(s, "Corrección aplicada:", 0.55, 4.2, 5.6, 0.32, size=12, color=GREEN_OK, bold=True)
add_text(s, "M = 100,000  →  M = 50", 0.55, 4.55, 2.5, 0.5, size=18, color=GREEN_OK, bold=True, font="Courier New")
add_text(s, "Valor calibrado al rango real de las dimensiones del inventario, restaurando la impenetrabilidad geométrica.", 0.55, 5.12, 5.6, 0.55, size=11.5, color=MID_GRAY, italic=True)

# Bug 2
card(s, 6.9, 1.3, 6.0, 4.85, fill=CARD_BG)
rect(s, 6.9, 1.3, 6.0, 0.52, RED_ERR)
add_text(s, "Bug 2  —  Contrapeso Fantasma (Ghost Weight)", 7.1, 1.36, 5.6, 0.38, size=12, color=WHITE, bold=True)

add_text(s, "Descripción del problema:", 7.1, 1.95, 5.6, 0.32, size=12, color=WHITE, bold=True)
add_text(s,
    "Las cajas NO asignadas a ningún compartimiento (cajas en tierra) "
    "mantenían sus variables Y_abs > 0, contribuyendo ilegalmente al cálculo "
    "del momento de equilibrio. El CG calculado era incorrecto.",
    7.1, 2.3, 5.6, 1.0, size=12, color=OFFWHITE)

add_text(s, "Diagnóstico:", 7.1, 3.38, 5.6, 0.32, size=12, color=RED_ERR, bold=True)
add_text(s, "Ausencia de restricción que forzara Y_abs = 0 cuando V_ij = 0 ∀j", 7.1, 3.72, 5.6, 0.4, size=12, color=OFFWHITE)

add_text(s, "Corrección aplicada:", 7.1, 4.2, 5.6, 0.32, size=12, color=GREEN_OK, bold=True)
add_text(s, "Y_abs_i ≤ M · Σ_j V_ij", 7.1, 4.55, 3.5, 0.5, size=16, color=GREEN_OK, bold=True, font="Courier New")
add_text(s, "Restricción explícita: si una caja no está en ningún compartimiento, su brazo de palanca se fuerza a cero.", 7.1, 5.12, 5.6, 0.55, size=11.5, color=MID_GRAY, italic=True)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 13 — CONCLUSIONES
# ══════════════════════════════════════════════════════════════════════════════
s = blank_slide()
bg(s, NAVY)

# Top decorative
rect(s, 0, 0, W, 1.15, HEADER_BG)
add_text(s, "Conclusiones", 0.5, 0.15, 9, 0.85, size=34, color=WHITE, bold=True, font="Cambria")
add_text(s, "Optimización Tridimensional de Carga Aeroportuaria", 7.0, 0.35, 6.0, 0.5, size=12, color=SKY, italic=True, align=PP_ALIGN.RIGHT)

# Five conclusion cards
conclusions = [
    ("Exactitud garantizada", "El enfoque MILP con CPLEX provee soluciones óptimas globales que los algoritmos heurísticos (First-Fit, genéticos) no pueden asegurar, especialmente bajo restricciones físicas acopladas.", GREEN_OK),
    ("Seguridad de vuelo integrada", "La restricción de Centro de Gravedad no es un chequeo posterior — es una variable activa de reposicionamiento que garantiza que cada solución cumple los estándares aeronáuticos.", SKY),
    ("Robustez ante exploits del solver", "La calibración de M=50 y la restricción anti-contrapeso fantasma demuestran que un modelo MILP robusto requiere iteración cuidadosa con el comportamiento real del solver.", GOLD),
    ("Arquitectura escalable", "El desacoplamiento Backend/Frontend permite cambiar de solver, aeronave o inventario sin reescribir la interfaz. El contrato JSON asegura independencia de capas.", RGBColor(0x7C,0x3A,0xED)),
    ("Visualización como validación", "El renderizado 3D no es solo un artefacto visual: permite verificar intuitivamente la no-colisión espacial, el balance y la distribución, cerrando el ciclo de validación del modelo.", RGBColor(0x0D,0x6E,0xFD)),
]

cx_c = 0.35
for i, (title, desc, col) in enumerate(conclusions):
    cw = 2.4
    card(s, cx_c, 1.35, cw, 4.7, fill=RGBColor(0x0D, 0x22, 0x45))
    # Top accent
    rect(s, cx_c, 1.35, cw, 0.32, col)
    add_text(s, str(i+1), cx_c, 1.35, cw, 0.32, size=14, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
    add_text(s, title, cx_c+0.1, 1.75, cw-0.2, 0.55, size=12, color=col, bold=True)
    add_text(s, desc, cx_c+0.1, 2.38, cw-0.2, 3.55, size=11, color=RGBColor(0xCB,0xD5,0xE1))
    cx_c += 2.6

# Final tagline
add_text(s,
    "La plataforma desarrollada es funcional, escalable para distintos tipos de aeronaves y demuestra "
    "que la Investigación de Operaciones aplicada al dominio aeronáutico produce herramientas de decisión robustas y seguras.",
    0.5, 6.2, 12.3, 0.75, size=13, color=MID_GRAY, italic=True, align=PP_ALIGN.CENTER)

add_text(s, "UCB San Pablo — Materia: Optimización — junio 2026",
         0.5, 7.05, 12.3, 0.35, size=10, color=RGBColor(0x44, 0x55, 0x70),
         align=PP_ALIGN.CENTER)

# ─── Save ─────────────────────────────────────────────────────────────────────
OUT = "Optimizacion_Carga_Aeroportuaria.pptx"
prs.save(OUT)
print(f"Saved: {OUT}")