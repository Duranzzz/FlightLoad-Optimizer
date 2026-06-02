# ✈️ FlightLoad Optimizer

**Optimización Tridimensional de Carga Aeroportuaria**

> Proyecto Final — Materia: Optimización · 3er Semestre  
> Universidad Católica Boliviana "San Pablo"  
> Autores: **Leonardo Duran Cuenca** · **Diego Villazón Arce**  
> Docente: Santos Carlos Huayta · Junio 2026

---

## 📋 Descripción

FlightLoad Optimizer resuelve el **problema de empaquetado 3D (3D Bin Packing)** combinado con el **problema de la mochila (Knapsack)**, aplicado a la carga de aeronaves comerciales.

El sistema determina:

- **Qué cajas** viajan y cuáles se quedan en tierra (selección por valor económico).
- **En qué compartimiento** va cada caja (asignación).
- **Las coordenadas exactas** `(x, y, z)` de cada pieza dentro del compartimiento.
- Que la distribución de peso mantenga el **Centro de Gravedad (CG)** dentro del rango seguro del avión.

Todo modelado como un problema de **Programación Lineal Entera Mixta (MILP)**, resuelto con **CPLEX** a través de **Pyomo**, con un frontend 3D interactivo en **Three.js**.

---

## 🧮 Formulación Matemática

### Conjuntos

| Símbolo | Descripción |
|---------|-------------|
| `I` | Cajas disponibles en inventario (`i = 1...n`) |
| `J` | Compartimientos del avión (`j = 1...m`) |
| `Pares` | Pares únicos `(i, k)` con `i < k` — elimina redundancia simétrica |

### Parámetros

| Parámetro | Descripción |
|-----------|-------------|
| `dx_i, dy_i, dz_i` | Dimensiones de la caja `i` (ancho, largo, alto) |
| `w_i` | Peso de la caja `i` |
| `val_i` | Valor económico de la caja `i` |
| `L_X_j, L_Y_j, L_Z_j` | Dimensiones del compartimiento `j` |
| `Wmax_j` | Capacidad máxima de peso del compartimiento `j` |
| `Ycomp_j` | Distancia nariz → inicio del compartimiento `j` |
| `CG_min, CG_max` | Rango seguro de Centro de Gravedad |
| `M` | Constante Big-M (`M = 100`) |

### Variables de Decisión

| Variable | Tipo | Descripción |
|----------|------|-------------|
| `V[i,j]` | Binaria | `1` si la caja `i` se asigna al compartimiento `j` |
| `x_i, y_i, z_i` | Continua ≥ 0 | Posición de la esquina inferior-izquierda de la caja |
| `Y_abs_i` | Continua ≥ 0 | Brazo de palanca longitudinal absoluto desde la nariz |
| `left, right, front, back, below, above` | Binaria | Relaciones espaciales para no-traslape entre pares |

### Función Objetivo

```
Max Z = Σ_i Σ_j (val_i · V_ij) − 0.001 · Σ_i (x_i + y_i + z_i)
```

**Dos componentes:**
1. **Maximización económica:** selecciona el subconjunto de cajas con mayor valor total (lógica Knapsack).
2. **Gravedad artificial** (λ = 0.001): penalización infinitesimal que compacta la carga hacia el suelo y las paredes, eliminando soluciones degeneradas donde las cajas "flotan".

### Restricciones

| Grupo | Restricción | Descripción |
|-------|-------------|-------------|
| **A** | `Σ_j V_ij ≤ 1` | **Unicidad:** cada caja va en máximo un compartimiento |
| **A** | `Σ_i w_i · V_ij ≤ Wmax_j` | **Peso máximo** por compartimiento |
| **B** | `x_i + dx_i ≤ L_X_j + M(1−V_ij)` | **Contención geométrica** (en X, Y, Z) |
| **C** | `left + right + ... + above ≥ V_ij + V_kj − 1` | **No traslape** disyuntivo |
| **D** | `Σ w_i·Y_abs_i ≥ CG_min · Σ w_i·V_ij` | **Balance estático** (CG mínimo) |
| **D** | `Σ w_i·Y_abs_i ≤ CG_max · Σ w_i·V_ij` | **Balance estático** (CG máximo) |
| **D** | `Y_abs_i ≤ M · Σ_j V_ij` | **Anti-contrapeso fantasma** |

> La restricción de CG se linealiza multiplicando en cruz para evitar la división no lineal `CG = Σ(w·Y) / Σ(w·V)`.

---

## 🏗️ Arquitectura

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  1. INGESTA       │     │  2. OPTIMIZACIÓN  │     │  3. VISUALIZACIÓN │
│  CSV → Pandas     │────▶│  Pyomo + CPLEX    │────▶│  JSON → Three.js  │
│                   │     │                   │     │                   │
│  inventario.csv   │     │  ConcreteModel()  │     │  Renderizado 3D   │
│  aviones.csv      │     │  Restricciones    │     │  WebGL interactivo │
│  Validación       │     │  Solver 120s      │     │  Tooltips + Stats  │
└──────────────────┘     └──────────────────┘     └──────────────────┘
```

**Backend** (Python/Jupyter) y **Frontend** (HTML/CSS/JS) están completamente desacoplados mediante un contrato JSON.

---

## 📁 Estructura del Proyecto

```
FlightLoad-Optimizer/
│
├── FlightLoad.ipynb              # Notebook principal (backend)
│
├── sources/                      # Datos de entrada (CSV)
│   ├── base_de_aviones.csv       # Flota: Boeing747, AirbusA330, HerculesC130, CessnaCaravan
│   ├── inventario_de_cajas1.csv  # Inventario de prueba 1 (13 cajas)
│   ├── inventario_de_cajas2.csv  # Inventario de prueba 2 (13 cajas)
│   └── inventario_de_cajas3.csv  # Inventario reducido (3 cajas)
│
├── interface/                    # Frontend 3D
│   ├── index.html                # Dashboard principal
│   ├── styles.css                # Estilos (dark theme, glassmorphism)
│   ├── app.js                    # Motor Three.js (fuselaje, compartimientos, cajas)
│   └── resultado_optimizacion.json  # Salida del backend (generado automáticamente)
│
├── docs/                         # Documentación académica
│   ├── FinalProjectOptimization.pdf   # Informe técnico (paper)
│   ├── FinalProjectOptimization.docx  # Fuente del informe
│   ├── Optimizacion_Carga_Aeroportuaria.pptx  # Presentación de diapositivas
│   ├── Presentación.py           # Script generador del PPTX (python-pptx)
│   ├── FlightLoad.ipynb.txt      # Copia plana del notebook
│   └── Rubrica.txt               # Rúbrica de evaluación
│
├── requirements.txt              # Dependencias Python (pip install -r requirements.txt)
├── iniciar.bat                   # ⚡ Setup automático (doble clic para ejecutar)
├── .gitignore
└── README.md                     # Este archivo
```

---

## ⚙️ Instalación Rápida

### ⚡ Opción 1 — Un solo clic (Windows)

Hacer **doble clic** en `iniciar.bat`. El script:
1. Verifica que Python esté instalado
2. Instala todas las dependencias automáticamente
3. Levanta el servidor HTTP en `http://localhost:8080`

### 🔧 Opción 2 — Manual

```bash
# 1. Clonar el repositorio
git clone https://github.com/Duranzzz/FlightLoad-Optimizer.git
cd FlightLoad-Optimizer

# 2. Instalar dependencias de Python
pip install -r requirements.txt

# 3. Ejecutar el notebook (backend)
jupyter notebook FlightLoad.ipynb

# 4. Levantar el frontend 3D
cd interface
python -m http.server 8080
# Abrir http://localhost:8080 en el navegador
```

---

## ⚙️ Requisitos

### Backend (Optimización)

| Dependencia | Versión | Propósito |
|-------------|---------|-----------|
| Python | ≥ 3.10 | Runtime |
| Pandas | ≥ 2.0 | Lectura de CSV y preparación de datos |
| Pyomo | ≥ 6.7 | Modelado algebraico MILP |
| CPLEX | ≥ 22.1 | Solver de optimización (IBM) |
| Jupyter | — | Ejecución del notebook |

Todas las dependencias están listadas en [`requirements.txt`](requirements.txt):

```bash
pip install -r requirements.txt
```

> ⚠️ **CPLEX** requiere una licencia de IBM. Versiones académicas disponibles en [IBM Academic Initiative](https://www.ibm.com/academic).

### Frontend (Visualización)

- Navegador web moderno (Edge, Firefox, Chrome, etc.)
- [Three.js r128+](https://threejs.org/) — cargado vía CDN, no requiere instalación.
- Servidor HTTP local para evitar restricciones CORS con `fetch()`.

---

## 🚀 Uso

### Paso 1 — Ejecutar la Optimización

Abrir `FlightLoad.ipynb` en Jupyter y ejecutar la celda. Por defecto resuelve para el **AirbusA330**:

```python
cajas, valor = optimizar_carga_avion(
    'sources/inventario_de_cajas1.csv',
    'sources/base_de_aviones.csv',
    'AirbusA330'
)
```

**Aviones disponibles:**

| Avión | Compartimientos | CG Rango | Notas |
|-------|----------------|----------|-------|
| `Boeing747` | Frontal, Trasero | 10.0 – 18.0 | 2 bodegas, alta capacidad |
| `AirbusA330` | Frontal, Central, Trasero | 8.0 – 15.0 | 3 bodegas |
| `HerculesC130` | BodegaUnica | 5.0 – 12.0 | Bodega única, 15 ton |
| `CessnaCaravan` | Principal | 1.0 – 3.0 | Avión pequeño, 500 kg |

La función genera automáticamente `interface/resultado_optimizacion.json`.

### Paso 2 — Visualizar en 3D

Iniciar un servidor HTTP local en la carpeta `interface/`:

```bash
cd interface
python -m http.server 8080
```

Abrir `http://localhost:8080` en el navegador.

### Controles del Visor 3D

| Acción | Control |
|--------|---------|
| Rotar la cámara | 🖱️ Clic + Arrastrar |
| Zoom | 🔍 Scroll del mouse |
| Mover la vista | ⇧ Shift + Arrastrar |
| Inspeccionar caja | Hover sobre cualquier caja |
| Ocultar sidebar | Clic en el botón `‹` del borde izquierdo |

---

## 📄 Contrato JSON

El archivo `resultado_optimizacion.json` es el puente entre backend y frontend:

```json
{
    "avion": "AirbusA330",
    "valor_total_optimizado": 10249.98,
    "compartimientos": [
        {
            "id_comp": "Frontal",
            "L_X": 3.5, "L_Y": 5.0, "L_Z": 2.5,
            "Ycomp": 3.0
        }
    ],
    "cajas_cargadas": [
        {
            "id_caja": "C1",
            "compartimiento": "Central",
            "x": 0.0, "y": 0.0, "z": 1.0,
            "dx": 1, "dy": 1, "dz": 1,
            "peso": 150,
            "valor": 500
        }
    ],
    "cajas_no_cargadas": [
        {
            "id_caja": "C10",
            "dx": 4, "dy": 4, "dz": 2.5,
            "peso": 1200,
            "valor": 3000
        }
    ]
}
```

| Campo | Descripción |
|-------|-------------|
| `avion` | Identificador de la aeronave |
| `valor_total_optimizado` | Ganancia neta (función objetivo) |
| `compartimientos[]` | Geometría de cada bodega + posición longitudinal (`Ycomp`) |
| `cajas_cargadas[]` | Cajas asignadas con posición exacta `(x, y, z)` y compartimiento destino |
| `cajas_no_cargadas[]` | Cajas rechazadas por el solver (sin coordenadas) |

---

## 📊 Casos de Estudio

### Caso 1 — Fallo Geométrico (AirbusA330)

La caja **C10** ($3,000 — la más valiosa del inventario) fue **rechazada** porque su ancho `dx = 4.0 m` excede el ancho máximo del compartimiento `L_X = 3.5 m`. El solver lo detecta automáticamente mediante la restricción de contención geométrica.

**Resultado:** 12/13 cajas cargadas · Ganancia: **$10,249.98**

### Caso 2 — Estrés de Balance (Boeing747)

Cajas pesadas (C6: 800 kg, C8: 400 kg) habrían sido cargadas en el compartimiento Frontal por una heurística First-Fit, generando un CG de ~4.3, muy por debajo del mínimo (10.0). El solver MILP redistribuyó la carga al compartimiento Trasero (`Ycomp = 14.0`).

**Resultado:** CG final = **14.2** (dentro del rango [10.0, 18.0]) ✈️

### Caso 3 — Densidad de Valor

El solver priorizó cajas pequeñas de alto valor (C3: $1,200 en 0.125 m³, C11: $2,000 en 0.18 m³) sobre cajas voluminosas baratas (C4: $150 en 12 m³). Combina lógica Knapsack + 3D BPP.

---

## 🐛 Exploits Mitigados

| Bug | Problema | Solución |
|-----|----------|----------|
| **Tolerancia numérica** | Con `M = 100,000`, CPLEX permitía traslape infinitesimal (ε ≈ 0.0001 m) | Calibrar `M = 100` al rango real de dimensiones |
| **Contrapeso fantasma** | Cajas no asignadas mantenían `Y_abs > 0`, corrompiendo el cálculo de CG | Restricción: `Y_abs_i ≤ M · Σ_j V_ij` |

---

## 🖥️ Características del Frontend

- **Fuselaje procedural** — Generado dinámicamente según dimensiones de compartimientos con `BufferGeometry` elíptica con taper en nariz y cola.
- **Compartimientos wireframe** — Posicionados según `Ycomp` del JSON, centrados automáticamente en el eje transversal.
- **Cajas con raycasting** — Hover interactivo con tooltips mostrando peso, valor, dimensiones y posición.
- **Zona de carga rechazada** — Hangar visual al costado del avión con grid automático y marcas ✕.
- **Sidebar colapsable** — Dashboard con estadísticas, leyenda de colores y lista de cajas (cargadas/rechazadas).
- **Dark theme** — Diseño glassmorphism con paleta índigo/púrpura.

---

## 📜 Licencia

Proyecto académico — Universidad Católica Boliviana "San Pablo", 2026.
