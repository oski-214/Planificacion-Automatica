#!/usr/bin/env python3

import random
import sys
import os

# CONFIGURACIÓN POR DEFECTO
NUM_DRONES = 2
NUM_CARRIERS = 2
NUM_LOCATIONS = 4
NUM_PERSONS = 4
NUM_CRATES = 8
NUM_GOALS = 4
CARRIER_CAPACITY = 4

content_types = ["comida", "medicina"]


def setup_content_types(crates, persons, goals):
    if goals > crates:
        print(f"Error: Objetivos ({goals}) > Cajas ({crates}).")
        sys.exit(1)

    while True:
        num_crates_with_contents = [0 for _ in content_types]
        for _ in range(crates):
            rand_type = random.randint(0, len(content_types) - 1)
            num_crates_with_contents[rand_type] += 1

        maxgoals = sum(min(nc, persons) for nc in num_crates_with_contents)
        if goals <= maxgoals:
            break

    crates_with_contents = []
    counter = 1
    for x in range(len(content_types)):
        crates_list = []
        for y in range(num_crates_with_contents[x]):
            crates_list.append("box" + str(counter))
            counter += 1
        crates_with_contents.append(crates_list)
    return crates_with_contents


def setup_person_needs(persons, goals, crates_with_contents):
    need = [[False for _ in range(len(content_types))] for _ in range(persons)]
    goals_per_contents = [0 for _ in range(len(content_types))]

    for _ in range(goals):
        generated = False
        attempts = 0
        while not generated and attempts < 100:
            rand_person = random.randint(0, persons - 1)
            rand_content = random.randint(0, len(content_types) - 1)

            if (goals_per_contents[rand_content] < len(crates_with_contents[rand_content])
                    and not need[rand_person][rand_content]):
                need[rand_person][rand_content] = True
                goals_per_contents[rand_content] += 1
                generated = True
            attempts += 1
    return need


def generate_problem(num_drones, num_carriers, num_locations, num_persons,
                     num_crates, num_goals, carrier_capacity, seed=None):
    if seed is not None:
        random.seed(seed)

    location = ["deposito"] + [f"refugio{x+1}" for x in range(num_locations)]
    drone = [f"dron{x+1}" for x in range(num_drones)]
    carrier = [f"carrier{x+1}" for x in range(num_carriers)]
    person = [f"person{x+1}" for x in range(num_persons)]
    num = [f"n{x}" for x in range(carrier_capacity + 1)]

    crates_with_contents = setup_content_types(num_crates, num_persons, num_goals)
    all_boxes = [box for sublist in crates_with_contents for box in sublist]
    need = setup_person_needs(num_persons, num_goals, crates_with_contents)

    problem_name = f"prob_d{num_drones}_t{num_carriers}_l{num_locations}_p{num_persons}_c{num_crates}"

    lines = []
    lines.append(f"(define (problem {problem_name})")
    lines.append("(:domain emergencias-temporal)")
    lines.append("(:objects")
    lines.append(f"\t{' '.join(drone)} - dron")
    lines.append(f"\t{' '.join(location)} - location")
    lines.append(f"\t{' '.join(all_boxes)} - box")
    lines.append(f"\t{' '.join(content_types)} - bcontent")
    lines.append(f"\t{' '.join(person)} - person")
    lines.append(f"\t{' '.join(carrier)} - carrier")
    lines.append(f"\t{' '.join(num)} - num")
    lines.append(")")
    lines.append("")
    lines.append("(:init")

    # Costes de vuelo (se mantiene fly-cost para la duración del vuelo)
    for l1 in location:
        for l2 in location:
            if l1 != l2:
                lines.append(f"\t(= (fly-cost {l1} {l2}) {random.randint(1, 20)})")

    # Números para el transportador
    for x in range(carrier_capacity):
        lines.append(f"\t(siguiente n{x} n{x+1})")

    # Drones: posición, brazo libre y mutex disponible
    for d in drone:
        lines.append(f"\t(at-dron {d} deposito)")
        lines.append(f"\t(free {d})")
        lines.append(f"\t(dron-available {d})")

    # Transportadores: posición, contador y mutex disponible
    for c in carrier:
        lines.append(f"\t(at-carrier {c} deposito)")
        lines.append(f"\t(boxes-in-carrier {c} n0)")
        lines.append(f"\t(carrier-available {c})")

    # Cajas
    for idx, crate_list in enumerate(crates_with_contents):
        for b in crate_list:
            lines.append(f"\t(at-box {b} deposito)")
            lines.append(f"\t(box-has {b} {content_types[idx]})")

    # Personas: posición y mutex disponible
    for p in person:
        lines.append(f"\t(at-person {p} {random.choice(location[1:])})")
        lines.append(f"\t(person-available {p})")

    lines.append(")")
    lines.append("")
    lines.append("(:goal (and")
    for x in range(num_persons):
        for y in range(len(content_types)):
            if need[x][y]:
                lines.append(f"\t(person-has {person[x]} {content_types[y]})")
    lines.append("))")

    lines.append("(:metric minimize (total-time))")
    lines.append(")")

    return problem_name, "\n".join(lines)


def main():
    target_dir = "problems"
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    problem_name, content = generate_problem(
        NUM_DRONES, NUM_CARRIERS, NUM_LOCATIONS, NUM_PERSONS,
        NUM_CRATES, NUM_GOALS, CARRIER_CAPACITY
    )

    file_path = os.path.join(target_dir, problem_name + ".pddl")
    with open(file_path, 'w') as f:
        f.write(content + "\n")

    print(f"Problema generado: {file_path}")


if __name__ == '__main__':
    main()
