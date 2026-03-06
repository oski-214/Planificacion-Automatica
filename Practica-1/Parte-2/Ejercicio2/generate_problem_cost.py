#!/usr/bin/env python3

import random
import sys
import os

# CONFIGURACIÓN DE ARGUMENTOS DIRECTOS
NUM_DRONES = 1
NUM_CARRIERS = 1
NUM_LOCATIONS = 4   # Cantidad de refugios (sin contar el depósito)
NUM_PERSONS = 4
NUM_CRATES = 8
NUM_GOALS = 4       # Debe ser <= NUM_CRATES
CARRIER_CAPACITY = 4

# Tipos de contenido
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

        # Verificamos que la suma de cajas por tipo cubra los objetivos
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
    need = [[False for i in range(len(content_types))] for j in range(persons)]
    goals_per_contents = [0 for i in range(len(content_types))]

    for goalnum in range(goals):
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

def main():
    # Crear la carpeta problems2 si no existe
    target_dir = "problems2"
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # Inicializar listas de objetos
    location = ["deposito"] + [f"refugio{x+1}" for x in range(NUM_LOCATIONS)]
    drone = [f"dron{x+1}" for x in range(NUM_DRONES)]
    carrier = [f"carrier{x+1}" for x in range(NUM_CARRIERS)]
    person = [f"person{x+1}" for x in range(NUM_PERSONS)]
    num = [f"n{x}" for x in range(CARRIER_CAPACITY + 1)]

    crates_with_contents = setup_content_types(NUM_CRATES, NUM_PERSONS, NUM_GOALS)
    all_boxes = [box for sublist in crates_with_contents for box in sublist]
    need = setup_person_needs(NUM_PERSONS, NUM_GOALS, crates_with_contents)

    problem_name = f"prob_l{NUM_LOCATIONS}_p{NUM_PERSONS}_c{NUM_CRATES}"
    file_path = os.path.join(target_dir, problem_name + ".pddl")

    with open(file_path, 'w') as f:
        f.write(f"(define (problem {problem_name})\n")
        f.write("(:domain emergencias-costs)\n")
        f.write("(:objects\n")
        f.write(f"\t{' '.join(drone)} - dron\n")
        f.write(f"\t{' '.join(location)} - location\n")
        f.write(f"\t{' '.join(all_boxes)} - box\n")
        f.write(f"\t{' '.join(content_types)} - bcontent\n")
        f.write(f"\t{' '.join(person)} - person\n")
        f.write(f"\t{' '.join(carrier)} - carrier\n")
        f.write(f"\t{' '.join(num)} - num\n")
        f.write(")\n\n(:init\n")
        
        # 1. Costes iniciales y métrica (Ejercicio 2.2) [cite: 75, 76, 79, 80]
        f.write("\t(= (total-cost) 0)\n")
        for l1 in location:
            for l2 in location:
                if l1 != l2:
                    # Simulamos flight_cost() con valores entre 1 y 20 [cite: 84]
                    f.write(f"\t(= (fly-cost {l1} {l2}) {random.randint(1, 20)})\n")

        # 2. Números para el transportador [cite: 33, 43, 44]
        for x in range(CARRIER_CAPACITY):
            f.write(f"\t(siguiente n{x} n{x+1})\n")

        # 3. Estado de drones y transportadores [cite: 15, 16]
        for d in drone:
            f.write(f"\t(at-dron {d} deposito)\n\t(free {d})\n")
        for c in carrier:
            f.write(f"\t(at-carrier {c} deposito)\n\t(boxes-in-carrier {c} n0)\n")

        # 4. Cajas y Personas
        for idx, crate_list in enumerate(crates_with_contents):
            for b in crate_list:
                f.write(f"\t(at-box {b} deposito)\n\t(box-has {b} {content_types[idx]})\n")
        for p in person:
            # Las personas se ubican en refugios, no en el depósito
            f.write(f"\t(at-person {p} {random.choice(location[1:])})\n")

        f.write(")\n\n(:goal (and\n")
        for x in range(NUM_PERSONS):
            for y in range(len(content_types)):
                if need[x][y]:
                    f.write(f"\t(person-has {person[x]} {content_types[y]})\n")
        f.write("))\n")
        
        # 5. Métrica de minimización [cite: 85]
        f.write("(:metric minimize (total-cost))\n)\n")

    print(f"¡Hecho! Archivo guardado en: {file_path}")

if __name__ == '__main__':
    main()
