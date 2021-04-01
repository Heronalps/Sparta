# Import required libraries :
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import math
from sklearn.metrics import mean_squared_error

df_t = pd.read_csv("./tensor-time-vs-max.csv")
df_mio = pd.read_csv("./matmul_io.csv")
df_mnist = pd.read_csv("./mnist.csv")

def log_func(x, a, b):
    return a + b * x

def log_reg(df1, df2, header1, header2):
    #X = Time
    #Y = Temperature
    X1 = df1[header1]
    Y1 = np.log(df1[header2])

    X2 = df2[header1]
    Y2 = np.log(df2[header2])

    popt, pcov = curve_fit(log_func, X1, Y1)
    print ("a = {}".format(popt[0]))
    print ("b = {}".format(popt[1]))

    # Plot the data :
    Y1_plot = log_func(X1, popt[0], popt[1])
    Y2_plot = log_func(X2, popt[0], popt[1])

    # plt.scatter(X1, Y1, label="Time vs Max Temp")
    # plt.plot(X1, Y1_plot, 'r-')
    # plt.xlabel("Time")
    # plt.ylabel("Temp")
    # plt.show()

    print ("RMSE Y1 : {}".format(math.sqrt(mean_squared_error(Y1, Y1_plot))))
    print ("RMSE Y2 : {}".format(math.sqrt(mean_squared_error(Y2, Y2_plot))))

    # Check the accuracy :
    from sklearn.metrics import r2_score
    Accuracy = r2_score(Y1,Y1_plot)
    print ("Y1 Accuracy: {}".format(Accuracy))

    Accuracy = r2_score(Y2,Y2_plot)
    print ("Y2 Accuracy: {}".format(Accuracy))
    print ("========================")

if __name__ == "__main__":
    log_reg(df_mio, df_t, "time1", "max1")
    log_reg(df_mio, df_t, "time2", "max2")
    log_reg(df_mio, df_t, "time3", "max3")