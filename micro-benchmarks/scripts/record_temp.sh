#!/bin/bash
_now=$(date +"%Y_%m_%d")
_file="temp_log_$_now.txt"
while true; do
    (date; sensors; echo '-----------') | cat >> "/var/log/temperatures/$_file"
done
