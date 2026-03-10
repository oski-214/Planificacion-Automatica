#!/usr/bin/env python3
"""
Benchmark para LPG-TD: compara modalidades quality vs speed.

Para cada número de drones/transportadores (1..10), genera problemas de tamaño
creciente y encuentra el mayor que LPG-TD resuelve en modo quality en ≤ 1 minuto.
Luego re-ejecuta ese problema en modo speed y compara resultados.
"""

import os
import sys
import subprocess
import re
import time
import glob

# Importar el generador de problemas
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generate_problem_temporal import generate_problem

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LPG_TD = os.path.expanduser("~/.planutils/packages/lpg-td/bin/lpg-td")
DOMAIN = os.path.join(BASE_DIR, "domainemergencias_temporal.pddl")
PROBLEMS_DIR = os.path.join(BASE_DIR, "problems")
PLANS_DIR = os.path.join(BASE_DIR, "plans")
RESULTS_DIR = os.path.join(BASE_DIR, "results")
TIMEOUT = 60 # 1 minuto


def parse_plan_output(output):
    """Extrae métricas de la salida de LPG-TD.
    Si hay varias soluciones, toma la última (mejor calidad)."""
    metrics = {}

    # Buscar la última aparición de cada métrica (última solución = mejor)
    for m in re.finditer(r"Total time:\s+([\d.]+)", output):
        metrics["cpu_time"] = float(m.group(1))

    for m in re.finditer(r"Actions:\s+(\d+)", output):
        metrics["actions"] = int(m.group(1))

    for m in re.finditer(r"Duration:\s+([\d.]+)", output):
        metrics["duration"] = float(m.group(1))

    for m in re.finditer(r"MakeSpan\s+([\d.]+)", output):
        metrics["makespan"] = float(m.group(1))

    for m in re.finditer(r"Plan quality:\s+([\d.]+)", output):
        metrics["quality"] = float(m.group(1))

    # Contar soluciones encontradas
    solutions = re.findall(r"Solution number:\s+(\d+)", output)
    if solutions:
        metrics["num_solutions"] = int(solutions[-1])

    return metrics


def run_lpg_td(domain_file, problem_file, mode="speed", timeout=60, n_drones=1):
    """Ejecuta LPG-TD y devuelve métricas del plan.
    mode: 'speed', 'quality' o 'n1' (para -n 1)
    Los planes se generan en PLANS_DIR/{n_drones}_drones/{mode}/
    """
    import shutil

    plans_subdir = os.path.join(PLANS_DIR, f"{n_drones}_drones", mode)
    os.makedirs(plans_subdir, exist_ok=True)

    # Copiar el problema a la subcarpeta para que LPG-TD genere planes ahí
    prob_basename = os.path.basename(problem_file)
    local_prob = os.path.join(plans_subdir, prob_basename)
    shutil.copy2(problem_file, local_prob)

    if mode == "quality":
        # -quality desactiva best-first search y no converge en este dominio temporal.
        # Usamos -n 10 para buscar hasta 10 soluciones mejorando iterativamente,
        # lo cual emula el comportamiento de optimización de calidad.
        cmd = [LPG_TD, "-o", domain_file, "-f", prob_basename, "-n", "10", "-cputime", str(timeout)]
    elif mode == "speed":
        cmd = [LPG_TD, "-o", domain_file, "-f", prob_basename, "-speed", "-cputime", str(timeout)]
    else:
        cmd = [LPG_TD, "-o", domain_file, "-f", prob_basename, "-n", "1", "-cputime", str(timeout)]

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout + 10, cwd=plans_subdir
        )
        output = result.stdout + result.stderr

        metrics = parse_plan_output(output)
        if metrics:
            metrics["solved"] = True
        else:
            metrics["solved"] = False

        # Limpiar la copia temporal del problema
        if os.path.exists(local_prob):
            os.remove(local_prob)

        # Para este problema, quedarse solo con el mejor plan (el de número más alto)
        # y renombrarlo a un nombre limpio sin sufijo numérico
        plan_prefix = f"plan_{prob_basename}"
        this_plans = sorted(glob.glob(os.path.join(plans_subdir, f"{plan_prefix}*")))
        if this_plans:
            best_plan = this_plans[-1]
            clean_name = os.path.join(plans_subdir, f"{plan_prefix}.SOL")
            if best_plan != clean_name:
                if os.path.exists(clean_name):
                    os.remove(clean_name)
                os.rename(best_plan, clean_name)
            # Borrar los intermedios que no sean el renombrado
            for pf in glob.glob(os.path.join(plans_subdir, f"{plan_prefix}*")):
                if pf != clean_name:
                    os.remove(pf)

        return metrics

    except subprocess.TimeoutExpired:
        if os.path.exists(local_prob):
            os.remove(local_prob)
        return {"solved": False, "cpu_time": timeout}


def generate_and_save_problem(num_drones, num_carriers, num_goals, num_locations=4, seed=42):
    """Genera un problema temporal y lo guarda en PROBLEMS_DIR/{n}_drones/."""
    num_persons = num_goals
    num_crates = num_goals * 2
    carrier_capacity = 4

    problem_name, content = generate_problem(
        num_drones=num_drones,
        num_carriers=num_carriers,
        num_locations=num_locations,
        num_persons=num_persons,
        num_crates=num_crates,
        num_goals=num_goals,
        carrier_capacity=carrier_capacity,
        seed=seed
    )

    problems_subdir = os.path.join(PROBLEMS_DIR, f"{num_drones}_drones")
    os.makedirs(problems_subdir, exist_ok=True)
    filepath = os.path.join(problems_subdir, f"{problem_name}.pddl")
    with open(filepath, 'w') as f:
        f.write(content + "\n")

    return filepath


def find_max_solvable(num_drones, max_timeout=TIMEOUT):
    """
    Para un número dado de drones/carriers, encuentra el mayor número de
    goals que LPG-TD puede resolver en quality mode dentro del timeout.
    """
    # Empezamos con goals pequeños y vamos subiendo
    goal_sizes = list(range(2, 20, 2))  # 2, 4, 6, 8, 10, 12, 14, 16, 18

    best_goals = 0
    best_file = None
    best_metrics = None

    for goals in goal_sizes:
        prob_file = generate_and_save_problem(num_drones, num_drones, goals, seed=42)
        print(f"  Probando {num_drones} drones, {goals} goals en modo quality... ", end="", flush=True)

        metrics = run_lpg_td(DOMAIN, prob_file, mode="quality", timeout=max_timeout, n_drones=num_drones)

        if metrics.get("solved"):
            cpu = metrics.get("cpu_time", "?")
            dur = metrics.get("duration", "?")
            print(f"RESUELTO (cpu={cpu:.2f}s, duración={dur})")
            best_goals = goals
            best_file = prob_file
            best_metrics = metrics
        else:
            print(f"TIMEOUT (>{max_timeout}s)")
            break

    return best_goals, best_file, best_metrics


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    # Limpiar carpetas de ejecuciones anteriores
    import shutil
    if os.path.exists(PLANS_DIR):
        shutil.rmtree(PLANS_DIR)
    if os.path.exists(PROBLEMS_DIR):
        shutil.rmtree(PROBLEMS_DIR)

    results = []

    print("=" * 80)
    print("BENCHMARK LPG-TD: quality vs speed")
    print("=" * 80)

    for n_drones in range(1, 11):
        print(f"\n--- {n_drones} dron(es) / {n_drones} transportador(es) ---")
        max_goals, prob_file, quality_metrics = find_max_solvable(n_drones)

        if max_goals == 0 or quality_metrics is None:
            print(f"  No se pudo resolver ningún problema con {n_drones} drones.")
            results.append({
                "drones": n_drones,
                "max_goals": 0,
                "quality": None,
                "speed": None
            })
            continue

        print(f"  Mayor problema resuelto en quality: {max_goals} goals")

        # Re-ejecutar en modo speed con el mismo problema
        print(f"  Ejecutando en modo speed... ", end="", flush=True)
        speed_metrics = run_lpg_td(DOMAIN, prob_file, mode="speed", timeout=TIMEOUT, n_drones=n_drones)

        if speed_metrics.get("solved"):
            cpu = speed_metrics.get("cpu_time", "?")
            dur = speed_metrics.get("duration", "?")
            print(f"RESUELTO (cpu={cpu:.2f}s, duración={dur})")
        else:
            print("TIMEOUT")

        results.append({
            "drones": n_drones,
            "max_goals": max_goals,
            "quality": quality_metrics,
            "speed": speed_metrics if speed_metrics.get("solved") else None
        })

    # Imprimir tabla comparativa
    print("\n" + "=" * 80)
    print("TABLA COMPARATIVA: Quality vs Speed")
    print("=" * 80)

    header = f"{'Drones':>6} | {'Goals':>5} | {'T.Quality(s)':>12} | {'Pasos Q':>7} | {'Dur. Q':>8} | {'T.Speed(s)':>11} | {'Pasos S':>7} | {'Dur. S':>8}"
    print(header)
    print("-" * len(header))

    for r in results:
        d = r["drones"]
        g = r["max_goals"]
        if r["quality"] is None:
            print(f"{d:>6} | {g:>5} | {'N/A':>12} | {'N/A':>7} | {'N/A':>8} | {'N/A':>11} | {'N/A':>7} | {'N/A':>8}")
            continue

        qt = r["quality"].get("cpu_time", 0)
        qa = r["quality"].get("actions", 0)
        qd = r["quality"].get("duration", 0)

        if r["speed"]:
            st = r["speed"].get("cpu_time", 0)
            sa = r["speed"].get("actions", 0)
            sd = r["speed"].get("duration", 0)
            print(f"{d:>6} | {g:>5} |     {qt:>8.2f} | {qa:>7} | {qd:>8.1f} |    {st:>8.2f} | {sa:>7} | {sd:>8.1f}")
        else:
            print(f"{d:>6} | {g:>5} |     {qt:>8.2f} | {qa:>7} | {qd:>8.1f} | {'TIMEOUT':>11} | {'N/A':>7} | {'N/A':>8}")

    # Guardar resultados en archivo
    results_file = os.path.join(RESULTS_DIR, "benchmark_results.txt")
    with open(results_file, 'w') as f:
        f.write("BENCHMARK LPG-TD: quality vs speed\n")
        f.write("=" * 80 + "\n\n")
        f.write(header + "\n")
        f.write("-" * len(header) + "\n")

        for r in results:
            d = r["drones"]
            g = r["max_goals"]
            if r["quality"] is None:
                f.write(f"{d:>6} | {g:>5} | {'N/A':>12} | {'N/A':>7} | {'N/A':>8} | {'N/A':>11} | {'N/A':>7} | {'N/A':>8}\n")
                continue

            qt = r["quality"].get("cpu_time", 0)
            qa = r["quality"].get("actions", 0)
            qd = r["quality"].get("duration", 0)

            if r["speed"]:
                st = r["speed"].get("cpu_time", 0)
                sa = r["speed"].get("actions", 0)
                sd = r["speed"].get("duration", 0)
                f.write(f"{d:>6} | {g:>5} |     {qt:>8.2f} | {qa:>7} | {qd:>8.1f} |    {st:>8.2f} | {sa:>7} | {sd:>8.1f}\n")
            else:
                f.write(f"{d:>6} | {g:>5} |     {qt:>8.2f} | {qa:>7} | {qd:>8.1f} | {'TIMEOUT':>11} | {'N/A':>7} | {'N/A':>8}\n")

    print(f"\nResultados guardados en: {results_file}")


if __name__ == '__main__':
    main()
