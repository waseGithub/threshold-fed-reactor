import serial.tools.list_ports
import pandas as pd
from datetime import datetime
import os 
# from reactor_controll import TrendGradientCalculator
from reactor_controll import TimeCheck
from reactor_controll import Control
import numpy as np
import json
import math


board_serial_number = 'AF0F89C75339473237202020FF194333'  
port = None

ports = list(serial.tools.list_ports.comports())
for p in ports:
    print(p.serial_number)
    if p.serial_number == board_serial_number:
        port = p.device
        break

if port is None:
    print(f"Arduino board with serial number {board_serial_number} not found.")
    exit()

board_baud_rate = 115200
ser = serial.Serial(port, board_baud_rate)

# CSV file path
csv_file = 'adalogger_data.csv'



# Read data from Arduino
control = Control()
data_dict = {}
gradient_dict = {}
time_checker1 = TimeCheck()
time_checker2 = TimeCheck()
time_checker3 = TimeCheck()
latest_gradient = 0 
while True:
 
    if ser.in_waiting > 0:
        line = ser.readline().decode('utf-8').rstrip()

        lines = line.split('\n')
        for line in lines:
            line = line.strip()
    
            if line:
                try:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    data_dict[key] = value
                except ValueError:
                    pass
                
        
        data_dict['datetime'] = str(datetime.now())
        data_log_time_check = 0.1
        feedrate_time_check =0.5
        pump_does_time_check = 3

        


        if time_checker1.has_passed_minutes(data_log_time_check):
            time_checker1.reset()
            


    
            if len(data_dict) == 6:

                print(data_dict)

                df = pd.DataFrame(data_dict, index=[data_dict['datetime']])
                df = df.drop('datetime', axis=1)
                df = df.rename_axis('datetime') 
                
                
                if not os.path.isfile(csv_file) or os.stat(csv_file).st_size == 0:
                    df.to_csv(csv_file, mode='w', header=True)
                else:
                    df.to_csv(csv_file, mode='a', header=False)

                

                df = pd.read_csv(csv_file)
                
                df['A Current'] = df['A Current'].str.replace(' mA', '').astype(float)
                if len(df) >= 30:
                
                    current_now = df['A Current'].tail(6).mean()
                else: 
                    print('length check fail')
                    current_now = 0
            
            else:
                print(data_dict)

            

        
            if time_checker2.has_passed_minutes(feedrate_time_check):
                time_checker2.reset()
                response_voltage = control.SetPump(current_now, latest_gradient)


            

                reciruclation_voltage = 0.2
                ser.write(str(response_voltage).encode())
                ser.write((':::').encode())
                ser.write(str(reciruclation_voltage).encode())
            

                print('feedrate voltage', str(response_voltage))
                data_to_append = pd.DataFrame({'datetime': [pd.to_datetime('now')], 'feedrate voltage': [response_voltage]})
                if not os.path.isfile('feedrate_data.csv') or os.stat('feedrate_data.csv').st_size == 0:
                    print('making new csv for feedrate')
                    data_to_append.to_csv('feedrate_data.csv', mode='w', header=False)
                else:
                    data_to_append.to_csv('feedrate_data.csv', mode='a', header=False)
        




        