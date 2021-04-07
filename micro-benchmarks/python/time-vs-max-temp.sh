#!/bin/bash

bash ../scripts/record_temp.sh &
# cgexec -g cpu:brain python ./Image_cls.py ../image_batch_3.zip 8
python ./Image_cls.py ../image_batch_3.zip 8
pkill -f record_temp.sh
