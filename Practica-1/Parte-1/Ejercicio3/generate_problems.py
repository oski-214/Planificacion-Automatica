#!/usr/bin/env python3
"""
Generador de problemas PDDL de tamaño creciente para el dominio de emergencias.

Cada problema de tamaño N tiene:
  - 1 dron con 2 grippers (izquierda, derecha)
  - N personas, cada una en un refugio distinto
  - N cajas, cada una con un contenido necesario por una persona
  - N+1 ubicaciones: 1 deposito + N refugios
  - 2 tipos de contenido: comida, medicina (se asignan cíclicamente)

Esto genera problemas que requieren ~ 3*N acciones (pick, move, leave por persona).
"""

import os

CONTENTS = ["comida", "medicina"]

def generate_problem(n, output_dir="."):
    """Genera un problema de tamaño n."""
    
    # Objetos
    drones = ["dron1"]
    grippers = ["izquierda", "derecha"]
    persons = [f"person{i}" for i in range(1, n + 1)]
    boxes = [f"box{i}" for i in range(1, n + 1)]
    locations = ["deposito"] + [f"refugio{i}" for i in range(1, n + 1)]
    contents = CONTENTS  # se reutilizan cíclicamente
    
    # Asignación: persona_i necesita contenido[i % len], box_i tiene ese contenido
    assignments = []
    for i in range(n):
        content = contents[i % len(contents)]
        assignments.append((persons[i], boxes[i], locations[i + 1], content))
    
    lines = []
    lines.append(f"(define (problem emergencias-size{n})")
    lines.append(f"    (:domain emergencias)")
    lines.append(f"")
    lines.append(f"    (:objects")
    lines.append(f"        {' '.join(drones)} - dron")
    lines.append(f"        {' '.join(persons)} - person")
    lines.append(f"        {' '.join(boxes)} - box")
    lines.append(f"        {' '.join(contents)} - bcontent")
    lines.append(f"        {' '.join(locations)} - location")
    lines.append(f"        {' '.join(grippers)} - grip")
    lines.append(f"    )")
    lines.append(f"")
    lines.append(f"    (:init")
    
    # Dron en deposito
    lines.append(f"        (at-dron dron1 deposito)")
    
    # Cajas en deposito
    for box in boxes:
        lines.append(f"        (at-box {box} deposito)")
    
    # Personas en refugios
    for person, box, refugio, content in assignments:
        lines.append(f"        (at-person {person} {refugio})")
    
    # Contenido de las cajas
    for person, box, refugio, content in assignments:
        lines.append(f"        (box-has {box} {content})")
    
    # Necesidades de las personas
    for person, box, refugio, content in assignments:
        lines.append(f"        (need {person} {content})")
    
    # Grippers libres
    for g in grippers:
        lines.append(f"        (free {g})")
    
    lines.append(f"    )")
    lines.append(f"")
    lines.append(f"    (:goal (and")
    for person, box, refugio, content in assignments:
        lines.append(f"        (person-has {person} {content})")
    lines.append(f"    ))")
    lines.append(f")")
    
    filename = os.path.join(output_dir, f"problem_size{n}.pddl")
    with open(filename, "w") as f:
        f.write("\n".join(lines) + "\n")
    
    print(f"Generado: {filename}  ({n} personas, {n} cajas, {n+1} ubicaciones)")
    return filename


if __name__ == "__main__":
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "problems")
    os.makedirs(output_dir, exist_ok=True)
    
    # Generar problemas de tamaño 1 a 30
    sizes = list(range(1, 31))
    
    for size in sizes:
        generate_problem(size, output_dir)
    
    print(f"\n✅ Generados {len(sizes)} problemas en {output_dir}")
