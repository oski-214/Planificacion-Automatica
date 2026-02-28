#!/usr/bin/env python3

########################################################################################
# Problem instance generator skeleton for emergencies drones domain.
# Based on the Linköping University TDDD48 2021 course.
# https://www.ida.liu.se/~TDDD48/labs/2021/lab1/index.en.shtml
#
# COMPLETADO PARA: domainemergencias.pddl
########################################################################################

from optparse import OptionParser
import random
import math
import sys

########################################################################################
# Hard-coded options
########################################################################################

content_types = ["comida", "medicina"] # Adaptado a tu dominio (bcontent)

########################################################################################
# Helper functions (sin cambios lógicos, solo adaptación de nombres si fuera necesario)
########################################################################################

def distance(location_coords, location_num1, location_num2):
    x1 = location_coords[location_num1][0]
    y1 = location_coords[location_num1][1]
    x2 = location_coords[location_num2][0]
    y2 = location_coords[location_num2][1]
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

def flight_cost(location_coords, location_num1, location_num2):
    return int(distance(location_coords, location_num1, location_num2)) + 1

def setup_content_types(options):
    while True:
        num_crates_with_contents = [0 for _ in content_types]
        
        # Asignar cada caja a un tipo de contenido aleatorio
        for _ in range(options.crates):
            rand_type = random.randint(0, len(content_types) - 1)
            num_crates_with_contents[rand_type] += 1

        maxgoals = sum(min(num_crates, options.persons) for num_crates in num_crates_with_contents)

        if options.goals <= maxgoals:
            break

    print("\nTipos\tCantidades")
    for x in range(len(num_crates_with_contents)):
        if num_crates_with_contents[x] > 0:
            print(f"{content_types[x]}\t {num_crates_with_contents[x]}")

    crates_with_contents = []
    counter = 1
    for x in range(len(content_types)):
        crates = []
        for y in range(num_crates_with_contents[x]):
            crates.append("box" + str(counter))
            counter += 1
        crates_with_contents.append(crates)

    return crates_with_contents

def setup_location_coords(options):
    location_coords = [(0, 0)]  
    for x in range(1, options.locations + 1):
        location_coords.append((random.randint(1, 200), random.randint(1, 200)))
    return location_coords

def setup_person_needs(options, crates_with_contents):
    need = [[False for i in range(len(content_types))] for j in range(options.persons)]
    goals_per_contents = [0 for i in range(len(content_types))]

    for goalnum in range(options.goals):
        generated = False
        while not generated:
            rand_person = random.randint(0, options.persons - 1)
            rand_content = random.randint(0, len(content_types) - 1)
            
            if (goals_per_contents[rand_content] < len(crates_with_contents[rand_content])
                    and not need[rand_person][rand_content]):
                need[rand_person][rand_content] = True
                goals_per_contents[rand_content] += 1
                generated = True
    return need

########################################################################################
# Main program
########################################################################################

def main():
    n = int(input("Introduce un número para definir locations, persons, crates y goals: "))

    # Valores fijos
    options = type('Options', (), {
        'drones': 1,
        'carriers': 0,
        'locations': n,
        'persons': n,
        'crates': n,
        'goals': n
    })()

    print(f"Drones:\t\t{options.drones}")
    print(f"Locations:\t{options.locations}")
    print(f"Persons:\t{options.persons}")
    print(f"Crates (Boxes):\t{options.crates}")
    print(f"Goals:\t\t{options.goals}")

    # Inicializar listas
    drone, person, crate, location, grip = [], [], [], [], []

    location.append("deposito") # Donde salen las cajas
    for x in range(options.locations):
        location.append("refugio" + str(x + 1)) # Donde están las personas
    for x in range(options.drones):
        drone_name = "dron" + str(x + 1)
        drone.append(drone_name)
        # Crear 2 brazos por dron
        grip.append(f"{drone_name}-izq")
        grip.append(f"{drone_name}-der")
        
    for x in range(options.persons):
        person.append("person" + str(x + 1))
    for x in range(options.crates):
        crate.append("box" + str(x + 1))

    crates_with_contents = setup_content_types(options)
    location_coords = setup_location_coords(options)
    need = setup_person_needs(options, crates_with_contents)

    problem_name = f"drone_problem_d{options.drones}_l{options.locations}_p{options.persons}_c{options.crates}_g{options.goals}"

    with open(problem_name + ".pddl", 'w') as f:
        f.write(f"(define (problem {problem_name})\n")
        f.write("(:domain emergencias)\n") # Nombre de tu dominio
        f.write("(:objects\n")

        # --- COMPLETADO: Escritura de objetos según tu PDDL ---
        f.write("\t" + " ".join(drone) + " - dron\n")
        f.write("\t" + " ".join(location) + " - location\n")
        f.write("\t" + " ".join(crate) + " - box\n")
        f.write("\t" + " ".join(content_types) + " - bcontent\n")
        f.write("\t" + " ".join(person) + " - person\n")
        f.write("\t" + " ".join(grip) + " - grip\n")
        f.write(")\n\n")

        # --- COMPLETADO: Generación del estado inicial ---
        f.write("(:init\n")

        # Drones en el deposito
        for d in drone:
            f.write(f"\t(at-dron {d} deposito)\n")

        # Brazos libres (vinculados al dron según nuestra corrección anterior)
        # Nota: Si no cambiaste tu dominio para vincular (free ?d ?g), usa solo (free ?g)
        for g in grip:
             # Asumiendo tu versión original de dominio: (free ?g)
             f.write(f"\t(free {g})\n")

        # Cajas en deposito y su contenido
        for content_index, crate_list in enumerate(crates_with_contents):
            for c in crate_list:
                f.write(f"\t(at-box {c} deposito)\n")
                f.write(f"\t(box-has {c} {content_types[content_index]})\n")

        # Personas aleatorias en localizaciones (no deposito)
        for p in person:
            rand_loc = random.choice(location[1:]) # Omite el deposito
            f.write(f"\t(at-person {p} {rand_loc})\n")

        f.write(")\n\n")

        # --- COMPLETADO: Metas ---
        f.write("(:goal (and\n")

        # Necesidades satisfechas
        for x in range(options.persons):
            for y in range(len(content_types)):
                if need[x][y]:
                    f.write(f"\t(person-has {person[x]} {content_types[y]})\n")
                    
        # (Opcional) Puedes añadir que los drones vuelvan al deposito si tu profesor lo pide, 
        # aunque el PDF original de la práctica no lo exige explícitamente en la meta.
        # for d in drone:
        #    f.write(f"\t(at-dron {d} deposito)\n")

        f.write("))\n")
        f.write(")\n")
        print(f"\nGenerado archivo: {problem_name}.pddl")

if __name__ == '__main__':
    main()