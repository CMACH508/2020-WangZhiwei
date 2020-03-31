#!/bin/bash
for ((i=1; i<=10; i++))
do
	echo "epoch $i"
	python selfplay.py
	python conquer.py
	python main.py --saved_model=current.model
done
cp current.model game72000.model
python play.py --saved_model=game72000.model

for ((i=1; i<=10; i++))
do
	echo "epoch $i"
	python selfplay.py
	python conquer.py
	python main.py --saved_model=current.model
done
cp current.model game74000.model
python play.py --saved_model=game74000.model

for ((i=1; i<=10; i++))
do
	echo "epoch $i"
	python selfplay.py
	python conquer.py
	python main.py --saved_model=current.model
done
cp current.model game76000.model
python play.py --saved_model=game76000.model

for ((i=1; i<=10; i++))
do
	echo "epoch $i"
	python selfplay.py
	python conquer.py
	python main.py --saved_model=current.model
done
cp current.model game78000.model
python play.py --saved_model=game78000.model


for ((i=1; i<=10; i++))
do
	echo "epoch $i"
	python selfplay.py
	python conquer.py
	python main.py --saved_model=current.model
done
cp current.model game80000.model
python play.py --saved_model=game80000.model


for ((i=1; i<=10; i++))
do
	echo "epoch $i"
	python selfplay.py
	python conquer.py
	python main.py --saved_model=current.model
done
cp current.model game82000.model
python play.py --saved_model=game82000.model


for ((i=1; i<=10; i++))
do
	echo "epoch $i"
	python selfplay.py
	python conquer.py
	python main.py --saved_model=current.model
done
cp current.model game84000.model
python play.py --saved_model=game84000.model
