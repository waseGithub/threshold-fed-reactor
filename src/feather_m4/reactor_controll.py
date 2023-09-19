import pandas as pd
import datetime as dt
import numpy as np
import time
import math
import json
import os
from enum import Enum




    

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
        self.current_threshold = 30.00
        self.feedrate = 0 
        self.feedrate_file = 'feedrate.json'
        self.state_file = 'state.json'
        self.feedrate_timer = TimeCheck()
        self.since_feed_timer = TimeCheck()
        self.pump_off_trig = 1 
        self.pump_pulse_time = 1.05 #5ml
        self.feed_time_interval = 180
        self.preset_high_pump_V = 1.6
        #recircluation pump variables
        self.trigger_counter = 0 
        self.recirculation_daily_timer = TimeCheck()
        self.recirculation_pump_timer = TimeCheck()
        self.reciruc_pump_on = False
        self.counter = 0 


        # if os.path.exists(self.feedrate_file):
        #     with open(self.feedrate_file, 'r') as f:
        #         data = json.load(f)
        #         if 'feedrate' in data:
        #             self.feedrate = data['feedrate']
        #     self.startup = False
        
        # if os.path.exists(self.state_file):
        #     print('State file exists')
        #     with open(self.state_file, 'r') as f:
        #         data = json.load(f)
        #         if 'state' in data:
        #             self.state = data['state']
  


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
            elif current_now != 0 :
                print('State Change: STARVED')
                print('Current detected to be below threshold feeding required')
                self.state = State.STARVED
              
        elif self.state == State.FED:
           
            if current_now >= self.current_threshold:
                print('State: FED')
                print('Current detected to be above threshold no feeding required')
                self.state = State.FED

            elif current_now != 0 and self.feedrate_timer.has_passed_minutes(self.feed_time_interval):
                print('State Change: STARVED')
                print('Current detected to be below threshold feeding required')
                self.state = State.STARVED
            else:
                print('State: FED')
                print('The average monitored current showed to dip below 0, however the set feed interval has not been met')
                self.state = State.FED
                
        elif self.state == State.RECOVERY:
            print('State: RECOVERY')
            print('System is being dosed by feeding pump, waiting for current to recover above the set threshold before refeeding')
            if current_now > self.current_threshold:
                self.since_feed_timer.reset()
                self.state = State.FED 
            
        elif self.state == State.STARVED:
            print('State: STARVED')
            print('Current detected to be below threshold dosing reactor with pump. System will now enter recovery')
            self.feedrate = self.preset_high_pump_V
            self.feedrate_timer.reset()
            self.pump_off_trig = 0
            print('State Change: Recovery')
            print('Current detected to be below threshold feeding required')
            self.state = State.RECOVERY    
         
        if self.feedrate_timer.has_passed_minutes(self.pump_pulse_time) and self.pump_off_trig == 0 : 
            print("Stopping pump - elspased pump time", self.pump_pulse_time, "minutes")
            self.feedrate = 0
            self.pump_off_trig = 1
        elif self.pump_off_trig == 0:
            print("pump currently dosing system")

        print('Feedrate is', self.feedrate)
        print('Last state is', str(self.state))

        # with open(self.feedrate_file, 'w') as f:
        #     json.dump({'feedrate': self.feedrate}, f)
        
        # with open(self.state_file, 'w') as f:
        #     json.dump({'state': str(self.state)}, f)

        return self.feedrate
    





    def SetRecirculation(self, pump_feedV: float, recirculation_percentage : float):


        if pump_feedV > 0 and self.trigger_counter == 0:
            self.counter +=1
            self.trigger_counter = 1
        elif pump_feedV == 0 :
            self.trigger_counter = 0 
        

        day_in_mins = 60*24
        recirc_T = self.counter * self.pump_pulse_time * recirculation_percentage
        if self.recirculation_daily_timer.has_passed_minutes(day_in_mins):
            
            print("Recirculation pump active - for", recirc_T, "minutes")
            self.recirculation_daily_timer.reset()
            self.reciruc_pump_on = self.preset_high_pump_V
            self.counter = 0    

        
        if self.recirculation_pump_timer.has_passed_minutes(recirc_T) and self.reciruc_pump_on != 0:
            self.reciruc_pump_on = 0


        print('Recirculation pump status is', self.reciruc_pump_on)
        print('Current feed count is:', self.counter)
        if self.reciruc_pump_on != 0 :
            print('Recirculation pump status pn for', recirc_T)


        return self.reciruc_pump_on
