# Import required libraries :
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import math
from sklearn.metrics import mean_squared_error
from sklearn import linear_model

df_t = pd.read_csv("./tensor-time-vs-max.csv")
df_mio = pd.read_csv("./matmul_io.csv")
df_mnist = pd.read_csv("./mnist.csv")

def log_func(x, a, b):
    return a + b * x

def log_reg(df1, df2, header1, header2):
    #X = [log(temp_target) - log(start_temp)]
    #Y = Freq
    X1 = np.log(df1[header2]) - np.log(df1[header2][0])
    Y1 = df1[header1] 

    X2 = np.log(df2[header2]) - np.log(df2[header2][0])
    Y2 = df2[header1] 

    X1 = X1[:, np.newaxis]
    X2 = X2[:, np.newaxis]

    regr = linear_model.LinearRegression()
    regr.fit(X1, Y1)

    print('Intercept: \n', regr.intercept_)
    print('Coefficients: \n', regr.coef_)

    # Plot the data :
    Y1_plot = regr.predict(X1)
    Y2_plot = regr.predict(X2)

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
    log_reg(df_mio, df_t, "Freq", "max1")
    log_reg(df_mio, df_t, "Freq", "max2")
    log_reg(df_mio, df_t, "Freq", "max3")