#!/usr/bin/env python3
import subprocess
import time
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOMAIN = os.path.join(BASE_DIR, "domainemergencias.pddl")
PROBLEMS_DIR = os.path.join(BASE_DIR, "problems")
RESULTS_DIR = os.path.join(BASE_DIR, "results")
TIMEOUT = 60  
SUMMARY_FILE = os.path.join(RESULTS_DIR, "summary.txt")
PYPERPLAN= "pyperplan"
#PYPERPLAN = os.path.expanduser("~/planutils-venv/bin/pyperplan")
summary_lines = []

def log(text=""):
    print(text)
    summary_lines.append(text)

def save_summary():
    with open(SUMMARY_FILE, 'w', encoding='utf-8') as f:
        f.write("\n".join(summary_lines))
    print(f"\n Resumen guardado en: {SUMMARY_FILE}")

def run_pyperplan(domain, problem, search, heuristic=None, timeout=TIMEOUT, save_plan_to=None):
    cmd = [PYPERPLAN]
    if heuristic: cmd.extend(["-H", heuristic])
    cmd.extend(["-s", search, domain, problem])
    plan_file = problem + ".soln"
    if os.path.exists(plan_file):
        try: os.remove(plan_file)
        except OSError: pass

    start = time.time()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=os.path.dirname(problem))
        elapsed = time.time() - start
        plan_length = 0
        
        if os.path.exists(plan_file):
            with open(plan_file) as f:
                plan_lines = [l.strip() for l in f.read().split('\n') if l.strip() and not l.startswith(";")]
                plan_length = len(plan_lines)
            if save_plan_to and plan_lines:
                os.makedirs(os.path.dirname(save_plan_to), exist_ok=True)
                with open(save_plan_to, 'w') as f:
                    for line in plan_lines:
                        action = line.strip().upper()
                        if action.startswith('('): action = action[1:-1].strip()
                        f.write(f"( {action} )\n")
            try: os.remove(plan_file)
            except OSError: pass
        return {"solved": plan_length > 0, "time": round(elapsed, 3), "plan_length": plan_length}
    except subprocess.TimeoutExpired:
        if os.path.exists(plan_file):
            try: os.remove(plan_file)
            except OSError: pass
        return {"solved": False, "time": timeout, "plan_length": 0}
    except Exception as e:
        return {"solved": False, "time": 0, "plan_length": 0}

def find_max_solvable(domain, sizes, search, heuristic, timeout=TIMEOUT):
    max_size = 0
    for size in sizes:
        problem = os.path.join(PROBLEMS_DIR, f"problem_size{size}.pddl")
        if not os.path.exists(problem): continue
        res = run_pyperplan(domain, problem, search, heuristic, timeout)
        if res["solved"]: max_size = size
        else: break
    return max_size

def print_markdown_table(headers, rows):
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    header_line = "| " + " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers)) + " |"
    sep_line = "| " + " | ".join("-" * col_widths[i] for i in range(len(headers))) + " |"
    log(header_line)
    log(sep_line)
    for row in rows: log("| " + " | ".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row)) + " |")

def parte2(sizes, gbfs_max):
    log(f"\n\n{'=' * 70}\nPARTE 2 (Ej 1.3.2): Heurísticas para planificadores satisficing\n{'=' * 70}")
    parte2_dir = os.path.join(RESULTS_DIR, "parte2")
    os.makedirs(parte2_dir, exist_ok=True)
    problem_file = os.path.join(PROBLEMS_DIR, f"problem_size{gbfs_max}.pddl")
    log(f"\nUsando problema de tamaño {gbfs_max}: {problem_file}")

    configs = [
        ("gbf", "hmax", "GBFS+hMAX", "GBFS_hMAX"), ("gbf", "hadd", "GBFS+hADD", "GBFS_hADD"),
        ("gbf", "hff", "GBFS+hFF", "GBFS_hFF"), ("gbf", "landmark", "GBFS+Landmark", "GBFS_Landmark"),
        ("ehs", "hmax", "EHC+hMAX", "EHC_hMAX"), ("ehs", "hadd", "EHC+hADD", "EHC_hADD"),
        ("ehs", "hff", "EHC+hFF", "EHC_hFF"), ("ehs", "landmark", "EHC+Landmark", "EHC_Landmark"),
    ]
    rows = []
    for search, heuristic, label, folder_name in configs:
        print(f"  {label}...", end=" ", flush=True)
        output_dir = os.path.join(parte2_dir, folder_name)
        os.makedirs(output_dir, exist_ok=True)
        res = run_pyperplan(DOMAIN, problem_file, search, heuristic, save_plan_to=os.path.join(output_dir, f"problem_size{gbfs_max}.pddl.plan"))
        if res["solved"]:
            print(f" {res['time']}s, plan={res['plan_length']}")
            rows.append([label, res["time"], res["plan_length"]])
        else:
            reason = "TIMEOUT" if res["time"] >= TIMEOUT else "FALLO"
            print(f" {reason}")
            rows.append([label, reason, "-"])
    print_markdown_table(["Algoritmo+Heurística", "Tiempo (s)", "Acciones Plan"], rows)

def parte3(sizes, astar_max):
    log(f"\n\n{'=' * 70}\nPARTE 3 (Ej 1.3.3): Heurísticas para planificadores óptimos\n{'=' * 70}")
    parte3_dir = os.path.join(RESULTS_DIR, "parte3")
    os.makedirs(parte3_dir, exist_ok=True)
    problem_file = os.path.join(PROBLEMS_DIR, f"problem_size{astar_max}.pddl")
    log(f"Problema a resolver: tamaño {astar_max}\n")

    configs = [
        ("bfs", None, "BFS", "BFS"), ("ids", None, "IDS", "IDS"),
        ("astar", "hmax", "A*+hMAX", "Astar_hMAX"), ("astar", "lmcut", "A*+lmcut", "Astar_lmcut"),
    ]
    rows = []
    for search, heuristic, label, folder_name in configs:
        print(f"  {label}...", end=" ", flush=True)
        output_dir = os.path.join(parte3_dir, folder_name)
        os.makedirs(output_dir, exist_ok=True)
        res = run_pyperplan(DOMAIN, problem_file, search, heuristic, save_plan_to=os.path.join(output_dir, f"problem_size{astar_max}.pddl.plan"))
        if res["solved"]:
            print(f" {res['time']}s")
            rows.append([label, res["time"], res["plan_length"], "Sí"])
        else:
            print(f" FALLO/TIMEOUT")
            rows.append([label, "TIMEOUT", "-", "-"])
    print_markdown_table(["Algoritmo", "Tiempo (s)", "Acciones Plan", "Solución Óptima"], rows)

def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    sizes = list(range(1, 31))
    
    subprocess.run([sys.executable, os.path.join(BASE_DIR, "generate_problems.py")])

    print("Calculando topes máximos")
    gbfs_max = find_max_solvable(DOMAIN, sizes, "gbf", "hmax")
    astar_max = find_max_solvable(DOMAIN, sizes, "astar", "hmax")
    gbfs_max = max(1, gbfs_max)
    astar_max = max(1, astar_max)

    parte2(sizes, gbfs_max)
    parte3(sizes, astar_max)
    save_summary()
    print(" Benchmark completado.")

if __name__ == "__main__":
    main()