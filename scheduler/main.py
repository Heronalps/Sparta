import time, threading
from scheduler import Scheduler
import numpy as np

FEATURE_FLAG = {"Annealing": 1, "AIMD": 2, "Hybrid":3}
# MODE = "Annealing"
MODE = "AIMD"
# MODE = "Hybrid"


def main():
    # s = Scheduler("../micro-benchmarks/python/Image_cls.py", "temp_log_path", 75.0, FEATURE_FLAG[MODE]) 
    s = Scheduler("../micro-benchmarks/python/tensorflow/wtb_train.py", "temp_log_path", 75.0, FEATURE_FLAG[MODE])
    # s = Scheduler("../micro-benchmarks/python/mnist.py", "temp_log_path", 75.0, FEATURE_FLAG[MODE])
    percent_below_threshold = []
    percent_on_target = []
    RMSD_max_temp = []
    RMSD_all_temp = []

    s.run()
    
    for t in range(100):
        print ("{} time(s) of execution".format(t + 1))
        s._execute_()
        print (repr(s))
        count = 0
        for i in s.temp_log_curr:
            if i > s.temp_threshold:
                count += 1
        for i in s.temp_log_all:
            if i > s.temp_threshold:
                count += 1
        length = len(s.temp_log_curr) + len(s.temp_log_all)
        print ("length of temp log : {}".format(length))
        temp_target = 0
        for t in s.max_temp_log:
            if t == s.temp_threshold:
                temp_target += 1
        on_target = temp_target / len(s.max_temp_log)
        below_thresh = 1 - (count / length)
        rmsd_max_temp = np.sqrt(np.mean((np.asarray(s.max_temp_log) - s.temp_threshold)**2))
        rmsd_all_temp = np.sqrt(np.mean((np.asarray(s.temp_log_all) - s.temp_threshold)**2))
        
        percent_below_threshold.append(below_thresh)
        percent_on_target.append(on_target)
        RMSD_max_temp.append(rmsd_max_temp)
        RMSD_all_temp.append(rmsd_all_temp)

        print ("Percentage of temp below threshold : {}".format(below_thresh))
        print ("Percentage of Max temp on target : {}".format(on_target))
        print ("RMSD Max temp : {}".format(rmsd_max_temp))
        print ("RMSD All temp : {}".format(rmsd_all_temp))
        print ("Max Temp Log : {}".format(s.max_temp_log))
        print ("Freq Log : {}".format(s.freq_set))


if __name__ == "__main__":
    main()
