#!/bin/bash

_now=$(date +"%Y_%m_%d")
_file="temp_log_$_now.txt"
#_regex="Package\sid\s0:\s*\+\d\d\.\d"
_regex="Package\sid\s0:\s*\+([0-9]*\.[0-9])"

while true; do
    sleep 1
    _temp_file=$(sensors)
    if [[ $_temp_file =~ $_regex ]]
    then
	echo $_temp_file
	_temp="${BASH_REMATCH[1]}"
    	echo $_temp >> "/home/heronalps/Downloads/Sparta/temp_data/$_file"
    fi
done
