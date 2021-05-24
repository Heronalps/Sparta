import re, time, math, random, threading
import numpy as np
import pandas as pd
from subprocess import Popen, PIPE
from multiprocessing import Process
from threading import Thread       
from scipy.optimize import curve_fit
from sklearn import linear_model
from sklearn.metrics import mean_squared_error, r2_score

# The number of seconds every regression and model calibration happens
CALIBRATION_PERIOD = 5

# K Increment after every run
INCREMENT = 0.5

# Regression dataset headers
X_HEADER = "max2"
Y_HEADER = "Freq"

# The resolution of addition in AIMD
# 0.1 => 100MHz
A_FACTOR = 0.07
M_FACTOR = 0.7

# The window size of sampling max temp in AIMD
WINDOW_SIZE = 4

# The left boundary of acceptable temperature
LEFT_BOUND = 5

# Time stamp of start
START = time.time()

df_t = pd.read_csv("./data/tensor-time-vs-max.csv")
df_mio = pd.read_csv("./data/matmul_io.csv")
df_mnist = pd.read_csv("./data/mnist.csv")

# Thread lock for hybrid mode
LOCK = threading.Lock()
        

class Scheduler:
    def __init__(self, pkg_path=None, log_path=None, temp=None, mode=1):    
        
        # The thread flag indicating either annealing or AIMD is running
        # 1 => Annealing & AIMD Entrance => (Annealing, AIMD) acquire lock 
        # 2 => Annealing While Iteration => (AIMD) acquire lock
        # 3 => AIMD While Iteration => (Annealing) acquire lock 
        self.thread_flag = 1

        self.temp_threshold = temp
        self.temp_start = None
        self.pkg_path = pkg_path
        self.log_path = log_path
        self.model = None
        self.freq = None
        
        # Feature flag among [1=>Annealing, 2=>AIMD, 3=>Hybrid]
        self.mode = mode
        
        # The initial freq from historical data extrapolation
        # This is used as the upper boundary of exploration
        self.freq_init = None
        
        # Real time data log - max temperature & temp time series
        self.temp_log_curr = []
        self.temp_log_all = []
        self.max_temp_log = []
        self.max_temp_log_cache = []
        self.freq_set = set()
        
        # The on/off flag for scheduler 
        self.flag = True

        # Two variables for annealing
        self.k = 1.0
        self.epsilon = 1.0

        # Mapping max temperature => freq
        self.max_temp_freq_map = {}

        # Control while true thread
        self.stop_threads = False

        self.exec = {
            "py"  : "python" ,
            "out" : ""       , 
        }

    def _reset_(self):
        self.flag = True
        self.epsilon = 1.0
        self.k = 1.0
        # self.max_temp_freq_map.clear()
        # self.freq_set.clear()
        # self.max_temp_log_cache.clear()

        
    def __repr__(self):
        return "======\nthreshold: {0} \ntemp_start : {1} \nmodel : {2} \nfreq : {3} \ntemp_log_all : {4} \n======\n ".format(
                self.temp_threshold, self.temp_start, self.model, self.freq, self.temp_log_all[:])

    # Execute the program based on the suffix
    def _execute_(self): 
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
        proc = Popen([cmd], shell=True, cwd=path.encode('unicode_escape'), stdout=PIPE, stderr=PIPE)
        stdout, stderr = proc.communicate()
        # print (stdout.decode("utf-8"))
        print ("exec ending")
           

    # Wrap function of log_temp in order to flush temp log data
    def _log_temp_realtime_(self, times=math.inf): 
        while(times):
            times -= 1
            self._log_temp_()
            time.sleep(1)
            if self.stop_threads:
                break


    # Log temperature during execution to optimize the existing model
    def _log_temp_(self): 
        # Read temperature of current execution
        proc = Popen(["sensors"], stdout=PIPE, stderr=PIPE)
        stdout, stderr = proc.communicate()
        stdout = stdout.decode("utf-8")
        match = re.search("Package\sid\s0:\s*\+([0-9]*\.[0-9])", stdout)
        temp = float(match.group(1))
        
        if (match):
            self.temp_log_curr.append(temp)
            self.temp_log_all.append(temp)
            
            # Record the starting temperature
            if (self.temp_start is None):
                self.temp_start = temp

        if (len(self.temp_log_curr) >= CALIBRATION_PERIOD):
            log_temp_delta = np.log(max(self.temp_log_curr)) - np.log(self.temp_start)
            
            # Log the current max temp
            self.max_temp_log.append(max(self.temp_log_curr))
            self.max_temp_log_cache.append(max(self.temp_log_curr))
            
            '''
            # Perturb temperature delta to prevent duplicate data point 
            log_temp_delta -= random.uniform(1e-7, 1e-6)
            # Perturb the designated frequency to secure at least two data points for regression
            self.freq -= random.uniform(1e-7, 1e-6)
            '''

            self.freq_set.add(self.freq)
            self.max_temp_freq_map[log_temp_delta] = self.freq
            self.temp_log_curr.clear()  
            # print ("TEMP DELTA: {} Freq : {}".format(self.max_temp_freq_map.keys(), self.max_temp_freq_map.values()))
       
        
    # Log temperature in the file system
    def _log_temp_file_(self):
        proc = Popen(['exec', 'bash', 'record_temp.sh', self.log_path], stdout=PIPE, stderr=PIPE, shell=True)
        proc.communicate()


    def retrieve_data_from_dataframe(self, df_benchmark, df_target, header1, header2):
        # X = [log(temp_target) - log(start_temp)]
        # Y = Freq
        X1 = np.log(df_benchmark[header2]) - np.log(df_benchmark[header2][0])
        Y1 = df_benchmark[header1] 

        X2 = np.log(df_target[header2]) - np.log(df_target[header2][0])
        Y2 = df_target[header1] 

        return X1, X2, Y1, Y2


    def retrieve_data_from_map(self):
        X1 = np.asarray(list(self.max_temp_freq_map.keys()))
        Y1 = np.asarray(list(self.max_temp_freq_map.values()))
        return X1, Y1


    def _extrapolate_realtime_(self):
        global LOCK
        
        while(True):
            if self.mode == 3 and self.thread_flag != 2:
                LOCK.acquire()
                self.thread_flag = 2

            print ("Max temp log : {}".format(self.max_temp_log))
            print ("All temp log : {}".format(self.temp_log_all))
            if (len(self.temp_log_all) >= WINDOW_SIZE):

                last_segment_temp_greater = [t > self.temp_threshold + 1 for t in self.temp_log_all[-WINDOW_SIZE:]]
                # print ("Last segment temp greater: {}".format(last_segment_temp_greater))

                if self.mode == 3 and all(last_segment_temp_greater):
                    
                    # Change thread flag to AIMD
                    self.thread_flag = 1
                    
                    LOCK.release()
                    
                    # Sleep to let AIMD thread pick up lock
                    time.sleep(5)
                    
                    continue

                last_segment_temp = [t > self.temp_threshold or t < self.temp_threshold - LEFT_BOUND for t in self.temp_log_all[-WINDOW_SIZE*2:]]
                # print ("Last segment temp : {}".format(last_segment_temp))

                # If any last segment temps are out of scope of [threshold - LEFT_BOUND, threshold]
                if all(last_segment_temp):
                   
                    # reset Threshold and self.k for Annealing
                    if not self.flag:
                        self._reset_()
                        print ("======Scheduler Wakes up=======")
                        print () 
                # All temps are in the scope
                # if not any(last_segment_temp):
                
                # Any one in the scope
                else:
                    # Scheduler goes to hibernate until anomaly detected
                    if self.flag:
                        print ("******Annealing stablized in {} seconds*******".format(time.time() - START))
                        print ()
                        self.flag = False
            

            # If all last ten temps are out of scope, we assume it stuck at local minimum
            if (len(self.temp_log_all) >= WINDOW_SIZE * 3):
                last_ten_temp = [t < self.temp_threshold - LEFT_BOUND for t in self.temp_log_all[-WINDOW_SIZE*3:]]
                # print ("Last Ten Temp : {}".format(last_ten_temp)) 
                # Reset scheudler
                if all(last_ten_temp):
                    self._reset_()            

            if (self.flag):
                self._extrapolate_()
                self.k += INCREMENT

            if self.stop_threads:
                break
            
           
            # Rebuild regression model every a few seconds on new data points 
            time.sleep(CALIBRATION_PERIOD)
            


    # Regress against logged data
    # Update self.freq based on temperature threshold
    # Adjust CPU performance given the self.freq
    def _extrapolate_(self):
        log_temp_delta = [[np.log(self.temp_threshold) - np.log(self.temp_start)]]
        p = np.random.random()
        threshold = self.epsilon / self.k
        if p < threshold and self.freq_init is not None:
            print ("P : {} Threshold : {}".format(p, threshold))
            # To guarantee the new freq would not lead to a excessive temperature over threshold
            # The recorded log is still good to extrapolate (not intrapolate) the regression
            self.freq = random.uniform(0.8, self.freq_init)
            # self.freq = random.uniform(0.8, 3.5)

        # Regression based on historical data, which is guaranteed in first few extrapolations
        elif len(self.max_temp_freq_map) < 3:
            X1, X2, Y1, Y2 = self.retrieve_data_from_dataframe(df_mio, df_t, Y_HEADER, X_HEADER)
            self.model = self._log_regress_(X1, Y1, X2, Y2)
            self.freq = self.model.predict(log_temp_delta)[0]
            if self.freq_init is None:
                self.freq_init = self.freq
        
           
        # Build regression model based on real time data if it has at least two data points
        else:
            X1, Y1 = self.retrieve_data_from_map()
            self.model = self._log_regress_(X1, Y1)    
            freq = self.model.predict(log_temp_delta)[0]
            if (freq >= 0.8 and freq <= 3.5):
                self.freq = freq
           
        while(self.temp_start is None):
            time.sleep(0.5)
        
        self._modify_freq_()  
   

    def _aimd_realtime_(self):

        # Set up initial frequency
        if self.freq == None:
            self._extrapolate_()
        
        global LOCK
        
        while(True):
            if self.mode == 3 and self.thread_flag != 3: 
                # Acquire thread lock when Annealing releases
                LOCK.acquire()
                self.thread_flag = 3

            
            print ("Realtime Curr Temp Log : {}".format(self.temp_log_all))
            
            # Capture conservative local minimum 
            if len(self.temp_log_all) > WINDOW_SIZE * LEFT_BOUND:
                # All temps in window are 5 degrees below threshold
                last_segment_temp_less = [t < self.temp_threshold - LEFT_BOUND for t in self.temp_log_all[-WINDOW_SIZE * LEFT_BOUND:]]
                
                if all(last_segment_temp_less):
                    self._aimd_()
                    if self.mode == 3:
                        self.thread_flag = 1
                        LOCK.release()
                        time.sleep(1)
                    continue

            # All temps in window are larger than threshold
            last_segment_temp = [t > self.temp_threshold for t in self.temp_log_all[-WINDOW_SIZE:]]
            
            # Start AIMD mode if all temps in window are above threshold
            if any(last_segment_temp):
                self._aimd_()
                if self.mode == 3:
                    self.thread_flag = 1
                    LOCK.release()
                    time.sleep(1)
                continue

            # All temps in window are larger than threshold by 5 degrees
            last_segment_temp_greater = [t >= self.temp_threshold + 5 for t in self.temp_log_all[-WINDOW_SIZE:]]

            # Start AIMD mode if any temps in window are above threshold + 5 
            if any(last_segment_temp_greater):
                self._aimd_()
                if self.mode == 3:
                    self.thread_flag = 1
                    LOCK.release()
                    time.sleep(1)
                continue

            time.sleep(WINDOW_SIZE)


    def _aimd_(self):
       
        print ("Start AIMD...")

        # Multiplicative Decrease
        while (True):

            # print ("Temp log all : {}".format(self.temp_log_all[-WINDOW_SIZE * 2:]))            
            last_segment_temp = [t > self.temp_threshold for t in self.temp_log_all[-WINDOW_SIZE * 2:]]
            
            if any(last_segment_temp): 
                self.freq *= M_FACTOR
                self._modify_freq_()    
            
            else:
                break
            
            time.sleep(WINDOW_SIZE * 2)
        

        # Additive Increase
        while (True):
    
            # print ("AIMD Curr Temp Log : {}".format(self.temp_log_curr))

            # All temps in window are within [threshold - LEFT_BOUND, threshold] 
            last_segment_temp = [t <= self.temp_threshold and t >= self.temp_threshold - LEFT_BOUND for t in self.max_temp_log[-WINDOW_SIZE:]]
            last_segment_temp_greater = [t > self.temp_threshold for t in self.temp_log_all[-WINDOW_SIZE:]]            
            
            # print ("Last Segment in scope: {}".format(last_segment_temp))
            # print ("Last Segment Greater : {}".format(last_segment_temp_greater))

            # Stop Additive Increase if all temps are in scope
            if all(last_segment_temp):
                print ("======AIMD Stablize in {} seconds======".format(time.time() - START))
                                
                # Change thread flag to Annealing
                self.thread_flag = 1

                time.sleep(1)

                break

            if all(last_segment_temp_greater):
                print ("Overkill")
                self.freq *= M_FACTOR
                self._modify_freq_()
                time.sleep(WINDOW_SIZE)
                continue
            
            # Additive increase when no temps are in the scope
            # This is a strategy to prevent overkill
            if not any(last_segment_temp):
                self.freq += A_FACTOR
                self._modify_freq_()

            time.sleep(WINDOW_SIZE)


    def _modify_freq_(self):
        if self.freq >= 0.8 and self.freq <= 3.5:
            print ("Modifying freq : {}".format(self.freq))
            proc = Popen(['./cpu_scaling', '-u', str(self.freq) + 'GHz'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
            stdout, stderr = proc.communicate()


    # Linear regression on the dfvs frequency by temperature threshold
    # a + b * [log(temp_target) - log(temp_start)] = Freq
    # Returns a regression model for extrapolation
    def _log_regress_(self, X1, Y1, X2=None, Y2=None):
        # Reshape from [X, ] to [X, 1]
        
        if isinstance(X1, pd.core.series.Series):
            X1 = X1.to_numpy()[:, np.newaxis]
        elif X1 is not None:
            X1 = X1[:, np.newaxis]
        
        if isinstance(X2, pd.core.series.Series):
            X2 = X2.to_numpy()[:, np.newaxis]
        elif X2 is not None:
            X2 = X2[:, np.newaxis]

        regr = linear_model.LinearRegression()
        regr.fit(X1, Y1)

        # print('Intercept: {}\n'.format(regr.intercept_))
        # print('Coefficients: {}\n'.format(regr.coef_))

        # Plot the data :
        Y1_plot = regr.predict(X1)
        Accuracy1 = r2_score(Y1, Y1_plot)
        # print ("RMSE Y1 : {}".format(math.sqrt(mean_squared_error(Y1, Y1_plot))))
        # print ("Y1 Accuracy: {}".format(Accuracy1))
        if (X2 is not None and Y2 is not None):
            Y2_plot = regr.predict(X2)
            Accuracy2 = r2_score(Y2, Y2_plot)
            # print ("RMSE Y2 : {}".format(math.sqrt(mean_squared_error(Y2, Y2_plot))))
            # print ("Y2 Accuracy: {}".format(Accuracy2))
        # print ("========================")

        return regr

    # Run scheduler
    def run(self):

        self.stop_threads = False

        proc_log_temp_rt = Thread(target=self._log_temp_realtime_)
        proc_log_temp_rt.daemon = True
        proc_log_temp_rt.start()

        proc_log_temp_f = Process(target=self._log_temp_file_)
        proc_log_temp_f.daemon = True
        proc_log_temp_f.start()

        # Delay extrapolate for 1 second to log temp_start
        time.sleep(1)
       
        # Annealing mode
        if self.mode == 1:
            thread_annealing = Thread(target=self._extrapolate_realtime_)
            thread_annealing.daemon = True
            thread_annealing.start()
       
        # AIMD mode
        elif self.mode == 2:
            thread_AIMD = Thread(target=self._aimd_realtime_)
            thread_AIMD.daemon = True
            thread_AIMD.start()
        
        # Hybrid mode
        else:
            thread_annealing = Thread(target=self._extrapolate_realtime_)
            thread_annealing.daemon = True
            thread_AIMD = Thread(target=self._aimd_realtime_)
            thread_AIMD.daemon = True

            thread_annealing.start()
            thread_AIMD.start()


        '''
        # Delay the execution for 1  second to make sure the starting temp is recorded    
        time.sleep(1)

        proc_exec = Process(target=self._execute_)
        proc_exec.start()

        # Terminate temp monitor when execution finishes
        
        if (proc_exec.join() is None):
            self.stop_threads = True
            proc_log_temp_rt.join()
            proc_extrapolate.join()
            proc_log_temp_f.terminate()

        
        time.sleep(1)
        '''
