(define (problem emergencias-size3)
    (:domain emergencias)

    (:objects
        dron1 - dron
        person1 person2 person3 - person
        box1 box2 box3 - box
        comida medicina - bcontent
        deposito refugio1 refugio2 refugio3 - location
        izquierda derecha - grip
    )

    (:init
        (at-dron dron1 deposito)
        (at-box box1 deposito)
        (at-box box2 deposito)
        (at-box box3 deposito)
        (at-person person1 refugio1)
        (at-person person2 refugio2)
        (at-person person3 refugio3)
        (box-has box1 comida)
        (box-has box2 medicina)
        (box-has box3 comida)
        (need person1 comida)
        (need person2 medicina)
        (need person3 comida)
        (free izquierda)
        (free derecha)
    )

    (:goal (and
        (person-has person1 comida)
        (person-has person2 medicina)
        (person-has person3 comida)
    ))
)
