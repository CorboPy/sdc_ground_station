# Initial commit

# CLIENT PROCESSES
# 1. Default. User input() OR menu system for messages to server. Starts 2 once message is sent. Time wait before can send next message? Can only send one request at a time
# 2. Listening for recieved messages and distributing to other processes below. If "TCAM stream" json, send to 3. If "data snapshot" json, send to 4.
# 3. Plot TCAM data from recieved json string
# 4. Parse recieved data or snapshot of TCAM to determine evacuation areas. For TCAM snapshot, need to write a .txt with columns "location", "temp", "safe or evacuate?" for all locations

# SERVER PROCESSES
# 1. Default. Waits for connection from client. If it's a command, start process 2. If data req, start process 3. If live TCAM stream (TRUE), start process 4. If live TCAM stream (FALSE), safely end process 4. If shutdown, run shutdown function on this process, ensuring other processes are shut down safely.
# 2. Command specific process function
# 3. Data request function
# 4. Live TCAM stream function

# https://www.youtube.com/watch?v=79dlpK03t30&list=PLGs0VKk2DiYxdMjCJmcP6jt4Yw6OHK85O&index=48

# process 1 - sending messages

from datetime import datetime
import time
import socket
import json
from multiprocessing import Process, managers
import numpy as np
from funcs import *

data_list=["TCAM","VOLT","TEMP"] # For additional intentifiable data reqs, add them here and then add them to parse_data() in funcs.py!!!!!!
cmmd_list=["AOCS","CMD2","CMD3"] # For additional intentifiable 4-character cmmd's, add them here and then add them to parse_cmd() in funcs.py!!!!!!

server_hostname = 'TABLET-9A2B0OP7'     # Can get around DHCP by knowing server host name? 
# Finding server IP
try:
    server_ip = str(socket.gethostbyname(server_hostname)) 
except:
    print("Server not found")

# Server IP found
print("Server found at IP ", server_ip)
# Setting up client socket
GROUNDClient = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
buffersize = 1024

while True:
    user_input = input("Please input a command: 'DATA' for data request, 'COMMAND' to send a command, 'STREAM' for TCAM stream, 'SHUTDOWN' to shutdown server (implement full Pi p-off later), 'EXIT' to close client")

    if (user_input.lower() == "command"):   #check command first, want to be quick
        print("command...")
        #need to check/start p2
    
    elif (user_input.lower() == "data"):
        confirm_data = 'n'
        while (confirm_data.lower() != 'y'):
            confirm_data = input("Please confirm dataconfig.json is configured correctly: Y/N")
        data_req = get_data_req()
        if data_req == None:
            print("Error, resetting...")
        else:
            msg = json.dumps(data_req)
            GROUNDClient.sendto(msg,server_ip)
        #need to check/start p2

    elif (user_input.lower() == "stream"):
        confirm_stream = input("STREAM: To start, type 'True'. To end, type 'End'.")
        if confirm_stream.lower() == 'true':
            msg = json.dumps({"STREAM":True})
            GROUNDClient.sendto(msg,server_ip)
        elif confirm_stream.lower() == 'false':
            msg = json.dumps({"STREAM":False})
            GROUNDClient.sendto(msg,server_ip)
        print("stream...")
        #need to check/start/shutdown p2
    
    elif (user_input.lower() == "shutdown"):
        print("shutting down server....")
        #need to check/start p2

    elif (user_input.lower() == "exit"):
        print("Ending client script")
        #need to check/shutdown other processes
        break
    else:
        print("Unidentified input, please try again.")