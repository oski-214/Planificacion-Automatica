(define (problem problem_size4)
(:domain emergencias)
(:objects
	dron1 - dron
	deposito refugio1 refugio2 refugio3 refugio4 - location
	box1 box2 box3 box4 - box
	comida medicina - bcontent
	person1 person2 person3 person4 - person
	carrier1 - carrier
	n0 n1 n2 n3 n4 - num
)

(:init
	(siguiente n0 n1)
	(siguiente n1 n2)
	(siguiente n2 n3)
	(siguiente n3 n4)
	(at-dron dron1 deposito)
	(free dron1)
	(at-carrier carrier1 deposito)
	(boxes-in-carrier carrier1 n0)
	(at-box box1 deposito)
	(box-has box1 comida)
	(at-box box2 deposito)
	(box-has box2 comida)
	(at-box box3 deposito)
	(box-has box3 comida)
	(at-box box4 deposito)
	(box-has box4 medicina)
	(at-person person1 refugio3)
	(at-person person2 refugio3)
	(at-person person3 refugio2)
	(at-person person4 refugio3)
)

(:goal (and
	(person-has person1 comida)
	(person-has person3 comida)
	(person-has person4 comida)
	(person-has person4 medicina)
))
)
