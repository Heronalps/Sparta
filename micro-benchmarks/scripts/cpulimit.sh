#!/bin/bash

taskset -p 10034 -c 0

while sleep 3        # execute each 3 seconds
do 
   # get the processes that use more than 20% of CPU
   PIDS=`top -b -n1 | tail -n +8 | gawk '$9>20 {print $1}'`
   for i in $PIDS
   do
      # limit the new violating processes to 20%
      cpulimit -p $i -l 20 -z &    
   done
done
