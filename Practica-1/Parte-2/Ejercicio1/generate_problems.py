#!/usr/bin/env python3

########################################################################################
# Generador de problemas de tamaño creciente para benchmark.
# PARTE 2 - EJERCICIO 1: Dominio con transportadores y números.
#
# Genera problemas problem_size1.pddl ... problem_sizeN.pddl
# El tamaño determina: locations, persons, crates, goals (todos = size).
# Siempre 1 dron y 1 carrier con capacidad 4.
########################################################################################

import random
import os
import sys

# ─── Configuración ───────────────────────────────────────────────────────────
PROBLEMS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "problems")
CONTENT_TYPES = ["comida", "medicina"]
CARRIER_CAPACITY = 4
MIN_SIZE = 1
MAX_SIZE = 30


def setup_content_types(num_crates, num_persons, num_goals):
    """Distribuye las cajas entre los tipos de contenido de forma aleatoria."""
    max_attempts = 100
    for _ in range(max_attempts):
        num_crates_with_contents = [0 for _ in CONTENT_TYPES]
        for _ in range(num_crates):
            rand_type = random.randint(0, len(CONTENT_TYPES) - 1)
            num_crates_with_contents[rand_type] += 1
        maxgoals = sum(min(n, num_persons) for n in num_crates_with_contents)
        if num_goals <= maxgoals:
            break

    crates_with_contents = []
    counter = 1
    for x in range(len(CONTENT_TYPES)):
        crates = []
        for _ in range(num_crates_with_contents[x]):
            crates.append("box" + str(counter))
            counter += 1
        crates_with_contents.append(crates)
    return crates_with_contents


def setup_person_needs(num_persons, num_goals, crates_with_contents):
    """Asigna necesidades a las personas de forma aleatoria."""
    need = [[False for _ in range(len(CONTENT_TYPES))] for _ in range(num_persons)]
    goals_per_contents = [0 for _ in range(len(CONTENT_TYPES))]
    goals_generated = 0

    for _ in range(num_goals * 100):
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
    """Genera un problema PDDL de tamaño 'size' con 1 dron, 1 carrier."""
    num_drones = 1
    num_carriers = 1
    num_locations = size
    num_persons = size
    num_crates = size
    num_goals = size

    if verbose:
        print(f"  size={size}: locs={num_locations}, persons={num_persons}, "
              f"crates={num_crates}, goals={num_goals}")

    drones = [f"dron{x+1}" for x in range(num_drones)]
    carriers = [f"carrier{x+1}" for x in range(num_carriers)]
    locations = ["deposito"] + [f"refugio{x+1}" for x in range(num_locations)]
    persons = [f"person{x+1}" for x in range(num_persons)]
    crates = [f"box{x+1}" for x in range(num_crates)]
    nums = [f"n{x}" for x in range(CARRIER_CAPACITY + 1)]

    crates_with_contents = setup_content_types(num_crates, num_persons, num_goals)
    need = setup_person_needs(num_persons, num_goals, crates_with_contents)

    problem_name = f"problem_size{size}"
    filepath = os.path.join(output_dir, f"{problem_name}.pddl")

    with open(filepath, 'w') as f:
        f.write(f"(define (problem {problem_name})\n")
        f.write("(:domain emergencias)\n")
        f.write("(:objects\n")
        f.write("\t" + " ".join(drones) + " - dron\n")
        f.write("\t" + " ".join(locations) + " - location\n")
        f.write("\t" + " ".join(crates) + " - box\n")
        f.write("\t" + " ".join(CONTENT_TYPES) + " - bcontent\n")
        f.write("\t" + " ".join(persons) + " - person\n")
        f.write("\t" + " ".join(carriers) + " - carrier\n")
        f.write("\t" + " ".join(nums) + " - num\n")
        f.write(")\n\n")

        f.write("(:init\n")

        # Secuencia de números
        for x in range(CARRIER_CAPACITY):
            f.write(f"\t(siguiente n{x} n{x+1})\n")

        # Drones en depósito y con el brazo libre
        for d in drones:
            f.write(f"\t(at-dron {d} deposito)\n")
            f.write(f"\t(free {d})\n")

        # Transportadores en depósito y vacíos
        for c in carriers:
            f.write(f"\t(at-carrier {c} deposito)\n")
            f.write(f"\t(boxes-in-carrier {c} n0)\n")

        # Cajas en depósito con su contenido
        for content_index, crate_list in enumerate(crates_with_contents):
            for c in crate_list:
                f.write(f"\t(at-box {c} deposito)\n")
                f.write(f"\t(box-has {c} {CONTENT_TYPES[content_index]})\n")

        # Personas en localizaciones aleatorias (no en depósito)
        for p in persons:
            rand_loc = random.choice(locations[1:])
            f.write(f"\t(at-person {p} {rand_loc})\n")

        f.write(")\n\n")

        # Goals: person-has
        f.write("(:goal (and\n")
        for person_idx in range(num_persons):
            for content_idx in range(len(CONTENT_TYPES)):
                if need[person_idx][content_idx]:
                    f.write(f"\t(person-has {persons[person_idx]} {CONTENT_TYPES[content_idx]})\n")
        f.write("))\n")
        f.write(")\n")

    return filepath


def main():
    os.makedirs(PROBLEMS_DIR, exist_ok=True)

    print("=" * 60)
    print("Generador de Problemas - Parte 2 Ejercicio 1")
    print("=" * 60)
    print(f"Directorio: {PROBLEMS_DIR}")
    print(f"Rango: {MIN_SIZE} a {MAX_SIZE}")
    print(f"Carrier capacity: {CARRIER_CAPACITY}")
    print("=" * 60)

    generated = []
    for size in range(MIN_SIZE, MAX_SIZE + 1):
        filepath = generate_problem(size, PROBLEMS_DIR, verbose=True)
        generated.append(filepath)

    print(f"\n✅ Generados {len(generated)} problemas en {PROBLEMS_DIR}/")


if __name__ == '__main__':
    main()
