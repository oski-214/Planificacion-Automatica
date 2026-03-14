(define (problem problem_size9)
(:domain emergencias)
(:objects
	dron1 - dron
	deposito refugio1 refugio2 refugio3 refugio4 refugio5 refugio6 refugio7 refugio8 refugio9 - location
	box1 box2 box3 box4 box5 box6 box7 box8 box9 - box
	comida medicina - bcontent
	person1 person2 person3 person4 person5 person6 person7 person8 person9 - person
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
	(at-box box4 deposito)
	(box-has box4 comida)
	(at-box box5 deposito)
	(box-has box5 medicina)
	(at-box box6 deposito)
	(box-has box6 medicina)
	(at-box box7 deposito)
	(box-has box7 medicina)
	(at-box box8 deposito)
	(box-has box8 medicina)
	(at-box box9 deposito)
	(box-has box9 medicina)
	(at-person person1 refugio1)
	(at-person person2 refugio4)
	(at-person person3 refugio1)
	(at-person person4 refugio8)
	(at-person person5 refugio2)
	(at-person person6 refugio2)
	(at-person person7 refugio2)
	(at-person person8 refugio5)
	(at-person person9 refugio2)
)

(:goal (and
	(person-has person2 medicina)
	(person-has person3 comida)
	(person-has person3 medicina)
	(person-has person4 medicina)
	(person-has person6 comida)
	(person-has person6 medicina)
	(person-has person7 comida)
	(person-has person7 medicina)
	(person-has person9 comida)
))
)
