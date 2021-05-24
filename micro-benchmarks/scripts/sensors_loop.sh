#!/bin/bash

for i in `seq 1 20000`; do
  sensors >> 'sensors1.txt'
  # sleep 0.1s
done
