#!/usr/bin/env python3
"""
Benchmark de pyperplan para el Ejercicio 1.3.

Ejecuta pyperplan con distintas combinaciones de algoritmos y heurísticas,
midiendo tiempos y recogiendo resultados. Genera tablas en formato Markdown.

Uso:
    python3 benchmark.py
"""

import subprocess
import time
import os
import sys
import signal
import re
from pathlib import Path

# ─── Configuración ───────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOMAIN = os.path.join(BASE_DIR, "domainemergencias.pddl")
PROBLEMS_DIR = os.path.join(BASE_DIR, "problems")
RESULTS_DIR = os.path.join(BASE_DIR, "results")
TIMEOUT = 60  # segundos


def run_pyperplan(domain, problem, search, heuristic=None, timeout=TIMEOUT):
    """
    Ejecuta pyperplan y devuelve un diccionario con los resultados.
    Returns: {solved, time, plan_length, plan_file} o None si timeout/error.
    """
    cmd = ["pyperplan", "-s", search]
    if heuristic:
        cmd += ["-H", heuristic]
    cmd += [domain, problem]

    start = time.time()
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        elapsed = time.time() - start

        # Buscar archivo de plan generado
        plan_file = problem + ".soln"
        plan_length = 0
        if os.path.exists(plan_file):
            with open(plan_file) as f:
                plan_lines = [l.strip() for l in f.readlines() if l.strip() and not l.startswith(";")]
                plan_length = len(plan_lines)

        # Comprobar si se resolvió
        if result.returncode == 0 and plan_length > 0:
            return {
                "solved": True,
                "time": round(elapsed, 3),
                "plan_length": plan_length,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        else:
            return {
                "solved": False,
                "time": round(elapsed, 3),
                "plan_length": 0,
                "stdout": result.stdout,
                "stderr": result.stderr
            }

    except subprocess.TimeoutExpired:
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


def find_max_solvable(domain, sizes, search, heuristic=None, timeout=TIMEOUT):
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

        label = f"{search}" + (f"+{heuristic}" if heuristic else "")
        print(f"  Probando {label} con tamaño {size}...", end=" ", flush=True)

        result = run_pyperplan(domain, problem, search, heuristic, timeout)

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
    """Imprime una tabla en formato Markdown."""
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))

    header_line = "| " + " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers)) + " |"
    sep_line = "| " + " | ".join("-" * col_widths[i] for i in range(len(headers))) + " |"

    print(header_line)
    print(sep_line)
    for row in rows:
        print("| " + " | ".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row)) + " |")


# ─── PARTE 1: BFS, IDS, A*+hmax, GBFS+hmax ─────────────────────────────────

def parte1(sizes):
    print("=" * 70)
    print("PARTE 1: Comparativa BFS, IDS, A*+hmax, GBFS+hmax")
    print("=" * 70)

    configs = [
        ("bfs", None, "BFS", "Sí (coste uniforme)"),
        ("ids", None, "IDS", "Sí (coste uniforme)"),
        ("astar", "hmax", "A*+hmax", "Sí (hmax admisible)"),
        ("gbf", "hmax", "GBFS+hmax", "No"),
    ]

    rows = []
    results_p1 = {}

    for search, heuristic, label, optimal in configs:
        print(f"\n--- {label} ---")
        max_size, result = find_max_solvable(DOMAIN, sizes, search, heuristic)

        if result:
            rows.append([label, max_size, result["time"], result["plan_length"], optimal])
        else:
            rows.append([label, 0, "-", "-", optimal])

        results_p1[label] = (max_size, result)

    print(f"\n{'─' * 70}")
    print("TABLA PARTE 1: Mayor tamaño resuelto en < 1 minuto")
    print(f"{'─' * 70}")
    print_markdown_table(
        ["Algoritmo", "Max Tamaño", "Tiempo (s)", "Acciones Plan", "Óptimo"],
        rows
    )

    return results_p1


# ─── PARTE 2: GBFS y EHC con hmax, hadd, hff, landmark ──────────────────────

def parte2(sizes, results_p1):
    print(f"\n\n{'=' * 70}")
    print("PARTE 2: Heurísticas para planificadores satisficing")
    print("=" * 70)

    # Encontrar el mayor tamaño que GBFS+hmax pudo resolver
    gbfs_max = results_p1.get("GBFS+hmax", (0, None))[0]
    if gbfs_max == 0:
        print("⚠ GBFS+hmax no resolvió ningún problema. Usando tamaño 5 por defecto.")
        gbfs_max = 5

    problem_file = os.path.join(PROBLEMS_DIR, f"problem_size{gbfs_max}.pddl")
    print(f"\nUsando problema de tamaño {gbfs_max}: {problem_file}")

    algorithms = ["gbf", "ehs"]
    heuristics = ["hmax", "hadd", "hff", "landmark"]

    rows = []
    for search in algorithms:
        for heur in heuristics:
            label = f"{search.upper()}+{heur}"
            print(f"  {label}...", end=" ", flush=True)

            result = run_pyperplan(DOMAIN, problem_file, search, heur)

            if result["solved"]:
                print(f"✅ {result['time']}s, plan={result['plan_length']}")
                rows.append([label, result["time"], result["plan_length"]])
            else:
                reason = "TIMEOUT" if result["time"] >= TIMEOUT else "FALLO"
                print(f"❌ {reason}")
                rows.append([label, reason, "-"])

    print(f"\n{'─' * 70}")
    print(f"TABLA PARTE 2: Algoritmos satisficing en problema tamaño {gbfs_max}")
    print(f"{'─' * 70}")
    print_markdown_table(
        ["Algoritmo+Heurística", "Tiempo (s)", "Acciones Plan"],
        rows
    )


# ─── PARTE 3: Heurísticas admisibles con A*, BFS, IDS ───────────────────────

def parte3(sizes, results_p1):
    print(f"\n\n{'=' * 70}")
    print("PARTE 3: Heurísticas para planificadores óptimos")
    print("=" * 70)

    # Heurísticas admisibles en pyperplan:
    #   - blind (h=0, trivialmente admisible)
    #   - hmax (admisible)
    #   - lmcut (admisible)
    # No admisibles:
    #   - hadd (no admisible, sobreestima)
    #   - hff (no admisible)
    #   - hsa (no admisible, sobreestima)
    #   - landmark (no admisible en general)

    print("\nHeurísticas admisibles: blind (h=0), hmax, lmcut")
    print("Heurísticas NO admisibles: hadd, hff, hsa, landmark\n")

    # Mayor tamaño que A*+hmax resolvió
    astar_max = results_p1.get("A*+hmax", (0, None))[0]
    if astar_max == 0:
        print("⚠ A*+hmax no resolvió ningún problema. Usando tamaño 3 por defecto.")
        astar_max = 3

    problem_file = os.path.join(PROBLEMS_DIR, f"problem_size{astar_max}.pddl")
    print(f"Usando problema de tamaño {astar_max}: {problem_file}")

    configs = [
        ("bfs", None, "BFS"),
        ("ids", None, "IDS"),
        ("astar", "blind", "A*+blind"),
        ("astar", "hmax", "A*+hmax"),
        ("astar", "lmcut", "A*+lmcut"),
    ]

    rows = []
    for search, heur, label in configs:
        print(f"  {label}...", end=" ", flush=True)

        result = run_pyperplan(DOMAIN, problem_file, search, heur)

        if result["solved"]:
            print(f"✅ {result['time']}s, plan={result['plan_length']}")
            rows.append([label, result["time"], result["plan_length"]])
        else:
            reason = "TIMEOUT" if result["time"] >= TIMEOUT else "FALLO"
            print(f"❌ {reason}")
            rows.append([label, reason, "-"])

    print(f"\n{'─' * 70}")
    print(f"TABLA PARTE 3: Algoritmos óptimos en problema tamaño {astar_max}")
    print(f"{'─' * 70}")
    print_markdown_table(
        ["Algoritmo+Heurística", "Tiempo (s)", "Acciones Plan"],
        rows
    )


# ─── MAIN ────────────────────────────────────────────────────────────────────

def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)

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

    print(f"\n\n{'=' * 70}")
    print("✅ Benchmark completado.")
    print("=" * 70)


if __name__ == "__main__":
    main()
