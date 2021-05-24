import statistics as sc
import re, os

path = '/home/heronalps/Downloads/Sparta/temp_data/second_cv_exp/'
regex = re.compile("temp_log_2021_02_1[8-9]*")
count = 1
for _, _, files in os.walk(path):
    for file in sorted(files):
        if regex.match(file):
            temps = []
            with open(path + file) as f:
                lines = f.readlines()
                for t in lines:
                    temps.append(float(t))

            third_len = int(len(temps) / 3)
            # print (third_len)
            # print (temps[third_len - 10 : third_len])
            # print (temps[third_len * 2 - 10 :third_len * 2])

            first = temps[:third_len]
            second = temps[third_len : third_len * 2 ]
            third = temps[third_len * 2 :]
            print ("===={}====".format(count))
            print (file)
            print (sc.stdev(first)/sc.mean(first))
            print (sc.stdev(second)/sc.mean(second))
            print (sc.stdev(third)/sc.mean(third))
            count += 1
