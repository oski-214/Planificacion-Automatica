#!/usr/bin/env python3
import subprocess
import os
import time

# --- CONFIGURACIÓN ---
PLANNER_EXE = "./downward.sif"
DOMAIN = "domainemergencias_costs.pddl"
PROBLEMS_DIR = "problems2" 
TIMEOUT = 60
OUTPUT_FILE = "resultados_benchmark.txt"

ALIA_SAT = ["metric-ff", "lama-first", "seq-sat-fdss-2", "seq-sat-fd-autotune-2"]
ALIA_OPT = ["seq-opt-lmcut", "seq-opt-bjolp", "seq-opt-fdss-2"]

def run_planner(problem_path, alias):
    abs_problem = os.path.abspath(problem_path)
    abs_domain = os.path.abspath(DOMAIN)

    # 1. Decidimos el comando según el alias
    if alias == "metric-ff":
        # Usamos planutils para Metric-FF
        cmd = f"planutils run metric-ff {abs_domain} {abs_problem}"
    else:
        # Usamos tu ejecutable .sif para los alias de Downward
        cmd = f"{PLANNER_EXE} --alias {alias} --overall-time-limit {TIMEOUT}s {abs_domain} {abs_problem}"
    
    try:
        # 2. Ejecutamos capturando TODO (salida estándar y errores)
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=TIMEOUT + 10)
        output = (result.stdout or "") + (result.stderr or "")
        
        success = False
        cost = "n/a"

        # 3. Lógica de detección de éxito según el planificador
        if alias == "metric-ff":
            if "found legal plan" in output:
                success = True
                if "plan cost:" in output:
                    # Extraemos el coste (ej: plan cost: 10.000 -> 10)
                    cost = output.split("plan cost:")[1].split("\n")[0].strip().split(".")[0]
        else:
            if "Solution found" in output or "Plan cost:" in output:
                success = True
                if "Plan cost: " in output:
                    cost = output.split("Plan cost: ")[1].split("\n")[0].strip()
        
        return success, cost

    except subprocess.TimeoutExpired:
        return False, "TIMEOUT"
    except Exception:
        return False, "ERROR"

def benchmark(title, aliases, file_handle):
    header = f"\n--- {title} ---\n"
    table_header = f"{'Alias':<25} | {'Size':<5} | {'Coste':<10}\n"
    separator = "-" * 45 + "\n"
    
    print(header + table_header + separator, end="")
    file_handle.write(header + table_header + separator)
    
    for alias in aliases:
        best_size = 0
        last_cost = "n/a"
        
        for size in range(1, 31):
            prob_file = os.path.join(PROBLEMS_DIR, f"problem_size{size}.pddl")
            if not os.path.exists(prob_file): break
            
            success, cost = run_planner(prob_file, alias)
            if success:
                best_size = size
                last_cost = cost
            else:
                break
        
        line = f"{alias:<25} | {best_size:<5} | {last_cost:<10}\n"
        print(line, end="")
        file_handle.write(line)

if __name__ == "__main__":
    with open(OUTPUT_FILE, "w") as f:
        f.write(f"BENCHMARK PDDL - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        benchmark("EJERCICIO 9: SATISFACCIÓN", ALIA_SAT, f)
        benchmark("EJERCICIO 10: ÓPTIMOS", ALIA_OPT, f)
    
    print(f"\n✅ Resultados guardados en: {OUTPUT_FILE}")