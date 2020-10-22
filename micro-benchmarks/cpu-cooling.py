import numpy as np
import time, subprocess, re

# Generate random 3D matrix
def gen3dMatrix(dim, lower, upper):
    matrix = np.random.randint(lower, upper, size=(dim, dim, dim))
    return matrix

# 3D matrix multiplication
def gen3dMatrixMul(m1, m2):
    return np.matmul(m1, m2)

if __name__ == "__main__":
    sleep_time = 0
    ts1 = time.time()
    dim = 300
    lower = 1000
    upper = 10000
    for i in range(100):
        m1 = gen3dMatrix(dim, lower, upper)
        m2 = gen3dMatrix(dim, lower, upper)
        gen3dMatrixMul(m1, m2)
        print ("Sleep {0} seconds".format(sleep_time))
        time.sleep(sleep_time)

        output = subprocess.check_output("sensors")
        # regex temp
        temp = re.search("Package id 0:  \+(\d\d.\d)", output.decode('utf-8')).group(1)
        print ("CPU Temp {0} \n".format(temp))
        sleep_time = sleep_time + 0.1   
        

    print("====Time====")
    print(time.time() - ts1)
