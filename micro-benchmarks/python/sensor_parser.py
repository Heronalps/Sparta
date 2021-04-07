import re

temps = []
with open("./sensors1.txt") as f:
    for raw_line in f:
        line = raw_line.strip()
        # regex temp
        # temp = re.search("Package id 0:  \+(\d\d.\d)", output.decode('utf-8')).group(1)
        temp = re.search("Package id 0:  \+(\d\d.\d)", line)
        if (temp):
            # print ("CPU Temp {0} \n".format(temp.group(1)))
            temps.append(temp.group(1))

with open("./temps1.txt", "a") as f:
    for temp in temps:
        f.write(temp)
        f.write("\n")
        
        

        
        

