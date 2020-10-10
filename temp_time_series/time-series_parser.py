import pandas as pd
import re

def parse_temp(path):
    temp_dict = {
        "seq_no": [],
        "epoch": [],
        "timestamp": [],
        "ip": [],
        "temp": []
    }
    re_seqno = re.compile("seq_no: (\d*)")
    re_temp = re.compile("^\d*.\d*")
    re_epoch = re.compile("time: (\d*)")
    re_timestamp = re.compile("-- (.*)")
    re_ip = re.compile("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
    
    with open(path, "r") as f:
        for line in f:
            seqno = re_seqno.search(line).group(1)
            epoch = re_epoch.search(line).group(1)
            timestamp = re_timestamp.search(line).group(1)
            ip = re_ip.search(line).group(0)
            temp = re_temp.search(line).group(0)

            if seqno:
                temp_dict["seq_no"].append(seqno)
            if epoch:
                temp_dict["epoch"].append(epoch)
            if timestamp:
                temp_dict["timestamp"].append(timestamp)
            if ip:
                temp_dict["ip"].append(ip)
            if temp:
                temp_dict["temp"].append(temp)
    
    df = pd.DataFrame(data=temp_dict) 
    csv_path = path[0:-3] + "csv"
    df.to_csv(csv_path, index=False)

if __name__ == "__main__":
    # paths = ["./inc-4.lrec.temp.txt", "./Icloud-3.lrec.temp.txt", "lrec.temp.txt", "lrec2.temp.txt", "pi3-02.txt", "pizero-09.txt"]
    paths = ["./temp_thread2.txt"]
    for path in paths:
        parse_temp(path)