import statistics as sc
import re, os

path = "/home/heronalps/Downloads/Sparta/temp_data/cold_tensorflow_0310/"
regex = re.compile("temp_log_2021_03_*")
count = 1
# print (path)
for _, _, files in os.walk(path):
    for file in sorted(files):
        # print (file)
        if regex.match(file):
            temps = []
            with open(path + file) as f:
                lines = f.readlines()
                for line in lines:
                    temps.append(float(line))
                print (count)
                print (file)
                print ("max : {}".format(max(temps)))
                print ("mean : {}".format(sc.mean(temps)))
                print ("median : {}".format(sc.median(temps)))
                # print ("mode : {}".format(sc.mode(temps)))
                print ("===========")
                count += 1


