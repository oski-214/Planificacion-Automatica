(define (problem emergencias-size1)
    (:domain emergencias)

    (:objects
        dron1 - dron
        person1 - person
        box1 - box
        comida medicina - bcontent
        deposito refugio1 - location
        izquierda derecha - grip
    )

    (:init
        (at-dron dron1 deposito)
        (at-box box1 deposito)
        (at-person person1 refugio1)
        (box-has box1 comida)
        (need person1 comida)
        (free izquierda)
        (free derecha)
    )

    (:goal (and
        (person-has person1 comida)
    ))
)
