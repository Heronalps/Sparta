#!/bin/bash

for i in $(seq 3.5 0.1 3.5)
do
	echo $i
	./cpu_scaling -u ${i}GHz
	bash record_temp.sh &
	# python ../python/Image_cls.py ../image_batch_3.zip 8
	# for i in `seq 460`
	# do
	# 	../c/a.out
	# done

	../c/a.out

	# python ../python/mnist.py
	pkill -f record_temp.sh
done
