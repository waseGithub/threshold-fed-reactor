import pandas as pd
import datetime as dt
import numpy as np
import time
import math
import json
import os
from enum import Enum


# class TrendGradientCalculator:
#     def __init__(self, dataframe):
#         self.dataframe = dataframe
    
#     def calculate_gradient(self):
#         # Convert the 'datetime' column to pandas datetime format
#         self.dataframe['datetime'] = pd.to_datetime(self.dataframe['datetime'])
            
#         # Sort the DataFrame by datetime in ascending order
#         self.dataframe.sort_values('datetime', inplace=True)
            
#         # Set the 'datetime' column as the DataFrame index
#         self.dataframe.set_index('datetime', inplace=True)
            
#         # Filter the DataFrame for the last three minutes of data
#         start_time = self.dataframe.index[-1] - dt.timedelta(minutes=60)
#         last_minute_df = self.dataframe[start_time:]
            
#         # Convert the 'A Current' column to float
#         last_minute_df['A Current'] = last_minute_df['A Current'].str.replace(' mA', '').astype(float)
        
#         # # Calculate the rolling mean with a window size of 10
#         # last_minute_df['A Current'] = last_minute_df['A Current'].rolling(window=20).mean()

#         # Calculate the gradient using NumPy's polyfit function
#         x = (last_minute_df.index - last_minute_df.index[0]).total_seconds()
#         y = last_minute_df['A Current']
#         gradient = np.polyfit(x, y, 1)[0]
            
#         return gradient

    

class TimeCheck:
    """
    A class used to track the time elapsed since a particular event.

    Attributes:
    last_event_time (float): The time of the last event, in seconds since the epoch.

    Methods:
    has_passed_minutes(minutes): Returns True if the specified number of minutes has elapsed since the last event.
    reset(): Resets the last event time to the current time.
    """
    
    def __init__(self):
        """
        Initializes the TimeCheck with the current time as the last event time.
        """
        self.last_event_time = time.time()
        
    def has_passed_minutes(self, minutes: float) -> bool:
        """
        Checks if the specified number of minutes has elapsed since the last event.

        Parameters:
        minutes (float): The number of minutes to check.

        Returns:
        bool: True if the specified number of minutes has elapsed since the last event, False otherwise.
        """
        current_time = time.time()
        elapsed_time = (current_time - self.last_event_time) / 60  # convert to minutes
        return elapsed_time >= minutes

    def reset(self):
        """
        Resets the last event time to the current time.
        """
        self.last_event_time = time.time()






class State(Enum):
    STARTUP = 1
    FED = 2
    STARVED = 3
    RECOVERY = 4

class Control:
    def __init__(self):
        self.state = State.STARTUP
        self.current_threshold = 70.00
        self.feedrate = 0 
        self.feedrate_file = 'feedrate.json'
        self.state_file = 'state.json'
        self.feedrate_timer = TimeCheck()
        self.pump_off_trig = 1 
        self.recovery_time = 3 # changing to allow for feeding amount
        if os.path.exists(self.feedrate_file):
            with open(self.feedrate_file, 'r') as f:
                data = json.load(f)
                if 'feedrate' in data:
                    self.feedrate = data['feedrate']
            self.startup = False
        
        if os.path.exists(self.state_file):
            print('State file exists')
            with open(self.state_file, 'r') as f:
                data = json.load(f)
                if 'state' in data:
                    self.state = data['state']
  


    def SetPump(self, current_now: float, latest_gradient: float) -> float:
        """
        This method calculates and sets the new feedrate based on the current and the latest gradient.
        
        Parameters:
        current_now (float): The current value.
        latest_gradient (float): The latest gradient value.

        Returns:
        float: The updated feedrate.
        """
        print('Av current', current_now)
        if self.state == State.STARTUP:
            print('State: STARTUP')
            print('System in start up phase')
            if current_now >= self.current_threshold:
                print('State Change: FED')
                print('Current detected to be above threshold no feeding required')
                self.state = State.FED
            else :
                print('State Change: STARVED')
                print('Current detected to be below threshold feeding required')
                self.state = State.STARVED
              

        elif self.state == State.FED:
           
            if current_now >= self.current_threshold:
                print('State: FED')
                print('Current detected to be above threshold no feeding required')
                self.state = State.FED
            else:
                print('State Change: STARVED')
                print('Current detected to be below threshold feeding required')
                self.state = State.STARVED
                

        
        elif self.state == State.RECOVERY:
            print('State: RECOVERY')
            print('System is being dosed by feeding pump, waiting for current to recover above the set threshold before refeeding')
            if current_now > self.current_threshold:
                self.state = State.FED 
            
        elif self.state == State.STARVED:
            print('State: STARVED')
            print('Current detected to be below threshold dosing reactor with pump. System will now enter recovery')
            self.feedrate = 0.5
            self.feedrate_timer.reset()
            self.pump_off_trig = 0
            print('State Change: Recovery')
            print('Current detected to be below threshold feeding required')
            self.state = State.RECOVERY
            
            
         
        




    
        if self.feedrate_timer.has_passed_minutes(1) and self.pump_off_trig == 0 : 
            print("Stopping pump - elspased pump time", self.recovery_time, "3 minutes")
            self.feedrate = 0
            self.pump_off_trig = 1
        elif self.pump_off_trig == 0:
            print("pump currently dosing system")



  


        print('Feedrate is', self.feedrate)
        print('Last state is', str(self.state))

        with open(self.feedrate_file, 'w') as f:
            json.dump({'feedrate': self.feedrate}, f)
        
        with open(self.state_file, 'w') as f:
            json.dump({'state': str(self.state)}, f)

        return self.feedrate