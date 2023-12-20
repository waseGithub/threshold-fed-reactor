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

def resample_mean(df, time, cols, round_val):
    df = df[cols].dropna()
    df = df[(df.apply(lambda x: pd.to_numeric(x, errors='coerce')) >= 0.0).all(1)]
    df = df.groupby([pd.Grouper(freq=time, level='datetime')]).mean() 
    df = df.round(round_val)
    return df

colnames = ['datetime','Gas 1','Gas 2','Gas 3']
data = pd.read_csv ('/home/wase/threshold-fed-reactor/src/feather_m4/mega_data.csv', names=colnames, skiprows=1)


df_data = pd.DataFrame(data)

df_data['datetime'] = pd.to_datetime(df_data['datetime'], errors='coerce')
df_data.set_index(['datetime'], inplace=True)

df_data.replace({'nan': None}, inplace=True)

df_data = df_data.where(pd.notnull(df_data), None)



for col in ['Gas 1','Gas 2','Gas 3']:
    df_data[col] = df_data[col].astype(str).str.replace(',', '').astype(float)


df_data = resample_mean(df_data, '30T', ['Gas 1','Gas 2','Gas 3'], 3)

df_data.reset_index(inplace=True)
df_data['datetime'] = df_data['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')

df_data.to_csv('test.csv')

print(df_data)

cnx = mysql.connector.connect(user='root', password='wase2022', host='34.89.81.147', database='r2_autonomous_reactor_PHIL')

cursor = cnx.cursor()
cols = "`,`".join([str(i) for i in df_data.columns.tolist()])
# for i,row in df_data.iterrows():
#     sql = "INSERT INTO `mega` (`" +cols + "`) VALUES (" + "%s,"*(len(row)-1) + "%s)"
#     cursor.execute(sql, tuple(row))
#     cnx.commit()

for i,row in df_data.iterrows():
    row = row.where(pd.notnull(row), None)  # Replace 'nan' with None in the row
    sql = "INSERT INTO `mega` (`" +cols + "`) VALUES (" + "%s,"*(len(row)-1) + "%s)"
    cursor.execute(sql, tuple(row))
    cnx.commit()
cnx.close()


os.remove('/home/wase/threshold-fed-reactor/src/feather_m4/mega_data.csv')
