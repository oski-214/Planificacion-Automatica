(define (problem emergencias-size2)
    (:domain emergencias)

    (:objects
        dron1 - dron
        person1 person2 - person
        box1 box2 - box
        comida medicina - bcontent
        deposito refugio1 refugio2 - location
        izquierda derecha - grip
    )

    (:init
        (at-dron dron1 deposito)
        (at-box box1 deposito)
        (at-box box2 deposito)
        (at-person person1 refugio1)
        (at-person person2 refugio2)
        (box-has box1 comida)
        (box-has box2 medicina)
        (need person1 comida)
        (need person2 medicina)
        (free izquierda)
        (free derecha)
    )

    (:goal (and
        (person-has person1 comida)
        (person-has person2 medicina)
    ))
)
