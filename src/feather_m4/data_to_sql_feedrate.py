#!/usr/bin/env python
# coding: utf-8

import sqlite3
from google.cloud import storage
import pandas as pd 
import numpy as np
from datetime import datetime
import mysql.connector 
import sys 
import os
import pandas as pd





colnames = ['datetime','pump_voltage_V']
# data = pd.read_csv ('/home/harvey/Documents/PlatformIO/Projects/autonomous reactor feed/data.csv',  names=colnames, skiprows=  1)

data = pd.read_csv ('/home/wase/autonomous_reactor/src/feather_m4/feedrate_data.csv', names=colnames, skiprows=  1)
#data = pd.read_csv (r'/home/farscopestudent/Documents/WASE/wase-cabinet/flowmeter_push.csv')  
df = pd.DataFrame(data)








def resample_mean(dfm, time, cols, round_val):
  print(dfm.tail())
  dfm.dropna(inplace=True)
  # df =  df[(df.astype(float) >= 0.0).all(1)]
  dfm = dfm.groupby([pd.Grouper(freq=time, level='datetime')])[cols].mean() 
  dfm = dfm.round(round_val)
  return dfm

def resample_sum(df, time, cols, round_val):
  df.dropna(inplace=True)
  df= df[(df.astype(float) >= 0.0).all(1)]
  df = df.groupby([pd.Grouper(freq=time, level='datetime')])[cols].sum()
  df = df.round(round_val)
  return df

def resample_max(df, time, cols, round_val):
  df.dropna(inplace=True)
  
  df= df[(df.astype(float) >= 0.0).all(1)]
  df = df.groupby([pd.Grouper(freq=time, level='datetime')])[cols].max()
  df = df.round(round_val)
  return df








df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')


# df['A Bus Voltage'] = df['A Bus Voltage'].str.replace(' V', '')
# df['A Current'] = df['A Current'].str.replace(' mA', '')



df['feedrate_ml_D'] = ((df['pump_voltage_V'] * 1.0726) - 0.021)*1440







df.set_index('datetime', inplace=True)
df = resample_mean(df, '2T',['pump_voltage_V', 'feedrate_ml_D'], 3)
df.reset_index(inplace=True)



df['datetime'] = df['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')



# df.to_csv('flowrate_inferred.csv')

cnx = mysql.connector.connect(user='root', password='wase2022', host='34.89.81.147', database='autonomous_reactor')


 

cursor = cnx.cursor()
cols = "`,`".join([str(i) for i in df.columns.tolist()])
for i,row in df.iterrows():
    try:
      sql = "INSERT INTO `feedrate` (`" +cols + "`) VALUES (" + "%s,"*(len(row)-1) + "%s)"
      cursor.execute(sql, tuple(row))
      cnx.commit()
    except mysql.connector.errors.ProgrammingError:
      pass


cnx.close()


os.remove('/home/wase/autonomous_reactor/src/feather_m4/feedrate_data.csv')

