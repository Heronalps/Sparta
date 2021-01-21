import numpy as np
import time

# Generate random 3D matrix
def gen3dMatrix(dim):
    matrix = np.random.rand(dim, dim, dim)
    return matrix

# 3D matrix multiplication
def gen3dMatrixMul(m1, m2):
    return np.matmul(m1, m2)

if __name__ == "__main__":
    sleep_time = 3.1
    ts1 = time.time()
    dim = 2560
    for _ in range(10):
        m1 = gen3dMatrix(dim)
        m2 = gen3dMatrix(dim)
        gen3dMatrixMul(m1, m2)
        # print ("Sleep {0} seconds".format(sleep_time))
        # time.sleep(sleep_time)
        # sleep_time = sleep_time + 0.1

    print("====Time====")
    print(time.time() - ts1)
