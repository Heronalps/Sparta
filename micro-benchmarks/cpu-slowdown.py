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
        for j in range(len(m2[0])): 
            for k in range(len(m2)): 
                time.sleep(sleep_time)
                print ("Sleep {0} seconds".format(sleep_time))
                # resulted matrix 
                res[i][j] += m1[i][k] * m2[k][j] 
    

if __name__ == "__main__":
    sleep_time = 0.1
    ts1 = time.time()
    dim = 300
    lower = 1000
    upper = 10000
    for i in range(100):
        m1 = gen2dMatrix(dim, lower, upper)
        m2 = gen2dMatrix(dim, lower, upper)
        gen2dMatrixMul(m1, m2)
        
        # output = subprocess.check_output("sensors")
        # # regex temp
        # temp = re.search("Package id 0:  \+(\d\d.\d)", output.decode('utf-8')).group(1)
        # print ("CPU Temp {0} \n".format(temp))
        # sleep_time = sleep_time + 0.1   
        

    print("====Time====")
    print(time.time() - ts1)
