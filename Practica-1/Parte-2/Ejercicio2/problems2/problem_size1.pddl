(define (problem problem_size1)
(:domain emergencias-costs)
(:objects
	dron1 - dron
	deposito refugio1 - location
	box1 - box
	comida medicina - bcontent
	person1 - person
	carrier1 - carrier
	n0 n1 n2 n3 n4 - num
)

(:init
	(= (total-cost) 0)
	(= (fly-cost deposito refugio1) 19)
	(= (fly-cost refugio1 deposito) 18)
	(siguiente n0 n1)
	(siguiente n1 n2)
	(siguiente n2 n3)
	(siguiente n3 n4)
	(at-dron dron1 deposito)
	(free dron1)
	(at-carrier carrier1 deposito)
	(boxes-in-carrier carrier1 n0)
	(at-box box1 deposito)
	(box-has box1 medicina)
	(at-person person1 refugio1)
)

(:goal (and
	(person-has person1 medicina)
))
(:metric minimize (total-cost))
)