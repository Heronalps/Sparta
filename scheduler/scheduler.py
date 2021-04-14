import re, time, math, random
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

# The number of seconds every regression and model calibration happens
CALIBRATION_PERIOD = 30
X_HEADER = "max2"
Y_HEADER = "Freq"

class Scheduler:
    def __init__(self, pkg_path=None, log_path=None, temp=None):
        self.temp_threshold = temp
        self.temp_start = None
        self.pkg_path = pkg_path
        self.log_path = log_path
        self.model = None
        self.freq = None
        # Real time data log - max temperature & temp time series
        self.temp_log_curr = []
        self.temp_log_all = []
        # Mapping max temperature => freq
        self.max_temp_freq_map = {}

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
            

    # Log temperature during execution to optimize the existing model
    def _log_temp_(self):
        while (True):
            # Read temperature of current execution
            proc = Popen(["sensors"], stdout=PIPE, stderr=PIPE)
            stdout, stderr = proc.communicate()
            stdout = stdout.decode("utf-8")
            match = re.search("Package\sid\s0:\s*\+([0-9]*\.[0-9])", stdout)
            temp = float(match.group(1))
            if (match):
                self.temp_log_curr.append(temp)
                print (self.temp_log)
                # Record the starting temperature
                if (self.temp_start is None):
                    self.temp_start = temp

            if (len(self.temp_log_curr) >= CALIBRATION_PERIOD):
                self.temp_log_all.extend(self.temp_log_curr)
                log_temp = np.log(max(self.temp_log_curr)) - np.log(self.temp_start)
                self.max_temp_freq_map[log_temp] = self.freq
                self.temp_log_curr.clear()
        
            time.sleep(1)
        
        
    # Log temperature in the file system
    def _log_temp_file_(self):
        # print ("Logging temp in file")
        proc = Popen(['exec', 'bash', 'record_temp.sh', self.log_path], stdout=PIPE, stderr=PIPE, shell=True)
        proc.communicate()


    def retrieve_data_from_dataframe(self, df_benchmark, df_target, header1, header2):
        #X = [log(temp_target) - log(start_temp)]
        #Y = Freq
        X1 = np.log(df_benchmark[header2]) - np.log(df_benchmark[header2][0])
        Y1 = df_benchmark[header1] 

        X2 = np.log(df_target[header2]) - np.log(df_target[header2][0])
        Y2 = df_target[header1] 

        X1 = X1.to_numpy()[:, np.newaxis]
        X2 = X2.to_numpy()[:, np.newaxis]
        return X1, X2, Y1, Y2


    def retrieve_data_from_map(self):
        X1 = np.asarray(list(self.max_temp_freq_map.keys()))
        Y1 = np.asarray(list(self.max_temp_freq_map.values()))
        return X1, Y1

    # Regress against logged data
    # Update self.freq based on temperature threshold
    # Adjust CPU performance given the self.freq
    def _extrapolate_(self, eps=0.1):
        times = 1
        while(True):
            p = np.random.random()
            threshold = eps/times
            # Regression based on historical data, which is guaranteed in first few extrapolations
            if len(self.max_temp_freq_map) <= 2:
                X1, X2, Y1, Y2 = self.retrieve_data_from_dataframe(df_mio, df_t, Y_HEADER, X_HEADER)
                self.model = self._log_regress_(X1, X2, Y1, Y2)
                self.freq = self.model.predict([[np.log(self.temp_threshold) - np.log(self.temp_start)]])[0]
            
            elif p < threshold:
                self.freq = random.uniform(0.8, 3.5)
            
            # Build regression model based on real time data if it has at least two data points
            else:
                X1, Y1 = self.retrieve_data_from_map()
                self.model = self._log_regress_(X1, Y1)
                self.freq = self.model.predict([[np.log(self.temp_threshold) - np.log(self.temp_start)]])[0]
            
            times += 1

            # self.freq += 0.35
            proc = Popen(['./cpu_scaling', '-u', str(self.freq) + 'GHz'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
            stdout, stderr = proc.communicate()
            # print (stdout.decode("utf-8"))
            
            # Rebuild regression model every 60 seconds on two new data points 
            time.sleep(CALIBRATION_PERIOD * 2)


    # Linear regression on the dfvs frequency by temperature threshold
    # a + b * [log(temp_target) - log(temp_start)] = Freq
    # Returns a regression model for extrapolation
    def _log_regress_(self, X1, Y1, X2=None, Y2=None):
        regr = linear_model.LinearRegression()
        regr.fit(X1, Y1)

        print('Intercept: {}\n'.format(regr.intercept_))
        print('Coefficients: {}\n'.format(regr.coef_))

        # Plot the data :
        Y1_plot = regr.predict(X1)
        print ("RMSE Y1 : {}".format(math.sqrt(mean_squared_error(Y1, Y1_plot))))
        Accuracy1 = r2_score(Y1,Y1_plot)
        print ("Y1 Accuracy: {}".format(Accuracy1))
        if X2 and Y2:
            Y2_plot = regr.predict(X2)
            print ("RMSE Y2 : {}".format(math.sqrt(mean_squared_error(Y2, Y2_plot))))
            Accuracy2 = r2_score(Y2, Y2_plot)
            print ("Y2 Accuracy: {}".format(Accuracy2))
        print ("========================")

        return regr

    # Run scheduler
    def run(self):
        proc_log_temp_rt = Thread(target=self._log_temp_)
        proc_log_temp_rt.daemon = True
        proc_log_temp_rt.start()
        
        proc_log_temp_f = Process(target=self._log_temp_file_)
        proc_log_temp_f.daemon = True
        proc_log_temp_f.start()

        proc_extrapolate = Thread(target=self._extrapolate_)
        proc_extrapolate.daemon = True
        proc_extrapolate.start()

        proc_exec = Process(target=self._execute_)
        proc_exec.start()

        # Terminate temp monitor when execution finishes
        if (proc_exec.join() is None):
            proc_log_temp_f.terminate()
            proc_extrapolate.terminate()
