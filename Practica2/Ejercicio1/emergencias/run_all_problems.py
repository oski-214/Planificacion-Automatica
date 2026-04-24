import os
import subprocess
import re

def ejecutar_experimento():
    # 1. Configuración de rutas para Ubuntu/WSL
    base_dir = "/home/jorge/JSHOP2/JSHOP2"
    antlr_jar = os.path.join(base_dir, "jshop2-console", "antlr.jar")
    jshop_jar = os.path.join(base_dir, "jshop2-console", "JSHOP2.jar")
    
    # 2. Configurar el entorno de Java (CLASSPATH)
    classpath = f".:{antlr_jar}:{jshop_jar}"
    env = os.environ.copy()
    env["CLASSPATH"] = classpath

    # 3. Carpeta de trabajo
    dominio_dir = "/home/jorge/JSHOP2/JSHOP2/domains/emergencias"
    os.chdir(dominio_dir)

    # 4. Obtener lista de problemas
    todos_los_ficheros = os.listdir('.')
    problemas = [f for f in todos_los_ficheros if re.fullmatch(r'p\d+', f)]
    problemas.sort(key=lambda x: int(re.search(r'\d+', x).group()))

    if not problemas:
        print("No se han encontrado archivos de problema (p10, p20...)")
        return

    # Preparamos el archivo de benchmark (modo 'w' para que se limpie al empezar)
    with open("benchmark.txt", "w") as b_file:
        b_file.write(f"{'Problema':<12} | {'Tiempo Used':<12}\n")
        b_file.write("-" * 30 + "\n")

    print(f"{'Problema':<12} | {'Tiempo Used':<12}")
    print("-" * 30)

    for p in problemas:
        try:
            # Paso A y B: Compilar con JSHOP2
            subprocess.run(["java", "JSHOP2.InternalDomain", "emergencias"], env=env, check=True, capture_output=True)
            subprocess.run(["java", "JSHOP2.InternalDomain", "-r1", p], env=env, check=True, capture_output=True)

            # Paso C: Compilar Java
            subprocess.run(["javac", "emergencias.java", f"{p}.java"], env=env, check=True)

            # Paso D: Ejecutar y guardar el plan en un .txt individual
            resultado = subprocess.run(["java", p], env=env, check=True, capture_output=True, text=True)
            
            # Guardamos el contenido completo en plan_pXX.txt
            with open(f"plan_{p}.txt", "w") as plan_file:
                plan_file.write(resultado.stdout)
            
            # Extraer el tiempo
            match = re.search(r"Time Used\s*=\s*([\d\.]+)", resultado.stdout)
            tiempo = match.group(1) if match else "N/A"
            
            linea = f"{p:<12} | {tiempo:<12}"
            print(linea)
            
            # Guardar en el benchmark
            with open("benchmark.txt", "a") as b_file:
                b_file.write(linea + "\n")

        except subprocess.CalledProcessError as e:
            msg_err = f"{p:<12} | Error en ejecucion"
            print(msg_err)
            with open("benchmark.txt", "a") as b_file:
                b_file.write(msg_err + "\n")
        
        # Limpieza de archivos generados por Java (NO borramos los planes ni el benchmark)
        for f in os.listdir('.'):
            if f.endswith(".class") or f == "emergencias.java" or f == "emergencias.txt" or (f.startswith(f"{p}.") and not f.endswith(".txt")):
                try: os.remove(f)
                except: pass

if __name__ == "__main__":
    ejecutar_experimento()