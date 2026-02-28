#!/usr/bin/env python3

########################################################################################
# Generador de problemas PDDL para el Dominio de Emergencias
# PARTE 2 - EJERCICIO 1: Transportadores y Números
########################################################################################

from optparse import OptionParser
import random
import math
import sys

# Tipos de contenido
content_types = ["comida", "medicina"]

# Capacidad máxima del transportador (según enunciado)
CARRIER_CAPACITY = 4

def setup_content_types(options):
    while True:
        num_crates_with_contents = [0 for _ in content_types]
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

def main():
    parser = OptionParser(usage='python generate-problem.py [-help] options...')
    parser.add_option('-d', '--drones', type=int, dest='drones', default=1)
    parser.add_option('-r', '--carriers', type=int, dest='carriers', default=1)
    parser.add_option('-l', '--locations', type=int, dest='locations')
    parser.add_option('-p', '--persons', type=int, dest='persons')
    parser.add_option('-c', '--crates', type=int, dest='crates')
    parser.add_option('-g', '--goals', type=int, dest='goals')

    (options, args) = parser.parse_args()

    # Comprobación manual de argumentos obligatorios
    if None in [options.locations, options.persons, options.crates, options.goals]:
        print("Error: Faltan argumentos obligatorios. Debes especificar -l, -p, -c y -g.")
        sys.exit(1)

    # Inicializar listas de objetos
    drone, person, crate, location, carrier, num = [], [], [], [], [], []

    location.append("deposito")
    for x in range(options.locations):
        location.append("refugio" + str(x + 1))
        
    for x in range(options.drones):
        drone.append("dron" + str(x + 1))
        
    for x in range(options.carriers):
        carrier.append("carrier" + str(x + 1))
        
    for x in range(options.persons):
        person.append("person" + str(x + 1))
        
    for x in range(options.crates):
        crate.append("box" + str(x + 1))
        
    # Números del 0 a la capacidad del transportador
    for x in range(CARRIER_CAPACITY + 1):
        num.append("n" + str(x))

    crates_with_contents = setup_content_types(options)
    need = setup_person_needs(options, crates_with_contents)

    problem_name = f"drone_problem_d{options.drones}_carr{options.carriers}_l{options.locations}_p{options.persons}_c{options.crates}_g{options.goals}"

    with open(problem_name + ".pddl", 'w') as f:
        f.write(f"(define (problem {problem_name})\n")
        f.write("(:domain emergencias)\n")
        f.write("(:objects\n")
        f.write("\t" + " ".join(drone) + " - dron\n")
        f.write("\t" + " ".join(location) + " - location\n")
        f.write("\t" + " ".join(crate) + " - box\n")
        f.write("\t" + " ".join(content_types) + " - bcontent\n")
        f.write("\t" + " ".join(person) + " - person\n")
        f.write("\t" + " ".join(carrier) + " - carrier\n")
        f.write("\t" + " ".join(num) + " - num\n")
        f.write(")\n\n")

        f.write("(:init\n")
        # 1. Secuencia de números
        for x in range(CARRIER_CAPACITY):
            f.write(f"\t(siguiente n{x} n{x+1})\n")

        # 2. Drones en depósito y con el brazo libre
        for d in drone:
            f.write(f"\t(at-dron {d} deposito)\n")
            f.write(f"\t(free {d})\n")

        # 3. Transportadores en depósito y vacíos (con n0 cajas)
        for c in carrier:
            f.write(f"\t(at-carrier {c} deposito)\n")
            f.write(f"\t(boxes-in-carrier {c} n0)\n")

        # 4. Cajas en depósito
        for content_index, crate_list in enumerate(crates_with_contents):
            for c in crate_list:
                f.write(f"\t(at-box {c} deposito)\n")
                f.write(f"\t(box-has {c} {content_types[content_index]})\n")

        # 5. Personas
        for p in person:
            rand_loc = random.choice(location[1:]) 
            f.write(f"\t(at-person {p} {rand_loc})\n")

        # 6. Necesidades
        for x in range(options.persons):
            for y in range(len(content_types)):
                if need[x][y]:
                    f.write(f"\t(need {person[x]} {content_types[y]})\n")

        f.write(")\n\n")

        f.write("(:goal (and\n")
        for x in range(options.persons):
            for y in range(len(content_types)):
                if need[x][y]:
                    f.write(f"\t(person-has {person[x]} {content_types[y]})\n")
        f.write("))\n")
        f.write(")\n")
        
        print(f"\nGenerado archivo: {problem_name}.pddl")

if __name__ == '__main__':
    main()