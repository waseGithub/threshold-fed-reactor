# import numpy as np 
# import serial.tools.list_ports
# import pandas as pd
# from datetime import datetime
# import os 
# # from reactor_controll import TrendGradientCalculator
# from reactor_controll import time_check
# import numpy as np
# import mysql.connector
# import matplotlib.pyplot as plt

# # cnx = mysql.connector.connect(user='root', password='wase2022', host='34.89.81.147', database='autonomous_reactor')

# # cursor = cnx.cursor()
# # query = "SELECT * FROM adalogger"
# # cursor.execute(query)



# cnx = mysql.connector.connect(user='root', password='wase2022', host='34.89.81.147', database='autonomous_reactor')

# query = "SELECT * FROM  adalogger"


# adalogger_df = pd.read_sql(query, cnx)


# cnx.close()







# adalogger_df['diff_prev'] = adalogger_df['A Current'].diff().abs()
# adalogger_df['diff_next'] = adalogger_df['A Current'].diff(-1).abs()
# adalogger_df['diff_total'] = adalogger_df['diff_prev'] + adalogger_df['diff_next']

# idx = adalogger_df.groupby('datetime')['diff_total'].idxmin()



# idx.dropna(inplace=True)


# adalogger_df = adalogger_df.loc[idx]





# adalogger_df.reset_index(inplace=True)
# adalogger_df = adalogger_df.drop_duplicates(subset='datetime')
# adalogger_df['datetime'] = pd.to_datetime(adalogger_df['datetime'])
# adalogger_df.set_index('datetime', inplace=True)

# # Resample the dataframe to get continuous data for every half hour
# df_resampled =adalogger_df.resample('90min').mean()

# # Reset 'time' column for resampled data
# df_resampled['time'] = (df_resampled.index - df_resampled.index[0]).total_seconds()

# # Calculate the gradient
# df_resampled['gradient'] = np.gradient(df_resampled['A Current'], df_resampled['time'])

# gradient_df = df_resampled['gradient']





# gradient_df.to_csv('gradient_data.csv')


# latest_gradient = gradient_df.iloc[-1]

# # Save the latest gradient value to a JSON file
# gradient_data = {
#     'latest_gradient': latest_gradient
# }

# with open('gradient_data.json', 'w') as file:
#     json.dump(gradient_data, file)




# # Plot the result
# plt.figure(figsize=(10,6))
# plt.plot(df_resampled.index, df_resampled['gradient'])
# plt.xlabel('Date and Time')
# plt.ylabel('Gradient')
# plt.title('Gradient of Model')
# plt.grid(True)
# plt.show()



import numpy as np
import pandas as pd
import mysql.connector
import matplotlib.pyplot as plt
import json
import time

while True:
    cnx = mysql.connector.connect(user='root', password='wase2022', host='34.89.81.147', database='autonomous_reactor')
    query = "SELECT * FROM adalogger"
    adalogger_df = pd.read_sql(query, cnx)
    cnx.close()

    adalogger_df['diff_prev'] = adalogger_df['A Current'].diff().abs()
    adalogger_df['diff_next'] = adalogger_df['A Current'].diff(-1).abs()
    adalogger_df['diff_total'] = adalogger_df['diff_prev'] + adalogger_df['diff_next']

    idx = adalogger_df.groupby('datetime')['diff_total'].idxmin()
    idx.dropna(inplace=True)
    adalogger_df = adalogger_df.loc[idx]

    adalogger_df.reset_index(inplace=True)
    adalogger_df = adalogger_df.drop_duplicates(subset='datetime')
    adalogger_df['datetime'] = pd.to_datetime(adalogger_df['datetime'])
    adalogger_df.set_index('datetime', inplace=True)

    # Resample the dataframe to get continuous data for every half hour
    df_resampled = adalogger_df.resample('60min').mean()

    # Reset 'time' column for resampled data
    df_resampled['time'] = (df_resampled.index - df_resampled.index[0]).total_seconds()/3600

    # Calculate the gradient
    df_resampled['gradient'] = np.gradient(df_resampled['A Current'], df_resampled['time'])
    print(df_resampled)

    gradient_df = df_resampled['gradient']

    # Save the latest gradient value to a JSON file
    latest_gradient = gradient_df.iloc[-1]
    gradient_data = {
        'latest_gradient': latest_gradient
    }
    with open('gradient_data.json', 'w') as file:
        json.dump(gradient_data, file)

    #  # Plot the result
    # plt.figure(figsize=(10, 6))
    # plt.plot(df_resampled.index, df_resampled['gradient'])
    # plt.xlabel('Date and Time')
    # plt.ylabel('Gradient')
    # plt.title('Gradient of Model')
    # plt.grid(True)
    # plt.pause(0.1)  # Pause for a small delay

    

    # Wait for one minute before reloading the data and image
    time.sleep(30)
    # Clear the current plot
    plt.clf()
    # Clear the current plot
    plt.close()

