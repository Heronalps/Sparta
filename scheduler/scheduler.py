import re, time, math
import numpy as np
import pandas as pd
from subprocess import Popen, PIPE
from multiprocessing import Process
from threading import Thread       
from scipy.optimize import curve_fit
from sklearn import linear_model
from sklearn.metrics import mean_squared_error, r2_score


df_t = pd.read_csv("./data/tensor-time-vs-max.csv")
df_mio = pd.read_csv("./data/matmul_io.csv")
df_mnist = pd.read_csv("./data/mnist.csv")

class Scheduler:
    def __init__(self, pkg_path=None, log_path=None, temp=None):
        self.temp_threshold = temp
        self.temp_start = None
        self.pkg_path = pkg_path
        self.log_path = log_path
        self.model = None
        self.freq = None
        self.temp_log = []
        self.exec = {
            "py"  : "python" ,
            "out" : ""       , 
        }
        
    def __repr__(self):
        return "======\nthreshold: {0} \ntemp_start : {1} \nmodel : {2} \nfreq : {3} \ntemp_log : {4} \n======\n ".format(
                self.temp_threshold, self.temp_start, self.model, self.freq, self.temp_log[:])

    # Execute the program based on the suffix
    def _execute_(self):
        # Delay the execution for 1 second to make sure the starting temp is recorded    
        time.sleep(1)
        
        # capture the suffix of the program
        suffix = ''
        path = './'
        filename = ''
        match = re.search("^(.*\/)(\w*\.(\w*))", self.pkg_path)
        if (match):
            path = match.group(1)
            filename = match.group(2)
            suffix = match.group(3)
        
        # print("suffix : {}".format(suffix))
        # print("path : {}".format(path))
        # print("filename : {}".format(filename))
        
        # self._log_temp_
        print ("exec starting")
        # shell=True executes commands through bash shell
        cmd = self.exec[suffix] + ' ' + filename
        # print (cmd)
        proc = Popen([cmd], shell=True, cwd=path.encode('unicode_escape'), stdout=PIPE, stderr=PIPE)
        stdout, stderr = proc.communicate()
        print (stdout.decode("utf-8"))
        print ("exec ending")


    # Adjust CPU performance given the self.freq
    def _dvfs_(self):
        proc = Popen(['./cpu_scaling', '-u', str(self.freq) + 'GHz'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        stdout, stderr = proc.communicate()
        # print (stdout.decode("utf-8"))


    def _log_temp_realtime_(self, times=math.inf):
        while (times):
            self._log_temp_()
            time.sleep(1)
            times -= 1

    # Log temperature during execution to optimize the existing model
    def _log_temp_(self):
        
        # Read temperature of current execution
        proc = Popen(["sensors"], stdout=PIPE, stderr=PIPE)
        stdout, stderr = proc.communicate()
        stdout = stdout.decode("utf-8")
        match = re.search("Package\sid\s0:\s*\+([0-9]*\.[0-9])", stdout)
        temp = float(match.group(1))
        if (match):
            self.temp_log.append(temp)
        return temp
        
        
    # Log temperature in the file system
    def _log_temp_file_(self):
        # print ("Logging temp in file")
        proc = Popen(['exec', 'bash', 'record_temp.sh', self.log_path], stdout=PIPE, stderr=PIPE, shell=True)
        proc.communicate()


    # Regress against logged data
    # Update self.freq based on temperature threshold
    def _extrapolate_(self):
        self.model = self._log_regress_(df_mio, df_t, "Freq", "max2")
        self.freq = self.model.predict([[np.log(self.temp_threshold) - np.log(self.temp_start)]])[0]
        self.freq += 0.35

    # Linear regression on the dfvs frequency by temperature threshold
    # a + b * [log(temp_target) - log(temp_start)] = Freq
    # Returns a regression model for extrapolation
    def _log_regress_(self, df_benchmark, df_target, header1, header2):
        #X = [log(temp_target) - log(start_temp)]
        #Y = Freq
        X1 = np.log(df_benchmark[header2]) - np.log(df_benchmark[header2][0])
        Y1 = df_benchmark[header1] 

        X2 = np.log(df_target[header2]) - np.log(df_target[header2][0])
        Y2 = df_target[header1] 

        X1 = X1.to_numpy()[:, np.newaxis]
        X2 = X2.to_numpy()[:, np.newaxis]

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
        # Record the starting temperature
        self.temp_start = self._log_temp_()

        # Update model and designated frequency
        self._extrapolate_()
        self._dvfs_()

        proc_log_temp_rt = Thread(target=self._log_temp_realtime_)
        proc_log_temp_rt.daemon = True
        proc_log_temp_rt.start()
        
        proc_log_temp_f = Process(target=self._log_temp_file_)
        proc_log_temp_f.daemon = True
        proc_log_temp_f.start()

        proc_exec = Process(target=self._execute_)
        proc_exec.start()

        # Terminate temp monitor when execution finishes
        if (proc_exec.join() is None):
            proc_log_temp_f.terminate()
