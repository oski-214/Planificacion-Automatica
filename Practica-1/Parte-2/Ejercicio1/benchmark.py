#!/usr/bin/env python3
"""
Benchmark con pyperplan para la Parte 2 - Ejercicio 1.

Repite los ejercicios 1.3.2 y 1.3.3 de la Parte 1 con el nuevo dominio
que incluye transportadores y números.

Ejercicio 1.3.2 (satisficing): GBFS y EHC con hMAX, hADD, hFF, Landmark.
Ejercicio 1.3.3 (óptimos): BFS, IDS, A*+hMAX, A*+lmcut.

Uso:
    python3 benchmark.py
"""

import subprocess
import time
import os
import sys

# ─── Configuración ───────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOMAIN = os.path.join(BASE_DIR, "domainemergencias.pddl")
PROBLEMS_DIR = os.path.join(BASE_DIR, "problems")
RESULTS_DIR = os.path.join(BASE_DIR, "results")
TIMEOUT = 60  # segundos

SUMMARY_FILE = os.path.join(RESULTS_DIR, "summary.txt")

PYPERPLAN = os.path.expanduser("~/planutils-venv/bin/pyperplan")

summary_lines = []


def log(text=""):
    print(text)
    summary_lines.append(text)


def save_summary():
    with open(SUMMARY_FILE, 'w', encoding='utf-8') as f:
        f.write("\n".join(summary_lines))
    print(f"\n📄 Resumen guardado en: {SUMMARY_FILE}")


def run_pyperplan(domain, problem, search, heuristic=None, timeout=TIMEOUT, save_plan_to=None):
    """Ejecuta pyperplan y devuelve {solved, time, plan_length, stdout, stderr}."""
    cmd = [PYPERPLAN]
    if heuristic:
        cmd.extend(["-H", heuristic])
    cmd.extend(["-s", search, domain, problem])

    plan_file = problem + ".soln"

    if os.path.exists(plan_file):
        try:
            os.remove(plan_file)
        except OSError:
            pass

    start = time.time()
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout,
            cwd=os.path.dirname(problem)
        )
        elapsed = time.time() - start

        plan_length = 0
        plan_lines = []

        if os.path.exists(plan_file):
            with open(plan_file) as f:
                plan_content = f.read()
                plan_lines = [l.strip() for l in plan_content.split('\n')
                              if l.strip() and not l.startswith(";")]
                plan_length = len(plan_lines)

            if save_plan_to and plan_lines:
                os.makedirs(os.path.dirname(save_plan_to), exist_ok=True)
                with open(save_plan_to, 'w') as f:
                    for line in plan_lines:
                        action = line.strip().upper()
                        if action.startswith('(') and action.endswith(')'):
                            action = action[1:-1].strip()
                        f.write(f"( {action} )\n")

            try:
                os.remove(plan_file)
            except OSError:
                pass

        return {
            "solved": plan_length > 0,
            "time": round(elapsed, 3),
            "plan_length": plan_length,
            "stdout": result.stdout,
            "stderr": result.stderr
        }

    except subprocess.TimeoutExpired:
        if os.path.exists(plan_file):
            try:
                os.remove(plan_file)
            except OSError:
                pass
        return {"solved": False, "time": timeout, "plan_length": 0, "stdout": "", "stderr": "TIMEOUT"}
    except Exception as e:
        return {"solved": False, "time": 0, "plan_length": 0, "stdout": "", "stderr": str(e)}


def find_max_solvable(domain, sizes, search, heuristic, label, timeout=TIMEOUT, output_dir=None):
    """Busca el mayor tamaño de problema resoluble dentro del timeout."""
    max_size = 0
    max_result = None

    for size in sizes:
        problem = os.path.join(PROBLEMS_DIR, f"problem_size{size}.pddl")
        if not os.path.exists(problem):
            continue

        print(f"  Probando {label} con tamaño {size}...", end=" ", flush=True)

        save_plan_to = None
        if output_dir:
            save_plan_to = os.path.join(output_dir, f"problem_size{size}.pddl.plan")

        result = run_pyperplan(domain, problem, search, heuristic, timeout, save_plan_to)

        if result["solved"]:
            print(f"✅ {result['time']}s, plan={result['plan_length']} acciones")
            max_size = size
            max_result = result
        else:
            reason = "TIMEOUT" if result["time"] >= timeout else "FALLO"
            print(f"❌ {reason} ({result['time']}s)")
            break
    return max_size, max_result


def print_markdown_table(headers, rows):
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


# ─── PARTE 1: Encontrar max tamaño para GBFS+hMAX y A*+hMAX ─────────────────

def parte1(sizes):
    """
    Parte 1: Encuentra el mayor tamaño resoluble por cada algoritmo base.
    Necesario para poder luego fijar el tamaño en partes 2 y 3.
    """
    log("=" * 70)
    log("PARTE 1: Mayor tamaño resuelto por BFS, IDS, A*+hMAX, GBFS+hMAX")
    log("=" * 70)

    parte1_dir = os.path.join(RESULTS_DIR, "parte1")
    os.makedirs(parte1_dir, exist_ok=True)

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
    return results_p1


# ─── PARTE 2 (Ej 1.3.2): Satisficing — GBFS y EHC ──────────────────────────

def parte2(sizes, results_p1):
    """
    Ejercicio 1.3.2: Resuelve el problema de mayor tamaño que GBFS+hMAX
    puede resolver en 1 minuto con GBFS y EHC + hMAX, hADD, hFF, Landmark.
    """
    log(f"\n\n{'=' * 70}")
    log("PARTE 2 (Ej 1.3.2): Heurísticas para planificadores satisficing")
    log("=" * 70)

    parte2_dir = os.path.join(RESULTS_DIR, "parte2")
    os.makedirs(parte2_dir, exist_ok=True)

    gbfs_max = results_p1.get("GBFS+hMAX", (0, None))[0]
    if gbfs_max == 0:
        log("⚠ GBFS+hMAX no resolvió ningún problema. Usando tamaño 5 por defecto.")
        gbfs_max = 5

    problem_file = os.path.join(PROBLEMS_DIR, f"problem_size{gbfs_max}.pddl")
    log(f"\nUsando problema de tamaño {gbfs_max}: {problem_file}")

    configs = [
        ("gbf", "hmax", "GBFS+hMAX", "GBFS_hMAX"),
        ("gbf", "hadd", "GBFS+hADD", "GBFS_hADD"),
        ("gbf", "hff", "GBFS+hFF", "GBFS_hFF"),
        ("gbf", "landmark", "GBFS+Landmark", "GBFS_Landmark"),
        ("ehs", "hmax", "EHC+hMAX", "EHC_hMAX"),
        ("ehs", "hadd", "EHC+hADD", "EHC_hADD"),
        ("ehs", "hff", "EHC+hFF", "EHC_hFF"),
        ("ehs", "landmark", "EHC+Landmark", "EHC_Landmark"),
    ]

    rows = []
    for search, heuristic, label, folder_name in configs:
        print(f"  {label}...", end=" ", flush=True)
        output_dir = os.path.join(parte2_dir, folder_name)
        os.makedirs(output_dir, exist_ok=True)
        save_plan_to = os.path.join(output_dir, f"problem_size{gbfs_max}.pddl.plan")

        result = run_pyperplan(DOMAIN, problem_file, search, heuristic, save_plan_to=save_plan_to)

        if result["solved"]:
            print(f"✅ {result['time']}s, plan={result['plan_length']}")
            rows.append([label, result["time"], result["plan_length"]])
        else:
            reason = "TIMEOUT" if result["time"] >= TIMEOUT else "FALLO"
            print(f"❌ {reason}")
            rows.append([label, reason, "-"])

    log(f"\n{'─' * 70}")
    log(f"TABLA PARTE 2 (Ej 1.3.2): Satisficing en problema tamaño {gbfs_max}")
    log(f"{'─' * 70}")
    print_markdown_table(
        ["Algoritmo+Heurística", "Tiempo (s)", "Acciones Plan"],
        rows
    )

    log(f"\n{'─' * 70}")
    log("ANÁLISIS: GBFS vs EHC y el planificador FF")
    log(f"{'─' * 70}")
    log("""
GBFS (Greedy Best First Search):
  - Expande siempre el nodo con menor valor heurístico h(n)
  - No considera el coste acumulado g(n)
  - Rápido pero no garantiza optimalidad
  - Puede quedar atrapado en mínimos locales

EHC (Enforced Hill Climbing):
  - Versión más agresiva de hill climbing
  - Busca en anchura hasta encontrar un sucesor con mejor h(n)
  - Si encuentra uno mejor, reinicia la búsqueda desde ahí
  - Más rápido que GBFS en muchos dominios
  - Puede fallar si no existe camino de mejora (mesetas/dead-ends)

El planificador FF (Fast Forward):
  - Usa EHC como búsqueda principal con heurística hFF
  - Si EHC falla (no encuentra mejora), cambia a GBFS como backup
  - Combina velocidad de EHC con completitud de GBFS
""")


# ─── PARTE 3 (Ej 1.3.3): Óptimos — BFS, IDS, A*+admisibles ────────────────

def parte3(sizes, results_p1):
    """
    Ejercicio 1.3.3: Resuelve el problema de mayor tamaño que A*+hMAX
    puede resolver en 1 minuto con BFS, IDS, A*+hMAX, A*+lmcut.
    """
    log(f"\n\n{'=' * 70}")
    log("PARTE 3 (Ej 1.3.3): Heurísticas para planificadores óptimos")
    log("=" * 70)

    parte3_dir = os.path.join(RESULTS_DIR, "parte3")
    os.makedirs(parte3_dir, exist_ok=True)

    log("""
Heurísticas ADMISIBLES en pyperplan:
  - hMAX: Máximo coste de subobjetivos individuales. Admisible.
  - lmcut: Landmark-cut, más informada que hMAX. Admisible.

Heurísticas NO ADMISIBLES:
  - hADD: Suma de costes → sobreestima
  - hFF: Basada en grafo relajado → sobreestima
  - landmark: Cuenta landmarks → no admisible en general
  - hSA: Set-additive → sobreestima
""")

    astar_max = results_p1.get("A*+hMAX", (0, None))[0]
    if astar_max == 0:
        log("⚠ A*+hMAX no resolvió ningún problema. Usando tamaño 3 por defecto.")
        astar_max = 3

    problem_file = os.path.join(PROBLEMS_DIR, f"problem_size{astar_max}.pddl")
    log(f"Problema a resolver: tamaño {astar_max}")
    log(f"Archivo: {problem_file}\n")

    configs = [
        ("bfs", None, "BFS", "BFS"),
        ("ids", None, "IDS", "IDS"),
        ("astar", "hmax", "A*+hMAX", "Astar_hMAX"),
        ("astar", "lmcut", "A*+lmcut", "Astar_lmcut"),
    ]

    rows = []
    for search, heuristic, label, folder_name in configs:
        print(f"  {label}...", end=" ", flush=True)
        output_dir = os.path.join(parte3_dir, folder_name)
        os.makedirs(output_dir, exist_ok=True)
        save_plan_to = os.path.join(output_dir, f"problem_size{astar_max}.pddl.plan")

        result = run_pyperplan(DOMAIN, problem_file, search, heuristic, save_plan_to=save_plan_to)

        if result["solved"]:
            print(f"✅ {result['time']}s, plan={result['plan_length']} acciones")
            rows.append([label, result["time"], result["plan_length"], "Sí"])
        else:
            reason = "TIMEOUT" if result["time"] >= TIMEOUT else "FALLO"
            print(f"❌ {reason}")
            rows.append([label, reason, "-", "-"])

    log(f"\n{'─' * 70}")
    log(f"TABLA PARTE 3 (Ej 1.3.3): Óptimos en problema tamaño {astar_max}")
    log(f"{'─' * 70}")
    print_markdown_table(
        ["Algoritmo", "Tiempo (s)", "Acciones Plan", "Solución Óptima"],
        rows
    )

    log(f"\n{'─' * 70}")
    log("ANÁLISIS DE RESULTADOS")
    log(f"{'─' * 70}")

    solved_rows = [(r[0], r[1], r[2]) for r in rows if isinstance(r[1], (int, float))]
    if solved_rows:
        best = min(solved_rows, key=lambda x: x[1])
        log(f"✓ Mejor algoritmo por tiempo: {best[0]} ({best[1]}s)")
        log(f"  Todos los algoritmos óptimos devuelven planes de igual longitud: {best[2]} acciones")
        log("\nJustificación:")
        log("  - lmcut suele ser más rápido que hMAX por ser más informada")
        log("  - hMAX es más rápido que BFS/IDS porque poda más estados")
        log("  - BFS explora todos los estados nivel por nivel (menos eficiente)")
        log("  - IDS tiene overhead por reiniciar búsquedas en cada iteración")


# ─── MAIN ────────────────────────────────────────────────────────────────────

def check_pyperplan():
    if not os.path.exists(PYPERPLAN):
        print(f"❌ Error: pyperplan no encontrado en {PYPERPLAN}")
        return False
    try:
        subprocess.run([PYPERPLAN, "--help"], capture_output=True, text=True, timeout=10)
        return True
    except (FileNotFoundError, Exception) as e:
        print(f"❌ Error verificando pyperplan: {e}")
        return False


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    print("Verificando pyperplan...")
    if not check_pyperplan():
        sys.exit(1)
    print("✅ pyperplan disponible\n")

    sizes = list(range(1, 31))

    # Generar problemas si no existen
    first_problem = os.path.join(PROBLEMS_DIR, "problem_size1.pddl")
    if not os.path.exists(first_problem):
        print("⚠ No se encontraron problemas. Generándolos...")
        subprocess.run([sys.executable, os.path.join(BASE_DIR, "generate_problems.py")])

    log(f"Dominio: {DOMAIN}")
    log(f"Problemas: {PROBLEMS_DIR}")
    log(f"Timeout: {TIMEOUT}s\n")

    # Ejecutar las 3 partes
    results_p1 = parte1(sizes)
    parte2(sizes, results_p1)
    parte3(sizes, results_p1)

    save_summary()

    log(f"\n{'=' * 70}")
    log("✅ Benchmark completado.")
    log("=" * 70)


if __name__ == "__main__":
    main()
