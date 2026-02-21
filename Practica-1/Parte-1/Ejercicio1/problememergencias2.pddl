(define (problem emergencias-problem2)
    (:domain emergencias)

    (:objects 
        dron1 - dron
        person1 person2 - person 
        box1 box2 box3 - box
        comida medicina - bcontent
        deposito refugio - location
        izquierda derecha - grip
    )

    (:init 
        (at-dron dron1 deposito)
        (at-box box1 deposito)
        (at-box box2 deposito)
        (at-box box3 deposito)
        (at-person person1 refugio)
        (at-person person2 refugio)
        (box-has box1 comida)
        (box-has box2 comida)
        (box-has box3 medicina)
        (need person1 comida)
        (need person2 medicina)
        (free derecha)
        (free izquierda)
    )

    (:goal 
        (and (person-has person1 comida)
        (person-has person2 medicina))
    )
)