import time
from scheduler import Scheduler

def main():
    s = Scheduler("../micro-benchmarks/python/Image_cls.py", "temp_log_path", 75.0)
    for _ in range(10):
        s.run()
        print (repr(s))
        count = 0
        for i in s.temp_log:
            if i > s.temp_threshold:
                count += 1
        print ("Accuracy : {}".format(1 - (count / len(s.temp_log))))
    # print (repr(s))

if __name__ == "__main__":
    main()
