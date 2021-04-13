import time
from scheduler import Scheduler

def main():
    s = Scheduler("../micro-benchmarks/python/Image_cls.py", "temp_log_path", 75.0)
    for t in range(10):
        print ("{} time(s) of execution".format(t + 1))
        s.run()
        print (repr(s))
        count = 0
        for i in s.temp_log_curr:
            if i > s.temp_threshold:
                count += 1
        for i in s.temp_log_all:
            if i > s.temp_threshold:
                count += 1
        length = len(s.temp_log_curr) + len(s.temp_log_all)
        print ("len : {}".format(length))
        print ("Accuracy : {}".format(1 - (count / length)))

if __name__ == "__main__":
    main()
