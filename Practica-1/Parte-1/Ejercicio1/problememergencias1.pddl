(define (problem emergencias-problem1)
    (:domain emergencias)

    (:objects 
        dron1 - dron
        person1 - person 
        box1 - box
        comida medicina - bcontent
        deposito refugio - location
        izquierda derecha - grip
    )

    (:init 
        (at-dron dron1 deposito)
        (at-box box1 deposito)
        (at-person person1 refugio)
        (box-has box1 comida)
        (need person1 comida)
        (free derecha)
        (free izquierda)
    )

    (:goal 
        (person-has person1 comida)
    )
)