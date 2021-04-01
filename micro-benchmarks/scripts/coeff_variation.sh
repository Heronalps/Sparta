#!/bin/bash
echo "Starting at $(date +"%H:%M:%S")"
for i in `seq 10`
do
	echo "$i time(s) at $(date +"%H:%M:%S")"
	bash record_temp.sh &
	sleep 300
	echo "Benchmark starts: $(date +"%H:%M:%S")"
	../c/a.out &
	sleep 300
	echo "Kill process: $(date +"%H:%M:%S")"
	pkill -f a.out
	sleep 300
	echo "Kill temp monitor: $(date +"%H:%M:%S")"
	pkill -f record_temp.sh
done
exit

