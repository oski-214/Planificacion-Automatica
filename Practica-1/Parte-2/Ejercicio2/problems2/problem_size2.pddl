(define (problem problem_size2)
(:domain emergencias-costs)
(:objects
	dron1 - dron
	deposito refugio1 refugio2 - location
	box1 box2 - box
	comida medicina - bcontent
	person1 person2 - person
	carrier1 - carrier
	n0 n1 n2 n3 n4 - num
)

(:init
	(= (total-cost) 0)
	(= (fly-cost deposito refugio1) 15)
	(= (fly-cost deposito refugio2) 18)
	(= (fly-cost refugio1 deposito) 7)
	(= (fly-cost refugio1 refugio2) 4)
	(= (fly-cost refugio2 deposito) 16)
	(= (fly-cost refugio2 refugio1) 11)
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
	(box-has box2 medicina)
	(at-person person1 refugio1)
	(at-person person2 refugio2)
)

(:goal (and
	(person-has person1 comida)
	(person-has person2 medicina)
))
(:metric minimize (total-cost))
)