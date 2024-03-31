# Functions module for client 
# NEEDS NEST CLEANUP in listen()

from datetime import datetime
import time
import socket
import json
import threading
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import queue

# Increment file name if exists already
def uniquify(path):
    filename, extension = os.path.splitext(path)
    counter = 1

    while os.path.exists(path):
        path = filename + " (" + str(counter) + ")" + extension
        counter += 1

    return path

# Quick plot for stream
def quick_plot(matrix):
    
    plt.imshow(matrix,cmap='hot')   #,interpolation='hermite')
    plt.colorbar()
    plt.show()

# Data analysis
def analysis(msg,q):
    # health.txt file (these will just be = None if not requested)
    time = msg["TIME"]
    volts = msg["VOLT"]
    #curr = msg["CURR"]
    temp = msg["TEMP"]
    ipad = msg["IPAD"]
    wlan = msg["WLAN"]
    angz = msg["ANGZ"]
    matrix = msg["TCAM"]

    txt_string = "Time: %s \nVoltage: %s \nTemp: %s degC \nPi Ip: %s \nWLAN: %s \nIMU z-angle: %s" % (time,volts,temp,ipad,wlan,angz)

    # If no time requested in data request, filename will just be health.txt, need uniquify func to increment filename
    if time != None:
        txt_name = uniquify('health/'+time+'.txt')
    else:
        txt_name = uniquify('health/health.txt') 
    
    # Send to main thread
    q.put({'DATA':[matrix,txt_string,angz,txt_name]})
    print("(t1): put something")
    
    with open(txt_name, 'w') as f:
        f.writelines(txt_string)

    if matrix == None:
        print("Data analysis complete")
    else:
        # # Plotting
        # plt.imshow(matrix,cmap='hot',interpolation='hermite')
        # plt.colorbar()
        # if time != None:
        #     figname = uniquify('images/tcam_'+time+'.pdf')
        # else:
        #     figname = uniquify('tcam.pdf') 

        # plt.savefig(figname,dpi=200)
        # plt.close('all')

        print("Data analysis finished")
        


# Listening in parallel process/thread
def listen(TCPClient, buffersize,listeningAddress,q,data_list):    # listen for incoming messages
    print("(t1) Starting listening thread.\n")
    TCPClient.settimeout(600.0)  # Listening thread will close after 10 mins
    while True:
        #print("(t1) In loop")
        # Recieving a message:
        try:
            data = TCPClient.recv(buffersize)
        except Exception as error:
            print("(t1) Listening thread error: ",error)
            break #???
        now_rec = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        try:
            data = data.decode("utf-8")
        except:
            print("(t1) Error: msg not decodable in UTF-8. Bytes lost.")   # Might want to write to a file or print or something so that message isnt completely lost?
            continue
        print("(t1) Message recieved from server at ",now_rec," : ",data,"\n")

        if data=='':
            print("(t1) Lost connection to Pi.")
            break

        try:
            if data[0] == "{" and data[-1] == "}":
                
                try:
                    msg = json.loads(data)
                    print("(t1) JSON string decoded into python dict: ")
                except json.JSONDecodeError as e:
                    print("(t1) Error: JSON string not decodable:", e)
                    print("(t1) Original message: ", data)
                    continue

                # This indent = JSON string successfully decoded into python dicitonary
                # Need to determine if it's from stream or data request
                # Can do so by analysing keys list
                keysList = list(msg.keys())


                #everything below should be a function:

                if (keysList[0] == "STREAM") and (len(keysList)==1):
                    # Stream JSON {"STREAM": [8x8 matrix]}
                    print("(t1) Is a STREAM data packet")
                    q.put(msg)
                    # Send to plot function (still part of p1)

                elif len(keysList) == len(data_list):
                    # Data JSON {"TCAM":[8x8],"VOLT":5,"TEMP":25}
                    print("(t1) Is a DATA packet")
                    analysis(msg,q)
                else:
                    print("(t1) Error: JSON contents not recognised.")
            
            else:
                continue
                #print("(t1) Message not identified as JSON\n")
                #print(data)    
        except Exception as err:
            print("(t1) Error: ",err)
            break
    q.put({"KILL":True})
    print("(t1) Ending listening thread.")
    

### Client -> Server ###
# Data JSON
def get_data_req():
    """Checks dataconfig.json is readble and returns config_dict (dict)
    """
    try:
        with open("dataconfig.json", "r") as jsonfile:
            config_dict = json.load(jsonfile)   # Checking it can be decoded OK before sending to server
    except Exception as error:     # Error reading file. Might want to specify type of error later
        print("Error: dataconfig.json read unsuccessful:",error)  
        return(None)

    if isinstance(config_dict, dict):       
        print("Success: dataconfig.json read successful.")
        return(config_dict)
    else:
        print("Error: dataconfig.json read unsuccessful.")
        return(None)
    
# Command JSON
def get_cmmd_req(cmmd_list,cmmd_params):  # For additional intentifiable commands, add them to cmd_list and then add an extra elif to the parse_cmd() func
    # Form: {"CMMD":[param1,param2,param3]}
    success=False
    while success == False:
        input_cmmd = input("Please refer to commands.txt and enter a command (case sensitive) in the form: CMMD(param1, param2, param3, etc):")

        cmmd = input_cmmd[0:4]  # Extracting CMMD identifier

        if cmmd.lower() == "exit":  # Exit
            print("EXIT selected.")
            success=False
            return(False)

        try:
            params = input_cmmd.split("(")[1].split(")")[0].split(",")  #list of ordered params
            params = [float(i) for i in params]     #converting args to floats
            # MAKE SURE PARAMS IS A LIST NOT NP ARRAY
        except:
            print("Error: cannot parse inputted command. Incorrect 4-char identifier or params not floatable, or not in form (a,b,c).")
            continue

        # Next check command and num of params matches cmmd_list and cmmd_params
        for i in range(len(cmmd_list)):     # For in range of number of commands
            if cmmd == cmmd_list[i]:         # Check CMMD matches a CMMD from the cmmd_list
                if len(params) == cmmd_params[i]:       # Check num of params matches num of params for that command from cmmd_params
                    print("Sucessful command input.")
                    success=True
                    return({cmmd:params})
        
        # If the code gets here then no match found 
        print("Error: CMMD not found and/or params does not match required number. Please try again")
