#!/usr/bin/env python3
"""
Benchmark para el Ejercicio 1.2
Genera problemas de complejidad creciente y prueba con FF planner.
Crea una gráfica cruzando tamaño de problema vs tiempo de solución.

Uso:
    python3 benchmark_grafica.py
"""

import subprocess
import time
import os
import sys
import signal

# Intentar importar matplotlib
try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("⚠ matplotlib no instalado. Instalar con: pip install matplotlib --break-system-packages")

# ─── Configuración ───────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOMAIN = os.path.join(BASE_DIR, "domainemergencias.pddl")
PROBLEMS_DIR = os.path.join(BASE_DIR, "problems_benchmark")
PLANUTILS_VENV = "/home/oscar/planutils-venv/bin/activate"
TIMEOUT = 60  # segundos (1 minuto)
START_SIZE = 1  # Tamaño mínimo (el generador falla con 1)
MAX_SIZE = 500  # Límite superior para evitar bucle infinito


def generate_problem(n):
    """
    Genera un problema de tamaño n usando generate-problem.py
    Retorna la ruta al archivo generado o None si falla.
    """
    problem_name = f"drone_problem_d1_l{n}_p{n}_c{n}_g{n}.pddl"
    problem_path = os.path.join(PROBLEMS_DIR, problem_name)
    
    # Si ya existe, usarlo
    if os.path.exists(problem_path):
        return problem_path
    
    try:
        process = subprocess.Popen(
            ["python3", os.path.join(BASE_DIR, "generate-problem.py")],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=BASE_DIR
        )
        stdout, stderr = process.communicate(input=str(n), timeout=30)
        
        if process.returncode != 0:
            print(f"Error generando problema: {stderr}")
            return None
        
        # Mover archivo generado al directorio de benchmark
        generated_file = os.path.join(BASE_DIR, problem_name)
        if os.path.exists(generated_file):
            os.rename(generated_file, problem_path)
            return problem_path
        else:
            return None
            
    except Exception as e:
        print(f"Excepción generando problema: {e}")
        return None


def run_ff_planner(domain, problem, timeout):
    """
    Ejecuta FF planner y retorna (tiempo_real, tiempo_ff, resuelto).
    """
    cmd = f"source {PLANUTILS_VENV} && planutils run ff {domain} {problem}"
    
    start = time.time()
    try:
        process = subprocess.Popen(
            cmd,
            shell=True,
            executable="/bin/bash",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            preexec_fn=os.setsid
        )
        
        stdout, stderr = process.communicate(timeout=timeout)
        elapsed = time.time() - start
        
        # Verificar si encontró solución
        if "found legal plan" in stdout:
            # Extraer tiempo reportado por FF
            ff_time = elapsed
            for line in stdout.split('\n'):
                if 'seconds total time' in line:
                    try:
                        ff_time = float(line.split()[0])
                    except:
                        pass
            return elapsed, ff_time, True
        else:
            return elapsed, None, False
            
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(process.pid), signal.SIGKILL)
        except:
            process.kill()
        process.wait()
        return timeout, None, False
    except Exception as e:
        print(f"Excepción: {e}")
        return None, None, False


def create_graph(results, max_solved):
    """Crea y guarda la gráfica de benchmark."""
    sizes = [r[0] for r in results]
    times = [r[1] for r in results]
    solved = [r[2] for r in results]
    
    plt.figure(figsize=(14, 8))
    
    # Datos resueltos vs timeout
    solved_sizes = [s for s, t, sol in results if sol]
    solved_times = [t for s, t, sol in results if sol]
    timeout_sizes = [s for s, t, sol in results if not sol]
    timeout_times = [t for s, t, sol in results if not sol]
    
    # Graficar
    plt.plot(solved_sizes, solved_times, 'b-o', linewidth=2, markersize=8, 
             label='Resuelto', zorder=3)
    
    if timeout_sizes:
        plt.scatter(timeout_sizes, timeout_times, color='red', s=150, marker='x', 
                   linewidths=3, label=f'Timeout (>{TIMEOUT}s)', zorder=5)
    
    # Línea de timeout
    plt.axhline(y=TIMEOUT, color='r', linestyle='--', alpha=0.7, 
                label=f'Límite de tiempo ({TIMEOUT}s)')
    
    # Marcar máximo resuelto
    if solved_sizes:
        max_idx = solved_sizes.index(max_solved)
        max_time = solved_times[max_idx]
        plt.annotate(f'Máximo resuelto:\nn = {max_solved}\n({max_time:.2f}s)', 
                     xy=(max_solved, max_time),
                     xytext=(max_solved - len(sizes)//4-2, max_time + 8),
                     fontsize=11,
                     arrowprops=dict(arrowstyle='->', color='green', lw=2),
                     bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgreen', alpha=0.9))
    
    plt.xlabel('Tamaño del problema (n = locations = persons = crates = goals)', fontsize=12)
    plt.ylabel('Tiempo (segundos)', fontsize=12)
    plt.title('FF Planner: Tamaño del problema vs Tiempo de resolución\n' +
              f'(1 dron, 0 carriers, timeout = {TIMEOUT}s)', fontsize=14)
    plt.legend(loc='upper left', fontsize=11)
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Guardar
    output_png = os.path.join(BASE_DIR, "benchmark_results.png")
    output_pdf = os.path.join(BASE_DIR, "benchmark_results.pdf")
    plt.savefig(output_png, dpi=150, bbox_inches='tight')
    plt.savefig(output_pdf, bbox_inches='tight')
    print(f"\n📊 Gráficas guardadas:")
    print(f"   - {output_png}")
    print(f"   - {output_pdf}")
    
    try:
        plt.show()
    except:
        pass


def main():
    # Verificar matplotlib
    if not HAS_MATPLOTLIB:
        print("❌ matplotlib necesario para gráficas")
        print("   Instalar con: pip install matplotlib --break-system-packages")
        sys.exit(1)
    
    # Crear directorio
    os.makedirs(PROBLEMS_DIR, exist_ok=True)
    
    print("=" * 70)
    print("BENCHMARK FF PLANNER - Dominio de Emergencias con Drones")
    print("=" * 70)
    print(f"Configuración:")
    print(f"  - Timeout por problema: {TIMEOUT} segundos")
    print(f"  - Parámetros: -d 1 -r 0, y -l = -p = -c = -g = n")
    print(f"  - Problemas generados con: generate-problem.py")
    print("=" * 70)
    
    results = []  # [(size, time, solved), ...]
    max_solved_size = 0
    
    size = START_SIZE
    while size <= MAX_SIZE:
        print(f"\n[Tamaño {size:3d}] ", end="", flush=True)
        
        # Generar problema
        print("Generando... ", end="", flush=True)
        problem_file = generate_problem(size)
        
        if problem_file is None:
            print("❌ Error generando problema")
            size += 1
            continue
        
        # Ejecutar FF
        print("FF... ", end="", flush=True)
        wall_time, ff_time, solved = run_ff_planner(DOMAIN, problem_file, TIMEOUT)
        
        if solved:
            results.append((size, wall_time, True))
            max_solved_size = size
            print(f"✅ {wall_time:.3f}s")
            size += 1
        else:
            results.append((size, TIMEOUT, False))
            print(f"❌ TIMEOUT (>{TIMEOUT}s)")
            print(f"\n{'=' * 70}")
            print(f"⏱  LÍMITE ALCANZADO en tamaño n = {size}")
            print(f"✅ MÁXIMO RESUELTO: n = {max_solved_size}")
            print(f"{'=' * 70}")
            break
    
    if size > MAX_SIZE:
        print(f"\n{'=' * 70}")
        print(f"✅ TODOS RESUELTOS hasta n = {max_solved_size}")
        print(f"   (máximo probado: {MAX_SIZE})")
        print(f"{'=' * 70}")
    
    # Tabla resumen
    print(f"\n{'=' * 60}")
    print("RESUMEN DE RESULTADOS")
    print(f"{'=' * 60}")
    print(f"{'Tamaño (n)':<15} {'Tiempo (s)':<15} {'Estado':<15}")
    print("-" * 60)
    for sz, t, sol in results:
        status = "RESUELTO" if sol else "TIMEOUT"
        print(f"{sz:<15} {t:<15.3f} {status:<15}")
    print("=" * 60)
    print(f"\n🏆 MÁXIMO TAMAÑO RESUELTO EN <{TIMEOUT}s: n = {max_solved_size}")
    
    # Gráfica
    if results:
        print("\nGenerando gráfica...")
        create_graph(results, max_solved_size)
    
    return max_solved_size


if __name__ == "__main__":
    main()
