import time

ts = time.time()

with open("./test.txt", "a") as f:
    for i in range(1_000_000_000):
        f.write("This is {0} line of string \n".format(i))

with open("./test.txt") as f:
    while True:
        line = f.readline()
        if not line:
            break
        # print ("Line: {} \n".format(line))

print("Time: {}".format(time.time() - ts))

    
