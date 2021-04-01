#!/bin/bash

_now=$(date +"%Y_%m_%d_%H_%M_%S")
_file="temp_log_$_now.txt"
#_regex="Package\sid\s0:\s*\+\d\d\.\d"
_regex="Package\sid\s0:\s*\+([0-9]*\.[0-9])"
_dir="/home/heronalps/Downloads/Sparta/temp_data"

if [ ! -d "$_dir/$1" ]
then
	mkdir "$_dir/$1"
fi

while true; do
    sleep 1
    _temp_file=$(sensors)
    if [[ $_temp_file =~ $_regex ]]
    then
	# echo $_temp_file
	_temp="${BASH_REMATCH[1]}"
    	echo $_temp >> "$_dir/$1/$_file"
    fi
done
