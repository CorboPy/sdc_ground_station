# CLIENT THREADS
# 1. Default. User input() OR menu system for messages to server. Starts 2 once message is sent. Time wait before can send next message? Can only send one request at a time
# 2. (loop) Listening for recieved messages and distributing to other threads below. If "TCAM stream" json, is quickly plotted. If "data snapshot" json, send to 3.
# 3. Parse recieved data or snapshot of TCAM to determine evacuation areas. For TCAM snapshot, need to write a .txt with columns "location", "temp", "safe or evacuate?" for all locations

# https://www.youtube.com/watch?v=79dlpK03t30&list=PLGs0VKk2DiYxdMjCJmcP6jt4Yw6OHK85O&index=48

# TO IMPLEMENT:
# GUI - have main thread for sending messages and GUI stuff 

from datetime import datetime
import time
import socket
import json
import threading
import numpy as np
from funcs_TCP import *
import matplotlib.pyplot as plt
import os
import signal
import sys
import subprocess

def get_pi_ip():    # Using mac address
    with open('mac.txt', 'r') as file:      # mac.txt has mac address of the Pi
        mac = file.read()
    cmd = 'arp -a | findstr "%s" ' %  mac
    returned_output = subprocess.check_output((cmd),shell=True,stderr=subprocess.STDOUT)
    print(returned_output)
    parse=str(returned_output).split(' ',1)
    ip=parse[1].split(' ')
    print(ip[1])
    return(ip[1])

def main():

    data_list=["TIME","TCAM","VOLT","TEMP","IPAD","WLAN"] # For additional identifiable data reqs, add them here and then add them to parse_data() in funcs.py!!!!!!
    cmmd_list=["AOCS","CMD2","CMD3"] # For additional identifiable 4-character cmmd's, add them here and then add them to parse_cmd() in funcs.py!!!!!!
    cmmd_params=[3,2,1]     # NUMBER OF PARAMS FOR COMMAND IN cmmd_list (MUST BE IN SAME ORDER!!!)

    try:
        server_ip = get_pi_ip()
        ask_ip=False
    except Exception as err:
        print("Error in getting Pi IP: ",err)
        ask_ip=True

    while ask_ip:
        ip_input = input("\nPlease input the Pi IP manually: ")
        try:
            socket.inet_aton(ip_input)
        except socket.error:
            print("Invalid IP address")
            continue
        # No errors raised. Valid IP
        ask_ip=False
        server_ip = ip_input

    # server_ip = ''
    server_port = 2222 #int(input("Please input the server port: "))
    listeningAddress = (server_ip, server_port)

    # Setting up client socket
    try:
        GROUNDClient = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        print ("Socket successfully created")
    except socket.error as err: 
        print ("Socket creation failed with error %s" %(err))
        sys.exit()
    buffersize = 2048

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    print("Attempting to connect to Pi...\n")
    attempt = 0
    while True:
        attempt +=1
        if attempt > 4:
            print("No connection after 5 attempts: exiting.\n")
            sys.exit()
        try:
            GROUNDClient.connect((server_ip, server_port)) 
            break
        except ConnectionRefusedError as con_err:
            print(con_err)
            print(">> Please check python script is running on the Pi before connecting! <<")
        except Exception as err:
            print(err)
            print("(unexpected error)")          
        print("\nCannot connect, trying again in 5s...\n")
        time.sleep(5)
    print("Connection establised!\n")
    # Setting up t1
    t1 = threading.Thread(target=listen, args=(GROUNDClient,buffersize,listeningAddress,data_list))    # Listening

    while True:
        user_input = input("Please input a command: 'DATA' for data request, 'COMMAND' to send a command, 'STREAM' for TCAM stream, 'SHUTDOWN' to shutdown server (implement full Pi p-off later), 'EXIT' to close client: \n")

        if (user_input.lower() == "command"):   #check command first, want to be quick
            cmmd_req = get_cmmd_req(cmmd_list,cmmd_params)
            if cmmd_req == False:
                print("Returning to menu...")
                continue
            elif isinstance(cmmd_req, dict) == False:  
                print("Error: cmmd_req not a dictionary. Returning to menu...")
                continue
            #else:       Everything is OK
            msg = json.dumps(cmmd_req)
            GROUNDClient.sendall(msg.encode('utf-8'))

            if t1.is_alive():
                continue
            #else:
            t1.start()
            #need to add try excepts to catch errors in the code above ^
        
        elif (user_input.lower() == "data"):
            while True:
                confirm_data = input("Please confirm dataconfig.json is configured correctly: Y / EXIT: ")
                confirm_data = confirm_data.lower()
                if (confirm_data == 'y') or (confirm_data == 'exit'):   # if no, need to check again
                    break
            
            if confirm_data.lower() == "exit":  # exit to menu
                print("Returning to menu...")
                continue
            
            data_req = get_data_req()

            if data_req == None:
                print("Error, resetting...")
                continue
            #else: all is OK
            msg = json.dumps(data_req)
            GROUNDClient.sendall(msg.encode('utf-8'))
            if t1.is_alive():
                continue
            #else:
            t1.start()

            #need to add try excepts to catch errors in the code above ^

        elif (user_input.lower() == "stream"):
            confirm_stream = None
            while (confirm_stream.lower() == 'exit') or (confirm_stream.lower() == 'start') or (confirm_stream.lower() == 'end'):
                confirm_stream = input("STREAM: To start, type 'Start'. To end, type 'End'. Or, to exit this menu, type 'Exit':")
            
            if confirm_stream.lower() == 'exit':
                print("Returning to menu...")
                continue

            elif confirm_stream.lower() == 'start':
                msg = json.dumps({"STREAM":True})
                GROUNDClient.sendall(msg.encode('utf-8'))
            
            elif confirm_stream.lower() == 'end':
                msg = json.dumps({"STREAM":False})
                GROUNDClient.sendall(msg.encode('utf-8'))

            if t1.is_alive():
                continue
            #else:
            t1.start()
            #need to add try excepts to catch errors in the code above ^
        
        elif (user_input.lower() == "shutdown"):
            print("(not yet implimented) shutting down server....")
            msg = json.dumps({"SHUTDOWN":True})
            GROUNDClient.sendall(msg.encode('utf-8'))
            if not t1.is_alive():
                t1.start()
            time.sleep(3)
            t1.join()
            print("Ending client.")
            break
  
        elif (user_input.lower() == "exit"):
            print("Ending TCP connection.")
            #need to check/shutdown other threads, and then join them up here before breaking https://stackoverflow.com/questions/18018033/how-to-stop-a-looping-thread-in-python
            #look at the stack overflow link? (top answer)
            # if t1.is_alive():
            #     print("Attempting to shutdown listening thread.")
            #     GROUNDClient.shutdown(socket.SHUT_RDWR)
            #     print("Waiting for thread to finish...")
            #     t1.join()
            #     print("Listening thread successfully terminated.")
            print("\nClosing socket.")
            GROUNDClient.shutdown(socket.SHUT_RDWR)
            if t1.is_alive():
                t1.join()
            GROUNDClient.close()

            break
        else:
            print("Unidentified input, please try again.")

    print("Escaped successfully. Goodbye.")

if __name__ == "__main__":
    main()