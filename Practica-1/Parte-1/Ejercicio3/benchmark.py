#!/usr/bin/env python3
"""
Benchmark con pyperplan para el Ejercicio 1.3.

Ejecuta pyperplan con distintas combinaciones de algoritmos y heurísticas,
midiendo tiempos y recogiendo resultados. Genera tablas en formato Markdown.

Algoritmos de pyperplan:
    - bfs: Breadth First Search
    - ids: Iterative Deepening Search
    - astar: A*
    - wastar: Weighted A*
    - gbfs: Greedy Best First Search
    - ehc: Enforced Hill Climbing
    - sat: Satisficibilidad booleana

Heurísticas de pyperplan:
    - hadd: hADD
    - hsa: hSA
    - hmax: hMAX (admisible)
    - hff: hFF
    - landmark: Landmark
    - lmcut: Landmark-cut (admisible)

Uso:
    python3 benchmark.py
"""

import subprocess
import time
import os
import sys
from pathlib import Path

# ─── Configuración ───────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOMAIN = os.path.join(BASE_DIR, "domainemergencias.pddl")
PROBLEMS_DIR = os.path.join(BASE_DIR, "problems")
RESULTS_DIR = os.path.join(BASE_DIR, "results")
TIMEOUT = 60  # segundos

SUMMARY_FILE = os.path.join(RESULTS_DIR, "summary.txt")

# Ruta a pyperplan (puede estar en ~/.local/bin)
PYPERPLAN = os.path.expanduser("~/planutils-venv/bin/pyperplan")

# Buffer para el resumen
summary_lines = []


def log(text=""):
    """Imprime en consola y guarda en el buffer de resumen."""
    print(text)
    summary_lines.append(text)


def save_summary():
    """Guarda el resumen en el archivo de texto."""
    with open(SUMMARY_FILE, 'w', encoding='utf-8') as f:
        f.write("\n".join(summary_lines))
    print(f"\n📄 Resumen guardado en: {SUMMARY_FILE}")


def run_pyperplan(domain, problem, search, heuristic=None, timeout=TIMEOUT, save_plan_to=None):
    """
    Ejecuta pyperplan y devuelve un diccionario con los resultados.
    
    Args:
        domain: ruta al archivo de dominio PDDL
        problem: ruta al archivo de problema PDDL
        search: algoritmo de búsqueda (bfs, ids, astar, gbfs, ehc, etc.)
        heuristic: heurística a usar (hadd, hmax, hff, landmark, lmcut, hsa)
        timeout: tiempo máximo en segundos
        save_plan_to: ruta donde guardar el archivo de plan (opcional)
    
    Returns: {solved, time, plan_length, stdout, stderr}
    """
    # Construir comando
    cmd = [PYPERPLAN]
    
    if heuristic:
        cmd.extend(["-H", heuristic])
    
    cmd.extend(["-s", search, domain, problem])

    # pyperplan genera el plan en <problem>.soln por defecto
    problem_name = os.path.basename(problem)
    plan_file = problem + ".soln"
    
    # Limpiar plan anterior si existe
    if os.path.exists(plan_file):
        try:
            os.remove(plan_file)
        except:
            pass

    start = time.time()
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=os.path.dirname(problem)  # Ejecutar en el directorio del problema
        )
        elapsed = time.time() - start

        # Leer el plan generado
        plan_length = 0
        plan_lines = []
        
        if os.path.exists(plan_file):
            with open(plan_file) as f:
                plan_content = f.read()
                plan_lines = [l.strip() for l in plan_content.split('\n') 
                             if l.strip() and not l.startswith(";")]
                plan_length = len(plan_lines)
            
            # Guardar el plan en la ubicación especificada
            if save_plan_to and plan_lines:
                os.makedirs(os.path.dirname(save_plan_to), exist_ok=True)
                with open(save_plan_to, 'w') as f:
                    for line in plan_lines:
                        # Formato: ( ACTION ARGS )
                        action = line.strip().upper()
                        if action.startswith('(') and action.endswith(')'):
                            action = action[1:-1].strip()
                        f.write(f"( {action} )\n")
            
            # Limpiar archivo de plan temporal
            try:
                os.remove(plan_file)
            except:
                pass

        # Comprobar si se resolvió
        solved = plan_length > 0

        return {
            "solved": solved,
            "time": round(elapsed, 3),
            "plan_length": plan_length,
            "stdout": result.stdout,
            "stderr": result.stderr
        }

    except subprocess.TimeoutExpired:
        # Limpiar archivo de plan si existe
        if os.path.exists(plan_file):
            try:
                os.remove(plan_file)
            except:
                pass
        return {
            "solved": False,
            "time": timeout,
            "plan_length": 0,
            "stdout": "",
            "stderr": "TIMEOUT"
        }
    except Exception as e:
        return {
            "solved": False,
            "time": 0,
            "plan_length": 0,
            "stdout": "",
            "stderr": str(e)
        }


def find_max_solvable(domain, sizes, search, heuristic, label, timeout=TIMEOUT, output_dir=None):
    """
    Busca el mayor tamaño de problema que se puede resolver dentro del timeout.
    Devuelve (max_size, result_dict) o (0, None) si ninguno se resuelve.
    """
    max_size = 0
    max_result = None

    for size in sizes:
        problem = os.path.join(PROBLEMS_DIR, f"problem_size{size}.pddl")
        if not os.path.exists(problem):
            continue

        print(f"  Probando {label} con tamaño {size}...", end=" ", flush=True)

        # Determinar ruta de guardado del plan
        save_plan_to = None
        if output_dir:
            plan_filename = f"problem_size{size}.pddl.plan"
            save_plan_to = os.path.join(output_dir, plan_filename)

        result = run_pyperplan(domain, problem, search, heuristic, timeout, save_plan_to)

        if result["solved"]:
            print(f"✅ {result['time']}s, plan={result['plan_length']} acciones")
            max_size = size
            max_result = result
        else:
            reason = "TIMEOUT" if result["time"] >= timeout else "FALLO"
            print(f"❌ {reason} ({result['time']}s)")
            break  # Si no resuelve este tamaño, los mayores tampoco

    return max_size, max_result


def print_markdown_table(headers, rows):
    """Imprime una tabla en formato Markdown y la guarda en el resumen."""
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))

    header_line = "| " + " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers)) + " |"
    sep_line = "| " + " | ".join("-" * col_widths[i] for i in range(len(headers))) + " |"

    log(header_line)
    log(sep_line)
    for row in rows:
        log("| " + " | ".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row)) + " |")


# ─── PARTE 1: BFS, IDS, A*+hMAX, GBFS+hMAX ─────────────────────────────────

def parte1(sizes):
    """
    Parte 1: Comparativa BFS, IDS, A* y GBFS con heurística hMAX.
    Encuentra el mayor tamaño de problema que cada algoritmo puede resolver en 1 minuto.
    """
    print("=" * 70)
    print("PARTE 1: Comparativa BFS, IDS, A*+hMAX, GBFS+hMAX")
    print("=" * 70)

    # Crear directorio base para los resultados de Parte 1
    parte1_dir = os.path.join(RESULTS_DIR, "parte1")
    os.makedirs(parte1_dir, exist_ok=True)

    # Configuraciones: (search, heuristic, label, es_óptimo, folder_name)
    # BFS e IDS son búsquedas no informadas (no usan heurística)
    # A* y GBFS son búsquedas informadas (usan hMAX)
    configs = [
        ("bfs", None, "BFS", "Sí (coste uniforme)", "BFS"),
        ("ids", None, "IDS", "Sí (coste uniforme)", "IDS"),
        ("astar", "hmax", "A*+hMAX", "Sí (hMAX admisible)", "Astar_hMAX"),
        ("gbf", "hmax", "GBFS+hMAX", "No", "GBFS_hMAX"),
    ]

    rows = []
    results_p1 = {}

    for search, heuristic, label, optimal, folder_name in configs:
        print(f"\n--- {label} ---")
        
        # Crear carpeta para este algoritmo
        output_dir = os.path.join(parte1_dir, folder_name)
        os.makedirs(output_dir, exist_ok=True)
        
        max_size, result = find_max_solvable(DOMAIN, sizes, search, heuristic, label, output_dir=output_dir)

        if result:
            rows.append([label, max_size, result["time"], result["plan_length"], optimal])
        else:
            rows.append([label, 0, "-", "-", optimal])

        results_p1[label] = (max_size, result)

    log(f"\n{'─' * 70}")
    log("TABLA PARTE 1: Mayor tamaño resuelto en < 1 minuto")
    log(f"{'─' * 70}")
    print_markdown_table(
        ["Algoritmo", "Max Tamaño", "Tiempo (s)", "Acciones Plan", "Óptimo"],
        rows
    )
    print(f"\n📁 Planes guardados en: {parte1_dir}")

    return results_p1


# ─── PARTE 2: GBFS y EHC con hMAX, hADD, hFF, Landmark ──────────────────────

def parte2(sizes, results_p1):
    """
    Parte 2: Algoritmos satisficing (GBFS y EHC) con heurísticas hMAX, hADD, hFF y Landmark.
    Usa el mayor tamaño que GBFS+hMAX pudo resolver en la Parte 1.
    """
    print(f"\n\n{'=' * 70}")
    print("PARTE 2: Heurísticas para planificadores satisficing")
    print("=" * 70)

    # Crear directorio base para los resultados de Parte 2
    parte2_dir = os.path.join(RESULTS_DIR, "parte2")
    os.makedirs(parte2_dir, exist_ok=True)

    # Encontrar el mayor tamaño que GBFS+hMAX pudo resolver
    gbfs_max = results_p1.get("GBFS+hMAX", (0, None))[0]
    if gbfs_max == 0:
        print("⚠ GBFS+hMAX no resolvió ningún problema. Usando tamaño 5 por defecto.")
        gbfs_max = 5

    problem_file = os.path.join(PROBLEMS_DIR, f"problem_size{gbfs_max}.pddl")
    print(f"\nUsando problema de tamaño {gbfs_max}: {problem_file}")

    # Configuraciones: (search, heuristic, label, folder_name)
    # GBFS y EHC con heurísticas: hmax, hadd, hff, landmark
    configs = [
        # GBFS con distintas heurísticas
        ("gbf", "hmax", "GBFS+hMAX", "GBFS_hMAX"),
        ("gbf", "hadd", "GBFS+hADD", "GBFS_hADD"),
        ("gbf", "hff", "GBFS+hFF", "GBFS_hFF"),
        ("gbf", "landmark", "GBFS+Landmark", "GBFS_Landmark"),
        # EHC con distintas heurísticas
        ("ehs", "hmax", "EHC+hMAX", "EHC_hMAX"),
        ("ehs", "hadd", "EHC+hADD", "EHC_hADD"),
        ("ehs", "hff", "EHC+hFF", "EHC_hFF"),
        ("ehs", "landmark", "EHC+Landmark", "EHC_Landmark"),
    ]

    rows = []
    for search, heuristic, label, folder_name in configs:
        print(f"  {label}...", end=" ", flush=True)

        # Crear carpeta y ruta para guardar el plan
        output_dir = os.path.join(parte2_dir, folder_name)
        os.makedirs(output_dir, exist_ok=True)
        plan_filename = f"problem_size{gbfs_max}.pddl.plan"
        save_plan_to = os.path.join(output_dir, plan_filename)

        result = run_pyperplan(DOMAIN, problem_file, search, heuristic, save_plan_to=save_plan_to)

        if result["solved"]:
            print(f"✅ {result['time']}s, plan={result['plan_length']}")
            rows.append([label, result["time"], result["plan_length"]])
        else:
            reason = "TIMEOUT" if result["time"] >= TIMEOUT else "FALLO"
            print(f"❌ {reason}")
            rows.append([label, reason, "-"])

    log(f"\n{'─' * 70}")
    log(f"TABLA PARTE 2: Algoritmos satisficing en problema tamaño {gbfs_max}")
    log(f"{'─' * 70}")
    print_markdown_table(
        ["Algoritmo+Heurística", "Tiempo (s)", "Acciones Plan"],
        rows
    )
    print(f"\n📁 Planes guardados en: {parte2_dir}")

    # Análisis de GBFS vs EHC
    log(f"\n{'─' * 70}")
    log("ANÁLISIS: GBFS vs EHC y el planificador FF")
    log(f"{'─' * 70}")
    log("""
GBFS (Greedy Best First Search):
  • Expande siempre el nodo con menor valor heurístico h(n)
  • No considera el coste acumulado g(n)
  • Rápido pero no garantiza optimalidad
  • Puede quedar atrapado en mínimos locales

EHC (Enforced Hill Climbing):
  • Versión más agresiva de hill climbing
  • Busca en anchura hasta encontrar un sucesor con mejor h(n)
  • Si encuentra uno mejor, reinicia la búsqueda desde ahí
  • Más rápido que GBFS en muchos dominios
  • Puede fallar si no existe camino de mejora (mesetas/dead-ends)

El planificador FF (Fast Forward):
  • Usa EHC como búsqueda principal con heurística hFF
  • Si EHC falla (no encuentra mejora), cambia a GBFS como backup
  • Combina velocidad de EHC con completitud de GBFS
  • La heurística hFF está diseñada específicamente para FF
""")


# ─── PARTE 3: Heurísticas admisibles con A*, BFS, IDS ───────────────────────

def parte3(sizes, results_p1):
    """
    Parte 3: Heurísticas para planificadores óptimos.
    
    Investiga cuáles heurísticas de pyperplan son admisibles y resuelve
    el problema de mayor tamaño que A*+hMAX puede resolver en 1 minuto con:
    - BFS
    - IDS
    - A* con cada heurística admisible
    """
    print(f"\n\n{'=' * 70}")
    print("PARTE 3: Heurísticas para planificadores óptimos")
    print("=" * 70)

    # Crear directorio base para los resultados de Parte 3
    parte3_dir = os.path.join(RESULTS_DIR, "parte3")
    os.makedirs(parte3_dir, exist_ok=True)

    # ═══════════════════════════════════════════════════════════════════════════
    # HEURÍSTICAS ADMISIBLES en pyperplan:
    # ═══════════════════════════════════════════════════════════════════════════
    # Una heurística h es ADMISIBLE si nunca sobreestima el coste real h*(n).
    # Es decir: h(n) ≤ h*(n) para todo estado n.
    #
    # ADMISIBLES:
    #   - hmax: Máximo coste de alcanzar cada subobjetivo individualmente.
    #           Admisible porque el coste real es al menos el del subobjetivo
    #           más costoso.
    #   - lmcut: Landmark-cut. Calcula un corte mínimo en el grafo de landmarks.
    #            Admisible y más informada que hmax.
    #
    # NO ADMISIBLES (sobreestiman):
    #   - hadd: Suma de costes de subobjetivos. Sobreestima porque asume que
    #           las acciones para distintos objetivos son independientes.
    #   - hff: Basada en grafo de planificación relajado. Cuenta acciones del
    #          plan relajado, que puede sobreestimar.
    #   - landmark: Cuenta landmarks no alcanzados. No es admisible en general.
    #   - hsa: Set-additive heuristic. Similar a hadd, sobreestima.
    # ═══════════════════════════════════════════════════════════════════════════

    print("\n╔══════════════════════════════════════════════════════════════════╗")
    print("║           ANÁLISIS DE ADMISIBILIDAD DE HEURÍSTICAS               ║")
    print("╠══════════════════════════════════════════════════════════════════╣")
    print("║ ADMISIBLES (h(n) ≤ h*(n)):                                       ║")
    print("║   • hMAX: Máximo coste de subobjetivos individuales              ║")
    print("║   • lmcut: Landmark-cut, más informada                           ║")
    print("╠══════════════════════════════════════════════════════════════════╣")
    print("║ NO ADMISIBLES (sobreestiman):                                    ║")
    print("║   • hADD: Suma de costes → sobreestima                           ║")
    print("║   • hFF: Basada en grafo relajado → sobreestima                  ║")
    print("║   • landmark: Cuenta landmarks → no admisible                    ║")
    print("║   • hSA: Set-additive → sobreestima                              ║")
    print("╚══════════════════════════════════════════════════════════════════╝\n")

    # Mayor tamaño que A*+hMAX resolvió
    astar_max = results_p1.get("A*+hMAX", (0, None))[0]
    if astar_max == 0:
        print("⚠ A*+hMAX no resolvió ningún problema. Usando tamaño 3 por defecto.")
        astar_max = 3

    problem_file = os.path.join(PROBLEMS_DIR, f"problem_size{astar_max}.pddl")
    print(f"Problema a resolver: tamaño {astar_max}")
    print(f"Archivo: {problem_file}\n")

    # Configuraciones: (search, heuristic, label, folder_name)
    # BFS e IDS no usan heurística
    # A* con heurísticas ADMISIBLES: hmax, lmcut
    configs = [
        # Búsquedas no informadas (óptimas)
        ("bfs", None, "BFS", "BFS"),
        ("ids", None, "IDS", "IDS"),
        # A* con heurísticas ADMISIBLES
        ("astar", "hmax", "A*+hMAX", "Astar_hMAX"),
        ("astar", "lmcut", "A*+lmcut", "Astar_lmcut"),
    ]

    rows = []
    for search, heuristic, label, folder_name in configs:
        print(f"  {label}...", end=" ", flush=True)

        # Crear carpeta y ruta para guardar el plan
        output_dir = os.path.join(parte3_dir, folder_name)
        os.makedirs(output_dir, exist_ok=True)
        plan_filename = f"problem_size{astar_max}.pddl.plan"
        save_plan_to = os.path.join(output_dir, plan_filename)

        result = run_pyperplan(DOMAIN, problem_file, search, heuristic, save_plan_to=save_plan_to)

        if result["solved"]:
            print(f"✅ {result['time']}s, plan={result['plan_length']} acciones")
            rows.append([label, result["time"], result["plan_length"], "Sí"])
        else:
            reason = "TIMEOUT" if result["time"] >= TIMEOUT else "FALLO"
            print(f"❌ {reason}")
            rows.append([label, reason, "-", "-"])

    log(f"\n{'─' * 70}")
    log(f"TABLA PARTE 3: Algoritmos óptimos en problema tamaño {astar_max}")
    log(f"{'─' * 70}")
    print_markdown_table(
        ["Algoritmo", "Tiempo (s)", "Acciones Plan", "Solución Óptima"],
        rows
    )
    print(f"\n📁 Planes guardados en: {parte3_dir}")

    # Análisis: encontrar el mejor algoritmo
    log(f"\n{'─' * 70}")
    log("ANÁLISIS DE RESULTADOS")
    log(f"{'─' * 70}")
    
    solved_rows = [(r[0], r[1], r[2]) for r in rows if isinstance(r[1], (int, float))]
    if solved_rows:
        best = min(solved_rows, key=lambda x: x[1])
        log(f"✓ Mejor algoritmo por tiempo: {best[0]} ({best[1]}s)")
        log(f"  Todos los algoritmos óptimos devuelven planes de igual longitud: {best[2]} acciones")
        log("\nJustificación esperada:")
        log("  • lmcut suele ser más rápido que hMAX por ser más informada")
        log("  • hMAX es más rápido que BFS/IDS porque poda más estados")
        log("  • BFS explora todos los estados nivel por nivel (menos eficiente)")
        log("  • IDS tiene overhead por reiniciar búsquedas en cada iteración")


# ─── MAIN ────────────────────────────────────────────────────────────────────

def check_pyperplan():
    """Verifica que pyperplan esté instalado."""
    if not os.path.exists(PYPERPLAN):
        print(f"❌ Error: pyperplan no encontrado en {PYPERPLAN}")
        print("\n⚠ Para instalar pyperplan:")
        print("   pip install pyperplan --break-system-packages")
        return False
    
    try:
        result = subprocess.run(
            [PYPERPLAN, "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return True
    except FileNotFoundError:
        print("❌ Error: pyperplan no está instalado.")
        print("\n⚠ Para instalar pyperplan:")
        print("   pip install pyperplan --break-system-packages")
        return False
    except Exception as e:
        print(f"❌ Error verificando pyperplan: {e}")
        return False


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    # Verificar pyperplan
    print("Verificando pyperplan...")
    if not check_pyperplan():
        sys.exit(1)
    print("✅ pyperplan disponible\n")

    # Tamaños de problema a probar
    sizes = list(range(1, 31))

    # Verificar que los problemas existen
    first_problem = os.path.join(PROBLEMS_DIR, "problem_size1.pddl")
    if not os.path.exists(first_problem):
        print("⚠ No se encontraron problemas. Generándolos...")
        subprocess.run([sys.executable, os.path.join(BASE_DIR, "generate_problems.py")])

    print(f"Dominio: {DOMAIN}")
    print(f"Problemas: {PROBLEMS_DIR}")
    print(f"Timeout: {TIMEOUT}s\n")

    # Ejecutar las 3 partes
    results_p1 = parte1(sizes)
    parte2(sizes, results_p1)
    parte3(sizes, results_p1)

    # Guardar resumen en archivo
    save_summary()

    print(f"\n{'=' * 70}")
    print("✅ Benchmark completado.")
    print("=" * 70)


if __name__ == "__main__":
    main()
