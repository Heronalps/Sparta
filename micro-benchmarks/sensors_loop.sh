#!/bin/bash

for i in `seq 1 200`; do
  sensors
  sleep 1s
done
