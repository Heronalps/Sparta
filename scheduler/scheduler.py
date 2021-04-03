import re, time, math
import numpy as np
import pandas as pd
from subprocess import Popen, PIPE
from multiprocessing import Process
from scipy.optimize import curve_fit
from sklearn.metrics import mean_squared_error, r2_score


df_t = pd.read_csv("./tensor-time-vs-max.csv")
df_mio = pd.read_csv("./matmul_io.csv")
df_mnist = pd.read_csv("./mnist.csv")

class Scheduler:
    def __init__(self, path=None, temp=None):
        self.temp = temp
        self.pkg_path = path
        self.model = {}
        self.exec = {
            "py"  : "python" ,
            "out" : "./"     , 
        }
        self.temp_log = []

    # Execute the program based on the suffix
    def _execute_(self):
        # Delay the execution for 1 second to make sure the starting temp is recorded    
        time.sleep(1)
        
        # capture the suffix of the program
        suffix = ''
        path = './'
        filename = ''
        match = re.search("\.(\w*)", self.pkg_path)
        if (match):
            suffix = match.group(1)
        
        match = re.search("(\/\w*)+(?!\w*\.\w*)", self.pkg_path)
        if (match):
            path = match.group(1)
        
        match = re.search("\w*\.\w*", self.pkg_path)
        if (match):
            filename = match.group(0)

        # print("suffix : {}".format(suffix))
        # print("path : {}".format(path))
        # print("filename : {}".format(filename))
        
        # self._log_temp_
        print ("exec starting")
        proc = Popen([self.exec[suffix], path + filename], stdout=PIPE, stderr=PIPE)
        stdout, stderr = proc.communicate()
        print (stdout.decode("utf-8"))
        print ("exec ending")


    # Adjust CPU performance given a frequency
    def _dvfs_(self, freq):
        proc = Popen(['./cpu_scaling', '-u', str(freq) + 'GHz'], stdin =PIPE, stdout=PIPE, stderr=PIPE)
        stdout, stderr = proc.communicate()
        print (stdout.decode("utf-8"))


    # Log temperature during execution to optimize the existing model
    def _log_temp_(self, log_path=None):
        print ("log_temp starting")
        
        # proc = Popen(['bash', 'record_temp.sh', log_path], stdout=PIPE, stderr=PIPE)
        # stdout, stderr = proc.communicate()
        # print (stdout.decode("utf-8"))
        # Read temperature of current execution
        while (True):
            proc = Popen(["sensors"], stdout=PIPE, stderr=PIPE)
            stdout, stderr = proc.communicate()
            stdout = stdout.decode("utf-8")
            match = re.search("Package\sid\s0:\s*\+([0-9]*\.[0-9])", stdout)
            if (match):
                self._log_temp_.append(match.group(1))
            print (self.temp_log)
            time.sleep(1)


    # Regress on logged data and return a recommanded frequency based on the regression
    def _extrapolate_(self, temp, data_path=None):
        pass


    # Update the model based on the last run
    def _update_model_(self):
        pass

    # Linear regression on the dfvs frequency by temperature threshold
    # a + b * [log(temp_target) - log(temp_start)] = Freq
    def _log_regress_(self, df_benchmark, df_target, header1, header2):
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

        print('Intercept: {}\n'.format(regr.intercept_))
        print('Coefficients: {}\n'.format(regr.coef_))

        # Plot the data :
        Y1_plot = regr.predict(X1)
        Y2_plot = regr.predict(X2)

        print ("RMSE Y1 : {}".format(math.sqrt(mean_squared_error(Y1, Y1_plot))))
        print ("RMSE Y2 : {}".format(math.sqrt(mean_squared_error(Y2, Y2_plot))))

        # Check the accuracy :
        Accuracy1 = r2_score(Y1,Y1_plot)
        Accuracy2 = r2_score(Y2,Y2_plot)
        print ("Y1 Accuracy: {}".format(Accuracy1))
        print ("Y2 Accuracy: {}".format(Accuracy2))
        print ("========================")

        return regr

    # Run scheduler
    def run(self):
        proc_exec = Process(target=self._execute_)
        proc_exec.start()

        proc_log = Process(target=self._log_temp_, args=("log_path", ))
        proc_log.start()

        prog_dvfs = Process(target=self._dvfs_, args=("1.2", ))
        prog_dvfs.start()
        prog_dvfs.join()
        
        # Terminate temp monitor when execution finishes
        if (proc_exec.join() is None):
            proc_log.terminate()
            print ("log_temp ending")


s = Scheduler("main.py", 75)
s.run()
