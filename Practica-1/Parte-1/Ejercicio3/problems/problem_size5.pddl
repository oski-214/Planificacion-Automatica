(define (problem emergencias-size5)
    (:domain emergencias)

    (:objects
        dron1 - dron
        person1 person2 person3 person4 person5 - person
        box1 box2 box3 box4 box5 - box
        comida medicina - bcontent
        deposito refugio1 refugio2 refugio3 refugio4 refugio5 - location
        izquierda derecha - grip
    )

    (:init
        (at-dron dron1 deposito)
        (at-box box1 deposito)
        (at-box box2 deposito)
        (at-box box3 deposito)
        (at-box box4 deposito)
        (at-box box5 deposito)
        (at-person person1 refugio1)
        (at-person person2 refugio2)
        (at-person person3 refugio3)
        (at-person person4 refugio4)
        (at-person person5 refugio5)
        (box-has box1 comida)
        (box-has box2 medicina)
        (box-has box3 comida)
        (box-has box4 medicina)
        (box-has box5 comida)
        (need person1 comida)
        (need person2 medicina)
        (need person3 comida)
        (need person4 medicina)
        (need person5 comida)
        (free izquierda)
        (free derecha)
    )

    (:goal (and
        (person-has person1 comida)
        (person-has person2 medicina)
        (person-has person3 comida)
        (person-has person4 medicina)
        (person-has person5 comida)
    ))
)
