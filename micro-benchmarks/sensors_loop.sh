#!/bin/bash

for i in `seq 1 2000`; do
  sensors >> 'sensors.txt'
  sleep 1s
done
