(define (problem problem_size4)
(:domain emergencias-costs)
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
	(= (total-cost) 0)
	(= (fly-cost deposito refugio1) 1)
	(= (fly-cost deposito refugio2) 13)
	(= (fly-cost deposito refugio3) 16)
	(= (fly-cost deposito refugio4) 4)
	(= (fly-cost refugio1 deposito) 15)
	(= (fly-cost refugio1 refugio2) 13)
	(= (fly-cost refugio1 refugio3) 2)
	(= (fly-cost refugio1 refugio4) 9)
	(= (fly-cost refugio2 deposito) 17)
	(= (fly-cost refugio2 refugio1) 4)
	(= (fly-cost refugio2 refugio3) 13)
	(= (fly-cost refugio2 refugio4) 11)
	(= (fly-cost refugio3 deposito) 10)
	(= (fly-cost refugio3 refugio1) 11)
	(= (fly-cost refugio3 refugio2) 3)
	(= (fly-cost refugio3 refugio4) 14)
	(= (fly-cost refugio4 deposito) 18)
	(= (fly-cost refugio4 refugio1) 19)
	(= (fly-cost refugio4 refugio2) 19)
	(= (fly-cost refugio4 refugio3) 13)
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
	(box-has box4 comida)
	(at-person person1 refugio2)
	(at-person person2 refugio3)
	(at-person person3 refugio4)
	(at-person person4 refugio1)
)

(:goal (and
	(person-has person1 comida)
	(person-has person2 comida)
	(person-has person3 comida)
	(person-has person4 comida)
))
(:metric minimize (total-cost))
)