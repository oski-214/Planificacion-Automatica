(define (problem drone_problem_d1_l5_p5_c5_g5)
(:domain emergencias)
(:objects
	dron1 - dron
	deposito refugio1 refugio2 refugio3 refugio4 refugio5 - location
	box1 box2 box3 box4 box5 - box
	comida medicina - bcontent
	person1 person2 person3 person4 person5 - person
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
	(at-box box4 deposito)
	(box-has box4 medicina)
	(at-box box5 deposito)
	(box-has box5 medicina)
	(at-person person1 refugio3)
	(at-person person2 refugio3)
	(at-person person3 refugio2)
	(at-person person4 refugio1)
	(at-person person5 refugio3)
)

(:goal (and
	(person-has person1 medicina)
	(person-has person2 comida)
	(person-has person2 medicina)
	(person-has person3 comida)
	(person-has person3 medicina)
))
)
