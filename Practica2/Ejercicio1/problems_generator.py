import random

def generar_problema(n, nombre_fichero):
    tipos_contenido = ["medicina", "comida"]
    # Localizaciones de entrega (sin contar loc-base y loc-almacen)
    listado_locs = [f"loc{i}" for i in range(1, n + 1)]
    
    # Aseguramos que haya stock para cada necesidad
    necesidades = [random.choice(tipos_contenido) for _ in range(n)]
    contenidos_cajas = necesidades.copy()
    random.shuffle(contenidos_cajas)

    with open(nombre_fichero, "w") as f:
        f.write(f"(defproblem {nombre_fichero} emergencias\n")
        f.write("  (\n")
        
        # --- ESTADO INICIAL ---
        f.write("    (at-dron d1 loc-base)\n")
        f.write("    (free g1)\n")
        f.write("    (free g2)\n") # Asumiendo dos garras según lo que comentamos
        
        # Cajas en el almacén
        for i, cont in enumerate(contenidos_cajas, 1):
            f.write(f"    (at-box b{i} loc-almacen)\n")
            f.write(f"    (box-has b{i} {cont})\n")
            
        # Personas en localizaciones aleatorias
        for i, nec in enumerate(necesidades, 1):
            destino = random.choice(listado_locs)
            f.write(f"    (at-person p{i} {destino})\n")
            f.write(f"    (necesita p{i} {nec})\n")
            
        f.write("  )\n")
        
        # --- TAREA ---
        f.write("  ((enviar-todo))\n")
        f.write(")\n")

# Generar la batería de problemas
for i in range(10, 501, 10):
    generar_problema(i, f"p{i}")

print("Problemas generados.")