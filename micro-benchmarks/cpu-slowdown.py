import numpy as np
import time, subprocess, re

# Generate random 2D matrix
def gen2dMatrix(dim, lower, upper):
    matrix = np.random.randint(lower, upper, size=(dim, dim))
    return matrix

# 2D matrix multiplication
def gen2dMatrixMul(m1, m2, sleep_time):
    res = [[0 for x in range(len(m1))] for y in range(len(m2[0]))]
    # explicit for loops 
    for i in range(len(m1)): 
        # time.sleep(sleep_time)
        for j in range(len(m2[0])): 
            for k in range(len(m2)):               
                # print ("Sleep {0} seconds".format(sleep_time))
                # print ("i: {}".format(i))
                # print ("j: {}".format(j))
                # resulted matrix 
                res[i][j] += m1[i][k] * m2[k][j] 
    

if __name__ == "__main__":
    sleep_time = 0.001
    ts1 = time.time()
    dim = 64
    lower = 100
    upper = 1000
    for i in range(100):
        m1 = gen2dMatrix(dim, lower, upper)
        m2 = gen2dMatrix(dim, lower, upper)
        gen2dMatrixMul(m1, m2, sleep_time)
        
        # output = subprocess.check_output("sensors")
        # # regex temp
        # temp = re.search("Package id 0:  \+(\d\d.\d)", output.decode('utf-8')).group(1)
        # print ("CPU Temp {0} \n".format(temp))
        # sleep_time = sleep_time + 0.1   
        

    print("====Time====")
    print(time.time() - ts1)
