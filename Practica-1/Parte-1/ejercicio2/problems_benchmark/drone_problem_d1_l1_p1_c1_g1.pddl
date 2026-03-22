(define (problem drone_problem_d1_l1_p1_c1_g1)
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
	(box-has box1 comida)
	(at-person person1 refugio1)
)

(:goal (and
	(person-has person1 comida)
))
)
