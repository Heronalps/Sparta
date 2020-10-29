#!/bin/bash

for i in `seq 1 8000`; do
  sensors >> 'sensors.txt'
  # sleep 0.1s
done
