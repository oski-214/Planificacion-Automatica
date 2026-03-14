(define (problem problem_size3)
(:domain emergencias)
(:objects
	dron1 - dron
	deposito refugio1 refugio2 refugio3 - location
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
	(box-has box3 comida)
	(at-person person1 refugio2)
	(at-person person2 refugio3)
	(at-person person3 refugio1)
)

(:goal (and
	(person-has person1 comida)
	(person-has person2 comida)
	(person-has person3 comida)
))
)
