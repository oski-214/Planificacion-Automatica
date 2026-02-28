#!/usr/bin/env python3

########################################################################################
# Problem instance generator for emergencies drones domain.
# Based on the Linköping University TDDD48 2021 course.
# https://www.ida.liu.se/~TDDD48/labs/2021/lab1/index.en.shtml
#
# Genera problemas de tamaño creciente para benchmark de algoritmos BFS, IDS, A*, GBFS
########################################################################################

import random
import math
import os
import sys

########################################################################################
# Configuración
########################################################################################

# Directorio donde se guardarán los problemas
PROBLEMS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "problems")

# Tipos de contenido disponibles
CONTENT_TYPES = ["comida", "medicina"]

# Rango de tamaños a generar (de MIN_SIZE a MAX_SIZE inclusive)
MIN_SIZE = 1
MAX_SIZE = 30

# Semilla eliminada - ahora los resultados serán diferentes en cada ejecución

########################################################################################
# Helper functions
########################################################################################

def setup_content_types(num_crates, num_persons, num_goals, verbose=False):
    """
    Distribuye las cajas entre los tipos de contenido de forma ALEATORIA.
    Retorna una lista de listas: crates_with_contents[content_index] = [box_names]
    """
    max_attempts = 100
    for _ in range(max_attempts):
        num_crates_with_contents = [0 for _ in CONTENT_TYPES]
        
        # Asignar cada caja a un tipo de contenido aleatorio
        for _ in range(num_crates):
            rand_type = random.randint(0, len(CONTENT_TYPES) - 1)
            num_crates_with_contents[rand_type] += 1

        # Verificar que se pueden satisfacer los goals
        maxgoals = sum(min(num_crates_type, num_persons) for num_crates_type in num_crates_with_contents)
        if num_goals <= maxgoals:
            break

    if verbose:
        print("  Tipos\tCantidades")
        for x in range(len(num_crates_with_contents)):
            if num_crates_with_contents[x] > 0:
                print(f"  {CONTENT_TYPES[x]}\t {num_crates_with_contents[x]}")

    # Crear lista de cajas con su contenido
    crates_with_contents = []
    counter = 1
    for x in range(len(CONTENT_TYPES)):
        crates = []
        for y in range(num_crates_with_contents[x]):
            crates.append("box" + str(counter))
            counter += 1
        crates_with_contents.append(crates)

    return crates_with_contents

def setup_person_needs(num_persons, num_goals, crates_with_contents):
    """
    Asigna necesidades a las personas de forma aleatoria.
    Retorna una matriz need[person_index][content_index] = True/False
    """
    need = [[False for _ in range(len(CONTENT_TYPES))] for _ in range(num_persons)]
    goals_per_contents = [0 for _ in range(len(CONTENT_TYPES))]

    goals_generated = 0
    max_attempts = num_goals * 100  # Evitar bucle infinito
    
    for _ in range(max_attempts):
        if goals_generated >= num_goals:
            break
            
        rand_person = random.randint(0, num_persons - 1)
        rand_content = random.randint(0, len(CONTENT_TYPES) - 1)
        
        if (goals_per_contents[rand_content] < len(crates_with_contents[rand_content])
                and not need[rand_person][rand_content]):
            need[rand_person][rand_content] = True
            goals_per_contents[rand_content] += 1
            goals_generated += 1
    
    return need


def generate_problem(size, output_dir, verbose=False):
    """
    Genera un problema PDDL de tamaño 'size'.
    El tamaño determina: locations, persons, crates, y goals.
    """
    # Configuración del problema basada en el tamaño
    num_drones = 1
    num_locations = size
    num_persons = size
    num_crates = size
    num_goals = size  # Cada persona necesita algo

    if verbose:
        print(f"\nGenerando problema size={size}:")
        print(f"  Drones: {num_drones}, Locations: {num_locations}, Persons: {num_persons}, Crates: {num_crates}, Goals: {num_goals}")

    # Crear listas de objetos
    drones = [f"dron{x+1}" for x in range(num_drones)]
    grips = []
    for d in drones:
        grips.append(f"{d}-izq")
        grips.append(f"{d}-der")
    
    locations = ["deposito"] + [f"refugio{x+1}" for x in range(num_locations)]
    persons = [f"person{x+1}" for x in range(num_persons)]
    crates = [f"box{x+1}" for x in range(num_crates)]

    # Distribuir contenidos
    crates_with_contents = setup_content_types(num_crates, num_persons, num_goals, verbose)
    
    # Asignar necesidades
    need = setup_person_needs(num_persons, num_goals, crates_with_contents)

    # Nombre del archivo
    problem_name = f"problem_size{size}"
    filepath = os.path.join(output_dir, f"{problem_name}.pddl")

    with open(filepath, 'w') as f:
        f.write(f"(define (problem {problem_name})\n")
        f.write("(:domain emergencias)\n")
        f.write("(:objects\n")

        # Objetos
        f.write("\t" + " ".join(drones) + " - dron\n")
        f.write("\t" + " ".join(locations) + " - location\n")
        f.write("\t" + " ".join(crates) + " - box\n")
        f.write("\t" + " ".join(CONTENT_TYPES) + " - bcontent\n")
        f.write("\t" + " ".join(persons) + " - person\n")
        f.write("\t" + " ".join(grips) + " - grip\n")
        f.write(")\n\n")

        # Estado inicial
        f.write("(:init\n")

        # Drones en el deposito
        for d in drones:
            f.write(f"\t(at-dron {d} deposito)\n")

        # Brazos libres
        for g in grips:
            f.write(f"\t(free {g})\n")

        # Cajas en deposito y su contenido
        for content_index, crate_list in enumerate(crates_with_contents):
            for c in crate_list:
                f.write(f"\t(at-box {c} deposito)\n")
                f.write(f"\t(box-has {c} {CONTENT_TYPES[content_index]})\n")

        # Personas en localizaciones aleatorias (no en deposito)
        for p in persons:
            rand_loc = random.choice(locations[1:])  # Omite el deposito
            f.write(f"\t(at-person {p} {rand_loc})\n")

        f.write(")\n\n")

        # Metas: necesidades satisfechas
        f.write("(:goal (and\n")
        for person_idx in range(num_persons):
            for content_idx in range(len(CONTENT_TYPES)):
                if need[person_idx][content_idx]:
                    f.write(f"\t(person-has {persons[person_idx]} {CONTENT_TYPES[content_idx]})\n")

        f.write("))\n")
        f.write(")\n")

    return filepath


########################################################################################
# Main program
########################################################################################

def main():
    # Crear directorio de problemas si no existe
    os.makedirs(PROBLEMS_DIR, exist_ok=True)
    
    print("=" * 60)
    print("Generador de Problemas para Benchmark")
    print("=" * 60)
    print(f"Directorio de salida: {PROBLEMS_DIR}")
    print(f"Rango de tamaños: {MIN_SIZE} a {MAX_SIZE}")
    print("=" * 60)
    
    generated_files = []
    
    for size in range(MIN_SIZE, MAX_SIZE + 1):
        filepath = generate_problem(size, PROBLEMS_DIR, verbose=True)
        generated_files.append(filepath)
    
    print("\n" + "=" * 60)
    print(f"✅ Generados {len(generated_files)} problemas en {PROBLEMS_DIR}/")
    print("=" * 60)
    print("\nArchivos generados:")
    for f in generated_files[:5]:
        print(f"  - {os.path.basename(f)}")
    if len(generated_files) > 5:
        print(f"  ... y {len(generated_files) - 5} más")
    
    print(f"\nListo para ejecutar: python3 benchmark.py")


if __name__ == '__main__':
    main()