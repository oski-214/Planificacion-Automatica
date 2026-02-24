(define (problem drone_problem_d1_l3_p3_c3_g3)
(:domain emergencias)
(:objects
	dron1 - dron
	deposito loc1 loc2 loc3 - location
	box1 box2 box3 - box
	comida medicina - bcontent
	person1 person2 person3 - person
	dron1-izq dron1-der - grip
)

(:init
	(at-dron dron1 deposito)
	(free dron1-izq)
	(free dron1-der)
	(at-box box1 deposito)
	(box-has box1 comida)
	(at-box box2 deposito)
	(box-has box2 comida)
	(at-box box3 deposito)
	(box-has box3 medicina)
	(at-person person1 loc3)
	(at-person person2 loc2)
	(at-person person3 loc3)
	(need person1 medicina)
	(need person2 comida)
	(need person3 comida)
)

(:goal (and
	(person-has person1 medicina)
	(person-has person2 comida)
	(person-has person3 comida)
))
)
