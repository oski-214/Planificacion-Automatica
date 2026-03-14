(define (problem problem_size1)
(:domain emergencias)
(:objects
	dron1 - dron
	deposito refugio1 - location
	box1 - box
	comida medicina - bcontent
	person1 - person
	dron1-izq dron1-der - grip
)

(:init
	(at-dron dron1 deposito)
	(free dron1-izq)
	(free dron1-der)
	(at-box box1 deposito)
	(box-has box1 medicina)
	(at-person person1 refugio1)
)

(:goal (and
	(person-has person1 medicina)
))
)
