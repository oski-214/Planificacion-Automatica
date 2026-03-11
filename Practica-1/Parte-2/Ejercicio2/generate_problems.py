#!/usr/bin/env python3

import random
import os

PROBLEMS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "problems2")
CONTENT_TYPES = ["comida", "medicina"]
CARRIER_CAPACITY = 4
MIN_SIZE = 1
MAX_SIZE = 50

def setup_content_types(num_crates, num_persons, num_goals):
    num_crates_with_contents = [0 for _ in CONTENT_TYPES]
    for _ in range(num_crates):
        num_crates_with_contents[random.randint(0, len(CONTENT_TYPES) - 1)] += 1
    
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
    possible_goals = [(p, c) for p in range(num_persons) for c in range(len(CONTENT_TYPES))]
    random.shuffle(possible_goals)

    goals_generated = 0
    for p, c in possible_goals:
        if goals_generated >= num_goals: break
        if goals_per_contents[c] < len(crates_with_contents[c]):
            need[p][c] = True
            goals_per_contents[c] += 1
            goals_generated += 1
    return need

def generate_problem(size, output_dir):
    num_locations = num_persons = num_crates = num_goals = size
    drones = ["dron1"]
    carriers = ["carrier1"]
    locations = ["deposito"] + [f"refugio{x+1}" for x in range(num_locations)]
    persons = [f"person{x+1}" for x in range(num_persons)]
    crates = [f"box{x+1}" for x in range(num_crates)]
    nums = [f"n{x}" for x in range(CARRIER_CAPACITY + 1)]

    crates_with_contents = setup_content_types(num_crates, num_persons, num_goals)
    need = setup_person_needs(num_persons, num_goals, crates_with_contents)

    problem_name = f"problem_size{size}"
    filepath = os.path.join(output_dir, f"{problem_name}.pddl")

    with open(filepath, 'w') as f:
        f.write(f"(define (problem {problem_name})\n(:domain emergencias-costs)\n(:objects\n")
        f.write("\t" + " ".join(drones) + " - dron\n\t" + " ".join(locations) + " - location\n")
        f.write("\t" + " ".join(crates) + " - box\n\t" + " ".join(CONTENT_TYPES) + " - bcontent\n")
        f.write("\t" + " ".join(persons) + " - person\n\t" + " ".join(carriers) + " - carrier\n")
        f.write("\t" + " ".join(nums) + " - num\n)\n\n(:init\n")

        # --- Costes y Funciones ---
        f.write("\t(= (total-cost) 0)\n")
        for l1 in locations:
            for l2 in locations:
                if l1 != l2:
                    cost = random.randint(1, 20)
                    f.write(f"\t(= (fly-cost {l1} {l2}) {cost})\n")

        # --- Estado Inicial ---
        for x in range(CARRIER_CAPACITY):
            f.write(f"\t(siguiente n{x} n{x+1})\n")

        f.write(f"\t(at-dron dron1 deposito)\n\t(free dron1)\n")
        f.write(f"\t(at-carrier carrier1 deposito)\n\t(boxes-in-carrier carrier1 n0)\n")

        for content_idx, crate_list in enumerate(crates_with_contents):
            for b in crate_list:
                f.write(f"\t(at-box {b} deposito)\n\t(box-has {b} {CONTENT_TYPES[content_idx]})\n")

        for p in persons:
            f.write(f"\t(at-person {p} {random.choice(locations[1:])})\n")

        f.write(")\n\n(:goal (and\n")
        for p_idx in range(num_persons):
            for c_idx in range(len(CONTENT_TYPES)):
                if need[p_idx][c_idx]:
                    f.write(f"\t(person-has {persons[p_idx]} {CONTENT_TYPES[c_idx]})\n")
        f.write("))\n")
        
        # --- Métrica de Optimización ---
        f.write("(:metric minimize (total-cost))\n)")

    return filepath

def main():
    os.makedirs(PROBLEMS_DIR, exist_ok=True)
    for size in range(MIN_SIZE, MAX_SIZE + 1):
        generate_problem(size, PROBLEMS_DIR)
    print(f"✅ Generados problemas con costes en {PROBLEMS_DIR}/")

if __name__ == '__main__':
    main()