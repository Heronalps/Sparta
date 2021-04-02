import subprocess, re, time
from multiprocessing import Process

class Scheduler:
    def __init__(self, path=None, temp=None):
        self.temp = temp
        self.pkg_path = path
        self.model = {}
        self.exec = {
            "py"  : "python" ,
            "out" : "./"     , 
        }

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
        proc = subprocess.Popen([self.exec[suffix], path + filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        print (stdout.decode("utf-8"))
        print ("exec ending")


    # Adjust CPU performance given a frequency
    def _dvfs_(self, freq):
        proc = subprocess.Popen(['./cpu_scaling', '-u', str(freq) + 'GHz'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        print (stdout.decode("utf-8"))


    # Log temperature during execution to optimize the existing model
    def _log_temp_(self, log_path=None):
        print ("log_temp starting")
        proc = subprocess.Popen(['bash', 'record_temp.sh', log_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        print (stdout.decode("utf-8"))
        print ("log_temp ending")


    # Regress on logged data and return a recommanded frequency based on the regression
    def _extrapolate_(self, temp, data_path=None):
        pass


    # Update the model based on the last run
    def _update_model_(self):
        pass


    # Run scheduler
    def run(self):
        proc_exec = Process(target=self._execute_)
        proc_exec.start()

        proc_log = Process(target=self._log_temp_, args=("path", ))
        proc_log.start()

        proc_exec.join()
        proc_log.join()



s = Scheduler("main.py", 75)
s.run()
