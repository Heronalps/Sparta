#!/bin/bash

for i in `seq 1`
do 
 	echo "\n$i"
	python -u main.py | tee -a ./log/Annealing_H_time_series_042621.log

	# python main.py | tee -a ./log/Annealing_N_random_forest_042221.log
	sleep 10
done


# python main.py | tee -a ./log/Hybrid_N_wtb_train_041921.log

