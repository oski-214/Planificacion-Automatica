(define (domain emergencias)
    (:requirements :strips :typing)
    (:types
        location box bcontent grip person dron - object
    )

    (:predicates
        (at-dron ?d - dron ?l - location) 
        (at-box ?b - box ?l - location)
        (at-person ?p - person ?l - location)
        
        (box-has ?b - box ?c - bcontent)
        (person-has ?p - person ?c - bcontent)
        
        (free ?g - grip)
        (carrying ?d - dron ?g - grip ?b - box)
    )


    (:action move
        :parameters (?from - location ?to - location ?dron - dron)
        :precondition (at-dron ?dron ?from)
        :effect (and (at-dron ?dron ?to)(not(at-dron ?dron ?from)))
    )

    (:action pick
        :parameters (?box - box ?location - location ?gripper - grip ?dron - dron)
        :precondition (and (at-dron ?dron ?location)(at-box ?box ?location)(free ?gripper))
        :effect (and (not (at-box ?box ?location))(not (free ?gripper))(carrying ?dron ?gripper ?box))
    )

    (:action leave
        :parameters (?box - box ?location - location ?gripper - grip ?dron - dron ?person - person ?content - bcontent)
        :precondition (and (at-dron ?dron ?location)(carrying ?dron ?gripper ?box)(at-person ?person ?location)(box-has ?box ?content))
        :effect (and (at-box ?box ?location)(free ?gripper)(not(carrying ?dron ?gripper ?box))(person-has ?person ?content))
    )
)