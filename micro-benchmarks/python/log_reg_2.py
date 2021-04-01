# Import required libraries :
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn import linear_model
import math
from sklearn.metrics import mean_squared_error, r2_score

df_t = pd.read_csv("./tensor-time-vs-max.csv")
df_mio = pd.read_csv("./matmul_io.csv")
df_mnist = pd.read_csv("./mnist.csv")

def log_reg(df_benchmark, df_target, header1, header2):
    #X, header1 = Time
    #Y, header2 = Temperature
    time_mio = df_benchmark[header1]
    temp_mio = np.log(df_benchmark[header2])

    time_t = df_target[header1]
    temp_t = np.log(df_target[header2])

    X = pd.concat([time_t, temp_mio], axis = 1)
    Y = temp_t

    regr = linear_model.LinearRegression()
    regr.fit(X, Y)

    print('Intercept: \n', regr.intercept_)
    print('Coefficients: \n', regr.coef_)
    

    # Plot the data :
    Y_plot = regr.predict(X)

    # Check the accuracy :
    print ("RMSE Y : {}".format(math.sqrt(mean_squared_error(Y, Y_plot))))
    Accuracy = r2_score(Y,Y_plot)
    print ("Y1 Accuracy: {}".format(Accuracy))


if __name__ == "__main__":
    log_reg(df_mio, df_t, "time1", "max1")
    log_reg(df_mio, df_t, "time2", "max2")
    log_reg(df_mio, df_t, "time3", "max3")