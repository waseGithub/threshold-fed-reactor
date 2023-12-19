import serial.tools.list_ports
import pandas as pd
from datetime import datetime
import os 
from reactor_controll import time_check

board_serial_number = '95131333137351D091D0'  
port = None


#check check check
ports = list(serial.tools.list_ports.comports())
for p in ports:
    print(p.serial_number)
    if p.serial_number == board_serial_number:
        port = p.device
        break

if port is None:
    print(f"Arduino board with serial number {board_serial_number} not found.")
    exit()

board_baud_rate = 38400
ser = serial.Serial(port, board_baud_rate)

# CSV file path
csv_file = 'mega_data.csv'
################
# Read data from Arduino
data_dict = {}
time_checker1 = time_check()
while True:
    if ser.in_waiting > 0:
        line = ser.readline().decode('utf-8').rstrip()


        lines = line.split('\n')
        for line in lines:
            line = line.strip()
      
            if line:
                key, value = line.split(':', 2)
                key = key.strip()
                value = value.strip()
                data_dict[key] = value
            
        
        data_dict['datetime'] = str(datetime.now())
        if '' in data_dict:
            del data_dict['']

        
        #check

        data_log_time_check = 0.1
        if time_checker1.has_passed_minutes(data_log_time_check):
            print(data_dict)
            time_checker1.reset()
            if len(data_dict) == 4:

                df = pd.DataFrame(data_dict, index=[data_dict['datetime']])
                df = df.drop('datetime', axis=1)
                df = df.rename_axis('datetime')
                
                # df = df.drop('alue', axis=1)
                
                

                # Append DataFrame to CSV if the file is empty
                if not os.path.isfile(csv_file) or os.stat(csv_file).st_size == 0:
                    df.to_csv(csv_file, mode='w', header=True)
                else:
                    df.to_csv(csv_file, mode='a', header=False)