(define (problem problem_size3)
(:domain emergencias-costs)
(:objects
	dron1 - dron
	deposito refugio1 refugio2 refugio3 - location
	box1 box2 box3 - box
	comida medicina - bcontent
	person1 person2 person3 - person
	carrier1 - carrier
	n0 n1 n2 n3 n4 - num
)

(:init
	(= (total-cost) 0)
	(= (fly-cost deposito refugio1) 18)
	(= (fly-cost deposito refugio2) 5)
	(= (fly-cost deposito refugio3) 7)
	(= (fly-cost refugio1 deposito) 8)
	(= (fly-cost refugio1 refugio2) 5)
	(= (fly-cost refugio1 refugio3) 17)
	(= (fly-cost refugio2 deposito) 19)
	(= (fly-cost refugio2 refugio1) 18)
	(= (fly-cost refugio2 refugio3) 15)
	(= (fly-cost refugio3 deposito) 13)
	(= (fly-cost refugio3 refugio1) 12)
	(= (fly-cost refugio3 refugio2) 6)
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
	(box-has box3 medicina)
	(at-person person1 refugio2)
	(at-person person2 refugio1)
	(at-person person3 refugio3)
)

(:goal (and
	(person-has person1 comida)
	(person-has person1 medicina)
	(person-has person2 comida)
))
(:metric minimize (total-cost))
)