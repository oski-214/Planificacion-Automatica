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

PROBLEMS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "problems")
CONTENT_TYPES = ["comida", "medicina"]
CARRIER_CAPACITY = 4
MIN_SIZE = 1
MAX_SIZE = 30

def setup_content_types(num_crates, num_persons, num_goals):
    max_attempts = 100
    for _ in range(max_attempts):
        num_crates_with_contents = [0 for _ in CONTENT_TYPES]
        for _ in range(num_crates):
            num_crates_with_contents[random.randint(0, len(CONTENT_TYPES) - 1)] += 1
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
    need = [[False for _ in range(len(CONTENT_TYPES))] for _ in range(num_persons)]
    goals_per_contents = [0 for _ in range(len(CONTENT_TYPES))]
    
    # Lista de todas las posibles combinaciones (persona, contenido) para asegurar aleatoriedad real sin repetir
    possible_goals = [(p, c) for p in range(num_persons) for c in range(len(CONTENT_TYPES))]
    random.shuffle(possible_goals)

    goals_generated = 0
    for p, c in possible_goals:
        if goals_generated >= num_goals:
            break
        if goals_per_contents[c] < len(crates_with_contents[c]):
            need[p][c] = True
            goals_per_contents[c] += 1
            goals_generated += 1
    return need

def generate_problem(size, output_dir, verbose=False):
    num_drones, num_carriers = 1, 1
    num_locations = num_persons = num_crates = num_goals = size

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
        f.write(f"(define (problem {problem_name})\n(:domain emergencias)\n(:objects\n")
        f.write("\t" + " ".join(drones) + " - dron\n\t" + " ".join(locations) + " - location\n")
        f.write("\t" + " ".join(crates) + " - box\n\t" + " ".join(CONTENT_TYPES) + " - bcontent\n")
        f.write("\t" + " ".join(persons) + " - person\n\t" + " ".join(carriers) + " - carrier\n")
        f.write("\t" + " ".join(nums) + " - num\n)\n\n(:init\n")

        for x in range(CARRIER_CAPACITY):
            f.write(f"\t(siguiente n{x} n{x+1})\n")

        for d in drones:
            f.write(f"\t(at-dron {d} deposito)\n\t(free {d})\n")

        for c in carriers:
            f.write(f"\t(at-carrier {c} deposito)\n\t(boxes-in-carrier {c} n0)\n")

        for content_index, crate_list in enumerate(crates_with_contents):
            for c in crate_list:
                f.write(f"\t(at-box {c} deposito)\n\t(box-has {c} {CONTENT_TYPES[content_index]})\n")

        for p in persons:
            f.write(f"\t(at-person {p} {random.choice(locations[1:])})\n")

        f.write(")\n\n(:goal (and\n")
        for p_idx in range(num_persons):
            for c_idx in range(len(CONTENT_TYPES)):
                if need[p_idx][c_idx]:
                    f.write(f"\t(person-has {persons[p_idx]} {CONTENT_TYPES[c_idx]})\n")
        f.write("))\n)\n")

    return filepath

def main():
    os.makedirs(PROBLEMS_DIR, exist_ok=True)
    generated = []
    for size in range(MIN_SIZE, MAX_SIZE + 1):
        generated.append(generate_problem(size, PROBLEMS_DIR, verbose=True))
    print(f"\n✅ Generados {len(generated)} problemas aleatorios sin 'need' en {PROBLEMS_DIR}/")

if __name__ == '__main__':
    main()