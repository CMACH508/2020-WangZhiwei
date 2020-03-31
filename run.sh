#!/bin/bash
for ((it=1; it<=50; it++))
do
    for ((i=1; i<=10; i++))
        do
            echo "epoch $i"
	    python selfplay.py
	    python conquer.py
	    python main.py --saved_model=current.model
        done
    num=`expr 2000 \* $it`
    cp current.model game$num.model
    python play.py --saved_model=game$num.model
done
cp best.model current.model
