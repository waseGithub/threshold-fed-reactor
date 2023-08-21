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





colnames = ['datetime','A Bus Voltage','A Current', 'Set Voltage','digital intput']
# data = pd.read_csv ('/home/harvey/Documents/PlatformIO/Projects/autonomous reactor feed/data.csv',  names=colnames, skiprows=  1)

data = pd.read_csv('/home/wase/phil_autonomous_reactor-/src/feather_m4/adalogger_data.csv', names=colnames, skiprows=  1)
#data = pd.read_csv (r'/home/farscopestudent/Documents/WASE/wase-cabinet/flowmeter_push.csv')  
df_auto_control = pd.DataFrame(data)








def resample_mean(df, time, cols, round_val):
  df.dropna(inplace=True)
  # df =  df[(df.astype(float) >= 0.0).all(1)]
  df = df.groupby([pd.Grouper(freq=time, level='datetime')])[cols].mean() 
  df = df.round(round_val)
  return df

def resample_sum(df, time, cols, round_val):
  df.dropna(inplace=True)
  df= df[(df.astype(float) >= 0.0).all(1)]
  df = df.groupby([pd.Grouper(freq=time, level='datetime')])[cols].sum()
  df = df.round(round_val)
  return df

def resample_max(df, time, cols, round_val):
  df.dropna(inplace=True)
  print(df)
  df= df[(df.astype(float) >= 0.0).all(1)]
  df = df.groupby([pd.Grouper(freq=time, level='datetime')])[cols].max()
  df = df.round(round_val)
  return df







df_auto_control['A Current'] = df_auto_control['A Current'].str.replace(' mA', '').astype(float)
df_auto_control['datetime'] = pd.to_datetime(df_auto_control['datetime'], errors='coerce')
df_auto_control.set_index('datetime', inplace=True)

df_auto_control['A Bus Voltage'] = df_auto_control['A Bus Voltage'].str.replace(' V', '')
df_auto_control['A Current'] = df_auto_control['A Current'].str.replace(' mA', '')



df_auto_control['A Bus Voltage'] = pd.to_numeric(df_auto_control['A Bus Voltage'], errors='coerce')
df_auto_control['A Current'] = pd.to_numeric(df_auto_control['A Current'], errors='coerce')
df_auto_control = df_auto_control.dropna(subset=['A Bus Voltage', 'A Current'])




print(df_auto_control)
df_auto_control = resample_mean(df_auto_control, '30T', ['A Bus Voltage','A Current', 'Feed voltage in','Recirculation voltage in', 'Feed voltage set'], 3)






df_auto_control.reset_index(inplace=True)
df_auto_control['datetime'] = df_auto_control['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')


df_auto_control.to_csv('test.csv')






cnx = mysql.connector.connect(user='root', password='wase2022', host='34.89.81.147', database='r4_autonomous_reactor_BILL')


 

cursor = cnx.cursor()
cols = "`,`".join([str(i) for i in df_auto_control.columns.tolist()])
for i,row in df_auto_control.iterrows():
    try:
      sql = "INSERT INTO `adalogger` (`" +cols + "`) VALUES (" + "%s,"*(len(row)-1) + "%s)"
      cursor.execute(sql, tuple(row))
      cnx.commit()
    except mysql.connector.errors.ProgrammingError:
      pass


cnx.close()


os.remove('/home/wase/phil_autonomous_reactor-/src/feather_m4/adalogger_data.csv')