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
	(= (fly-cost deposito refugio1) 19)
	(= (fly-cost deposito refugio2) 13)
	(= (fly-cost deposito refugio3) 12)
	(= (fly-cost deposito refugio4) 2)
	(= (fly-cost refugio1 deposito) 14)
	(= (fly-cost refugio1 refugio2) 11)
	(= (fly-cost refugio1 refugio3) 1)
	(= (fly-cost refugio1 refugio4) 2)
	(= (fly-cost refugio2 deposito) 12)
	(= (fly-cost refugio2 refugio1) 15)
	(= (fly-cost refugio2 refugio3) 12)
	(= (fly-cost refugio2 refugio4) 2)
	(= (fly-cost refugio3 deposito) 19)
	(= (fly-cost refugio3 refugio1) 18)
	(= (fly-cost refugio3 refugio2) 20)
	(= (fly-cost refugio3 refugio4) 11)
	(= (fly-cost refugio4 deposito) 4)
	(= (fly-cost refugio4 refugio1) 11)
	(= (fly-cost refugio4 refugio2) 4)
	(= (fly-cost refugio4 refugio3) 5)
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
	(at-box box3 deposito)
	(box-has box3 medicina)
	(at-box box4 deposito)
	(box-has box4 medicina)
	(at-person person1 refugio2)
	(at-person person2 refugio3)
	(at-person person3 refugio3)
	(at-person person4 refugio3)
)

(:goal (and
	(person-has person2 medicina)
	(person-has person3 comida)
	(person-has person3 medicina)
	(person-has person4 medicina)
))
(:metric minimize (total-cost))
)