import time, threading, statistics
from scheduler import Scheduler
import numpy as np

FEATURE_FLAG = {"Annealing": 1, "AIMD": 2, "Hybrid":3}
MODE = "Annealing"
# MODE = "AIMD"
# MODE = "Hybrid"

LEFT_BOUND = 5


def main():
    # s = Scheduler("../micro-benchmarks/python/tensorflow/wtb_train.py", "temp_log_path", 75.0, FEATURE_FLAG[MODE])
    # s = Scheduler("../micro-benchmarks/python/tensorflow/Image_cls.py", "temp_log_path", 75.0, FEATURE_FLAG[MODE]) 
    # s = Scheduler("../micro-benchmarks/python/tensorflow/mnist.py", "temp_log_path", 75.0, FEATURE_FLAG[MODE])
    # s = Scheduler("../micro-benchmarks/python/tensorflow/biLSTM.py", "temp_log_path", 75.0, FEATURE_FLAG[MODE])
    # s = Scheduler("../micro-benchmarks/python/tensorflow/random_forest.py", "temp_log_path", 75.0, FEATURE_FLAG[MODE])
    s = Scheduler("../micro-benchmarks/python/tensorflow/time_series.py", "temp_log_path", 75.0, FEATURE_FLAG[MODE])
    percent_below_threshold = []
    percent_on_target = []
    RMSD_max_temp = []
    RMSD_all_temp = []
    Average_runtime = []

    s.run()
    ts = time.time()    
    for t in range(10):
        print ("{} time(s) of execution".format(t + 1))
        s._execute_()
        # print (repr(s))
        count = 0
        for i in s.temp_log_curr:
            if i > s.temp_threshold:
                count += 1
        for i in s.temp_log_all:
            if i > s.temp_threshold:
                count += 1
        length = len(s.temp_log_curr) + len(s.temp_log_all)
        # print ("length of temp log : {}".format(length))
        temp_target = 0
        for temp in s.max_temp_log:
            if temp <= s.temp_threshold and temp >= s.temp_threshold - LEFT_BOUND:
                temp_target += 1
        print ("Max temp log : {}".format(s.max_temp_log))
        on_target = temp_target / len(s.max_temp_log)
        below_thresh = 1 - (count / length)
        rmsd_max_temp = np.sqrt(np.mean((np.asarray(s.max_temp_log) - s.temp_threshold)**2))
        rmsd_all_temp = np.sqrt(np.mean((np.asarray(s.temp_log_all) - s.temp_threshold)**2))
        
        percent_below_threshold.append(below_thresh)
        percent_on_target.append(on_target)
        RMSD_max_temp.append(rmsd_max_temp)
        RMSD_all_temp.append(rmsd_all_temp)

        print ("Percentage of temp below threshold : {}".format(percent_below_threshold))
        print ("Percentage of Max temp on target : {}".format(percent_on_target))
        print ("RMSD Max temp : {}".format(RMSD_max_temp))
        print ("RMSD All temp : {}".format(RMSD_all_temp))
        # print ("Max Temp Log : {}".format(s.max_temp_log))
        # print ("Freq Log : {}".format(s.freq_set))
        # print ("Time : {}".format(time.time() - ts)) 
        # print ("T : {}".format(t + 1))
        runtime = (time.time() - ts) / (t + 1)
        Average_runtime.append(runtime) 
        print ("Average Runtime : {}".format(Average_runtime))
    
    if len(Average_runtime) >= 2:
        print ("Average Runtime : {}".format(Average_runtime))
        print ("Runtime stdev :{}".format(statistics.stdev(Average_runtime)))
        print ("P_below stdev :{}".format(statistics.stdev(percent_below_threshold)))
        print ("P_target stdev :{}".format(statistics.stdev(percent_on_target)))
        print ("RMSD Max stdev :{}".format(statistics.stdev(RMSD_max_temp)))
        print ("RMSD All stdev :{}".format(statistics.stdev(RMSD_all_temp)))




main()
