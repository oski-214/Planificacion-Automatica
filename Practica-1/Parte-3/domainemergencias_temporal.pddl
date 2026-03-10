(define (domain emergencias-temporal)
    (:requirements :strips :typing :durative-actions :fluents)
    (:types
        location box bcontent person dron carrier num - object
    )

    (:functions
        (fly-cost ?l1 ?l2 - location) - number
    )

    (:predicates
        (at-dron ?d - dron ?l - location) 
        (at-box ?b - box ?l - location)
        (at-person ?p - person ?l - location)
        (at-carrier ?c - carrier ?l - location)
        
        (box-has ?b - box ?c - bcontent)
        (person-has ?p - person ?c - bcontent)
        
        ;; Estado del brazo del dron
        (free ?d - dron)
        (carrying ?d - dron ?b - box)
        
        ;; Predicados para el transportador y los números
        (in-carrier ?b - box ?c - carrier)
        (boxes-in-carrier ?c - carrier ?n - num)
        (siguiente ?n1 - num ?n2 - num)

        ;; Mutex para concurrencia
        (dron-available ?d - dron)
        (carrier-available ?c - carrier)
        (person-available ?p - person)
    )

    ;; Mueve solo al dron (duración = fly-cost)
    (:durative-action move
        :parameters (?from - location ?to - location ?dron - dron)
        :duration (= ?duration (fly-cost ?from ?to))
        :condition (and 
            (at start (dron-available ?dron))
            (at start (at-dron ?dron ?from))
            (at start (free ?dron))
        )
        :effect (and 
            (at start (not (dron-available ?dron)))
            (at start (not (at-dron ?dron ?from)))
            (at end (at-dron ?dron ?to))
            (at end (dron-available ?dron))
        )
    )

    ;; Mueve al dron llevándose el transportador consigo (duración = fly-cost)
    (:durative-action move-carrier
        :parameters (?from - location ?to - location ?dron - dron ?carrier - carrier)
        :duration (= ?duration (fly-cost ?from ?to))
        :condition (and 
            (at start (dron-available ?dron))
            (at start (carrier-available ?carrier))
            (at start (at-dron ?dron ?from))
            (at start (at-carrier ?carrier ?from))
            (at start (free ?dron))
        )
        :effect (and 
            (at start (not (dron-available ?dron)))
            (at start (not (carrier-available ?carrier)))
            (at start (not (at-dron ?dron ?from)))
            (at start (not (at-carrier ?carrier ?from)))
            (at end (at-dron ?dron ?to))
            (at end (at-carrier ?carrier ?to))
            (at end (dron-available ?dron))
            (at end (carrier-available ?carrier))
        )
    )

    ;; Recoge una caja del suelo (duración = 5)
    (:durative-action pick
        :parameters (?box - box ?location - location ?dron - dron)
        :duration (= ?duration 5)
        :condition (and 
            (at start (dron-available ?dron))
            (at start (at-dron ?dron ?location))
            (at start (at-box ?box ?location))
            (at start (free ?dron))
        )
        :effect (and 
            (at start (not (dron-available ?dron)))
            (at start (not (at-box ?box ?location)))
            (at start (not (free ?dron)))
            (at end (carrying ?dron ?box))
            (at end (dron-available ?dron))
        )
    )

    ;; Entrega una caja a una persona (duración = 5)
    (:durative-action leave
        :parameters (?box - box ?location - location ?dron - dron ?person - person ?content - bcontent)
        :duration (= ?duration 5)
        :condition (and 
            (at start (dron-available ?dron))
            (at start (person-available ?person))
            (at start (at-dron ?dron ?location))
            (at start (carrying ?dron ?box))
            (at start (at-person ?person ?location))
            (at start (box-has ?box ?content))
        )
        :effect (and 
            (at start (not (dron-available ?dron)))
            (at start (not (person-available ?person)))
            (at start (not (carrying ?dron ?box)))
            (at start (not (box-has ?box ?content)))
            (at end (at-box ?box ?location))
            (at end (free ?dron))
            (at end (person-has ?person ?content))
            (at end (dron-available ?dron))
            (at end (person-available ?person))
        )
    )

    ;; Mete una caja en el transportador (duración = 5)
    (:durative-action put-in-carrier
        :parameters (?box - box ?location - location ?dron - dron ?carrier - carrier ?n1 - num ?n2 - num)
        :duration (= ?duration 5)
        :condition (and 
            (at start (dron-available ?dron))
            (at start (carrier-available ?carrier))
            (at start (at-dron ?dron ?location))
            (at start (at-carrier ?carrier ?location))
            (at start (carrying ?dron ?box))
            (at start (boxes-in-carrier ?carrier ?n1))
            (at start (siguiente ?n1 ?n2))
        )
        :effect (and 
            (at start (not (dron-available ?dron)))
            (at start (not (carrier-available ?carrier)))
            (at start (not (carrying ?dron ?box)))
            (at start (not (boxes-in-carrier ?carrier ?n1)))
            (at end (free ?dron))
            (at end (in-carrier ?box ?carrier))
            (at end (boxes-in-carrier ?carrier ?n2))
            (at end (dron-available ?dron))
            (at end (carrier-available ?carrier))
        )
    )

    ;; Saca una caja del transportador (duración = 5)
    (:durative-action take-from-carrier
        :parameters (?box - box ?location - location ?dron - dron ?carrier - carrier ?n1 - num ?n2 - num)
        :duration (= ?duration 5)
        :condition (and 
            (at start (dron-available ?dron))
            (at start (carrier-available ?carrier))
            (at start (at-dron ?dron ?location))
            (at start (at-carrier ?carrier ?location))
            (at start (free ?dron))
            (at start (in-carrier ?box ?carrier))
            (at start (boxes-in-carrier ?carrier ?n2))
            (at start (siguiente ?n1 ?n2))
        )
        :effect (and 
            (at start (not (dron-available ?dron)))
            (at start (not (carrier-available ?carrier)))
            (at start (not (free ?dron)))
            (at start (not (in-carrier ?box ?carrier)))
            (at start (not (boxes-in-carrier ?carrier ?n2)))
            (at end (carrying ?dron ?box))
            (at end (boxes-in-carrier ?carrier ?n1))
            (at end (dron-available ?dron))
            (at end (carrier-available ?carrier))
        )
    )
)
