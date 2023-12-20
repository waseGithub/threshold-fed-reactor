#!/bin/bash

# Name of the process to check
PROCESS="log_from_mega.py"
# Command to start the process
COMMAND="python3 /home/wase/threshold-fed-reactor/src/feather_m4/log_from_mega.py"

# Check if the process is running
if pgrep -f $PROCESS > /dev/null
then
    echo "$PROCESS is running."
else
    echo "$PROCESS is not running."
    # Start the process if it's not running
    $COMMAND &
fi
