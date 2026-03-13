#!/usr/bin/env python3
"""
Benchmark para Optic: modo anytime.

Para cada numero de drones/transportadores (1..5), genera problemas de tamano
creciente (incrementando goals de 1 en 1) y encuentra el mayor que Optic
resuelve en <= 1 minuto. Para cada problema resuelto, extrae la primera y la
ultima solucion encontrada en ese minuto y compara pasos y duracion.
"""

import os
import sys
import subprocess
import re
import glob
import shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generate_problem_temporal import generate_problem

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OPTIC = os.path.join(BASE_DIR, "optic-clp")
DOMAIN = os.path.join(BASE_DIR, "domainemergencias_temporal.pddl")
PROBLEMS_DIR = os.path.join(BASE_DIR, "problems")
PLANS_DIR = os.path.join(BASE_DIR, "plans")
RESULTS_DIR = os.path.join(BASE_DIR, "results")
TIMEOUT = 60  # 1 minuto


def parse_optic_solutions(output):
    """Extrae todas las soluciones del output anytime de Optic.
    Devuelve una lista de dicts con metricas de cada solucion encontrada."""

    solutions = []

    # Patron para detectar bloques de solucion de Optic
    # Formato: ; Time X.XX seguido de lineas de acciones T.TTT: (ACTION) [D.DDD]
    plan_pattern = re.compile(
        r"; (?:Plan found with metric|Cost:)\s+([\d.]+).*?"
        r"; (?:Time)\s+([\d.]+)\s*\n"
        r"((?:\d+\.\d+:\s+\(.+?\)\s+\[\d+\.\d+\]\s*\n)+)",
        re.DOTALL
    )

    for m in plan_pattern.finditer(output):
        metric = float(m.group(1))
        cpu_time = float(m.group(2))
        actions_block = m.group(3).strip()
        num_actions = len(actions_block.split("\n"))

        # Duracion = max(start_time + duration) de las acciones
        max_end = 0.0
        for action_line in actions_block.split("\n"):
            am = re.match(r"([\d.]+):\s+\(.+?\)\s+\[([\d.]+)\]", action_line.strip())
            if am:
                end_time = float(am.group(1)) + float(am.group(2))
                if end_time > max_end:
                    max_end = end_time

        solutions.append({
            "metric": metric,
            "cpu_time": cpu_time,
            "actions": num_actions,
            "duration": max_end,
            "plan": actions_block
        })

    return solutions


def run_optic(domain_file, problem_file, timeout=60, n_drones=1):
    """Ejecuta Optic en modo anytime y devuelve primera y ultima solucion."""

    plans_subdir = os.path.join(PLANS_DIR, f"{n_drones}_drones")
    os.makedirs(plans_subdir, exist_ok=True)

    cmd = [OPTIC, domain_file, problem_file]

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout,
            cwd=plans_subdir
        )
        output = result.stdout + result.stderr
    except subprocess.TimeoutExpired as e:
        # Optic fue cortado por timeout - capturar el output parcial
        output = ""
        if e.stdout:
            output += e.stdout if isinstance(e.stdout, str) else e.stdout.decode(errors="replace")
        if e.stderr:
            output += e.stderr if isinstance(e.stderr, str) else e.stderr.decode(errors="replace")

    solutions = parse_optic_solutions(output)

    if not solutions:
        return {"solved": False}

    first = solutions[0]
    last = solutions[-1]

    # Guardar primer y ultimo plan
    prob_basename = os.path.basename(problem_file).replace(".pddl", "")
    if first["plan"]:
        with open(os.path.join(plans_subdir, f"{prob_basename}_first.SOL"), "w") as f:
            f.write(f"; Primera solucion - Metric: {first['metric']}, Time: {first['cpu_time']}s\n")
            f.write(f"; Actions: {first['actions']}, Duration: {first['duration']}\n\n")
            f.write(first["plan"] + "\n")
    if last["plan"] and len(solutions) > 1:
        with open(os.path.join(plans_subdir, f"{prob_basename}_last.SOL"), "w") as f:
            f.write(f"; Ultima solucion - Metric: {last['metric']}, Time: {last['cpu_time']}s\n")
            f.write(f"; Actions: {last['actions']}, Duration: {last['duration']}\n\n")
            f.write(last["plan"] + "\n")

    return {
        "solved": True,
        "num_solutions": len(solutions),
        "first": {
            "cpu_time": first["cpu_time"],
            "actions": first["actions"],
            "duration": first["duration"],
        },
        "last": {
            "cpu_time": last["cpu_time"],
            "actions": last["actions"],
            "duration": last["duration"],
        }
    }


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
    Para un numero dado de drones/carriers, encuentra el mayor numero de
    goals que Optic puede resolver dentro del timeout.
    Incrementa de 1 en 1 como indica el enunciado.
    """
    goal_sizes = list(range(1, 15))  # 1, 2, 3, ..., 14

    all_results = []

    for goals in goal_sizes:
        prob_file = generate_and_save_problem(num_drones, num_drones, goals, seed=42)
        print(f"  Probando {num_drones} drones, {goals} goals... ", end="", flush=True)

        result = run_optic(DOMAIN, prob_file, timeout=max_timeout, n_drones=num_drones)

        if result.get("solved"):
            first = result["first"]
            last = result["last"]
            nsol = result["num_solutions"]
            print(f"OK ({nsol} sol, primera: {first['duration']:.1f}, ultima: {last['duration']:.1f})")
            all_results.append({"goals": goals, "result": result})
        else:
            print(f"TIMEOUT (>{max_timeout}s)")
            break

    return all_results


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    # Limpiar carpetas de ejecuciones anteriores
    if os.path.exists(PLANS_DIR):
        shutil.rmtree(PLANS_DIR)
    if os.path.exists(PROBLEMS_DIR):
        shutil.rmtree(PROBLEMS_DIR)

    all_data = []

    print("=" * 100)
    print("BENCHMARK OPTIC: modo anytime (primera vs ultima solucion)")
    print("=" * 100)

    for n_drones in range(1, 6):
        print(f"\n--- {n_drones} dron(es) / {n_drones} transportador(es) ---")
        drone_results = find_max_solvable(n_drones)

        if not drone_results:
            print(f"  No se pudo resolver ningun problema con {n_drones} drones.")

        all_data.append({
            "drones": n_drones,
            "results": drone_results
        })

    # Imprimir tabla comparativa
    print("\n" + "=" * 100)
    print("TABLA COMPARATIVA: Primera vs Ultima solucion (Optic anytime)")
    print("=" * 100)

    header = (f"{'Drones':>6} | {'Goals':>5} | {'#Sol':>4} | "
              f"{'Pasos 1a':>8} | {'Dur. 1a':>8} | {'T. 1a(s)':>9} | "
              f"{'Pasos Ult':>9} | {'Dur. Ult':>8} | {'T. Ult(s)':>10}")
    separator = "-" * len(header)
    print(header)
    print(separator)

    for drone_data in all_data:
        d = drone_data["drones"]
        if not drone_data["results"]:
            print(f"{d:>6} | {'N/A':>5} | {'N/A':>4} | "
                  f"{'N/A':>8} | {'N/A':>8} | {'N/A':>9} | "
                  f"{'N/A':>9} | {'N/A':>8} | {'N/A':>10}")
            continue

        for entry in drone_data["results"]:
            g = entry["goals"]
            r = entry["result"]
            nsol = r["num_solutions"]
            f1 = r["first"]
            fl = r["last"]
            print(f"{d:>6} | {g:>5} | {nsol:>4} | "
                  f"{f1['actions']:>8} | {f1['duration']:>8.1f} | {f1['cpu_time']:>9.2f} | "
                  f"{fl['actions']:>9} | {fl['duration']:>8.1f} | {fl['cpu_time']:>10.2f}")

    # Guardar resultados en archivo
    results_file = os.path.join(RESULTS_DIR, "benchmark_results.txt")
    with open(results_file, 'w') as f:
        f.write("BENCHMARK OPTIC: modo anytime (primera vs ultima solucion)\n")
        f.write("=" * 100 + "\n\n")
        f.write(header + "\n")
        f.write(separator + "\n")

        for drone_data in all_data:
            d = drone_data["drones"]
            if not drone_data["results"]:
                f.write(f"{d:>6} | {'N/A':>5} | {'N/A':>4} | "
                        f"{'N/A':>8} | {'N/A':>8} | {'N/A':>9} | "
                        f"{'N/A':>9} | {'N/A':>8} | {'N/A':>10}\n")
                continue

            for entry in drone_data["results"]:
                g = entry["goals"]
                r = entry["result"]
                nsol = r["num_solutions"]
                f1 = r["first"]
                fl = r["last"]
                f.write(f"{d:>6} | {g:>5} | {nsol:>4} | "
                        f"{f1['actions']:>8} | {f1['duration']:>8.1f} | {f1['cpu_time']:>9.2f} | "
                        f"{fl['actions']:>9} | {fl['duration']:>8.1f} | {fl['cpu_time']:>10.2f}\n")

    print(f"\nResultados guardados en: {results_file}")


if __name__ == '__main__':
    main()
