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
	(= (fly-cost deposito refugio1) 3)
	(= (fly-cost deposito refugio2) 9)
	(= (fly-cost deposito refugio3) 18)
	(= (fly-cost refugio1 deposito) 18)
	(= (fly-cost refugio1 refugio2) 20)
	(= (fly-cost refugio1 refugio3) 14)
	(= (fly-cost refugio2 deposito) 14)
	(= (fly-cost refugio2 refugio1) 20)
	(= (fly-cost refugio2 refugio3) 10)
	(= (fly-cost refugio3 deposito) 18)
	(= (fly-cost refugio3 refugio1) 16)
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
	(box-has box3 comida)
	(at-person person1 refugio2)
	(at-person person2 refugio3)
	(at-person person3 refugio3)
)

(:goal (and
	(person-has person1 comida)
	(person-has person2 comida)
	(person-has person3 comida)
))
(:metric minimize (total-cost))
)