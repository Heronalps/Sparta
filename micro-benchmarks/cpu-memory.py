import numpy as np
import time

# Generate random 3D matrix
def gen3dMatrix(dim, lower, upper):
    matrix = np.random.randint(lower, upper, size=(dim, dim, dim))
    return matrix

# 3D matrix multiplication
def gen3dMatrixMul(m1, m2):
    return np.matmul(m1, m2)

if __name__ == "__main__":
    ts1 = time.time()
    dim = 1024
    lower = 100
    upper = 1000
    for i in range(1):
        m1 = gen3dMatrix(dim, lower, upper)
        m2 = gen3dMatrix(dim, lower, upper)
        gen3dMatrixMul(m1, m2)

    print("====Time====")
    print(time.time() - ts1)