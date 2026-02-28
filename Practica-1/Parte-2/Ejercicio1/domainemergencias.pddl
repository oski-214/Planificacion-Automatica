(define (domain emergencias)
    (:requirements :strips :typing)
    (:types
        location box bcontent person dron carrier num - object
    )

    (:predicates
        (at-dron ?d - dron ?l - location) 
        (at-box ?b - box ?l - location)
        (at-person ?p - person ?l - location)
        (at-carrier ?c - carrier ?l - location)
        
        (box-has ?b - box ?c - bcontent)
        (person-has ?p - person ?c - bcontent)
        
        ;; EL PREDICADO QUE FALTABA
        (need ?p - person ?c - bcontent)
        
        ;; El dron ahora tiene un único brazo implícito
        (free ?d - dron)
        (carrying ?d - dron ?b - box)
        
        ;; Predicados para el transportador y los números
        (in-carrier ?b - box ?c - carrier)
        (boxes-in-carrier ?c - carrier ?n - num)
        (siguiente ?n1 - num ?n2 - num)
    )

    ;; Mueve solo al dron
    (:action move
        :parameters (?from - location ?to - location ?dron - dron)
        :precondition (at-dron ?dron ?from)
        :effect (and (at-dron ?dron ?to) (not (at-dron ?dron ?from)))
    )

    ;; Mueve al dron llevándose el transportador consigo
    (:action move-carrier
        :parameters (?from - location ?to - location ?dron - dron ?carrier - carrier)
        :precondition (and (at-dron ?dron ?from) (at-carrier ?carrier ?from))
        :effect (and (at-dron ?dron ?to) (not (at-dron ?dron ?from)) 
                     (at-carrier ?carrier ?to) (not (at-carrier ?carrier ?from)))
    )

    ;; Recoge una caja del suelo (requiere tener el brazo libre)
    (:action pick
        :parameters (?box - box ?location - location ?dron - dron)
        :precondition (and (at-dron ?dron ?location) (at-box ?box ?location) (free ?dron))
        :effect (and (not (at-box ?box ?location)) (not (free ?dron)) (carrying ?dron ?box))
    )

    ;; Entrega una caja a una persona (Actualizada con NEED)
    (:action leave
        :parameters (?box - box ?location - location ?dron - dron ?person - person ?content - bcontent)
        :precondition (and (at-dron ?dron ?location) (carrying ?dron ?box) (at-person ?person ?location) (box-has ?box ?content) (need ?person ?content))
        :effect (and (at-box ?box ?location) (free ?dron) (not (carrying ?dron ?box)) (person-has ?person ?content) (not (need ?person ?content)))
    )

    ;; Mete una caja en el transportador (Suma 1)
    (:action put-in-carrier
        :parameters (?box - box ?location - location ?dron - dron ?carrier - carrier ?n1 - num ?n2 - num)
        :precondition (and (at-dron ?dron ?location) (at-carrier ?carrier ?location) (carrying ?dron ?box) 
                           (boxes-in-carrier ?carrier ?n1) (siguiente ?n1 ?n2))
        :effect (and (not (carrying ?dron ?box)) (free ?dron) (in-carrier ?box ?carrier) 
                     (not (boxes-in-carrier ?carrier ?n1)) (boxes-in-carrier ?carrier ?n2))
    )

    ;; Saca una caja del transportador (Resta 1)
    (:action take-from-carrier
        :parameters (?box - box ?location - location ?dron - dron ?carrier - carrier ?n1 - num ?n2 - num)
        :precondition (and (at-dron ?dron ?location) (at-carrier ?carrier ?location) (free ?dron) (in-carrier ?box ?carrier) 
                           (boxes-in-carrier ?carrier ?n2) (siguiente ?n1 ?n2))
        :effect (and (carrying ?dron ?box) (not (free ?dron)) (not (in-carrier ?box ?carrier)) 
                     (not (boxes-in-carrier ?carrier ?n2)) (boxes-in-carrier ?carrier ?n1))
    )
)