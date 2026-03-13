(define (problem prob_d1_t1_l4_p1_c2)
(:domain emergencias-temporal)
(:objects
	dron1 - dron
	deposito refugio1 refugio2 refugio3 refugio4 - location
	box1 box2 - box
	comida medicina - bcontent
	person1 - person
	carrier1 - carrier
	n0 n1 n2 n3 n4 - num
)

(:init
	(= (fly-cost deposito refugio1) 8)
	(= (fly-cost deposito refugio2) 5)
	(= (fly-cost deposito refugio3) 4)
	(= (fly-cost deposito refugio4) 18)
	(= (fly-cost refugio1 deposito) 3)
	(= (fly-cost refugio1 refugio2) 19)
	(= (fly-cost refugio1 refugio3) 14)
	(= (fly-cost refugio1 refugio4) 2)
	(= (fly-cost refugio2 deposito) 1)
	(= (fly-cost refugio2 refugio1) 3)
	(= (fly-cost refugio2 refugio3) 7)
	(= (fly-cost refugio2 refugio4) 8)
	(= (fly-cost refugio3 deposito) 17)
	(= (fly-cost refugio3 refugio1) 20)
	(= (fly-cost refugio3 refugio2) 1)
	(= (fly-cost refugio3 refugio4) 18)
	(= (fly-cost refugio4 deposito) 7)
	(= (fly-cost refugio4 refugio1) 18)
	(= (fly-cost refugio4 refugio2) 14)
	(= (fly-cost refugio4 refugio3) 8)
	(siguiente n0 n1)
	(siguiente n1 n2)
	(siguiente n2 n3)
	(siguiente n3 n4)
	(at-dron dron1 deposito)
	(free dron1)
	(dron-available dron1)
	(at-carrier carrier1 deposito)
	(boxes-in-carrier carrier1 n0)
	(carrier-available carrier1)
	(at-box box1 deposito)
	(box-has box1 comida)
	(at-box box2 deposito)
	(box-has box2 comida)
	(at-person person1 refugio4)
	(person-available person1)
)

(:goal (and
	(person-has person1 comida)
))
(:metric minimize (total-time))
)
