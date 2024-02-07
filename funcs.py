# Functions / Processes for client 

# Quick plot for stream
def quick_plot(matrix):
    
    plt.imshow(matrix,cmap='hot',interpolation='hermite')
    plt.colorbar()
    plt.show()

# Data analysis
def analysis(msg):
    print(msg)
    #this will be painful

    # Plotting
    matrix = msg["STREAM"]
    plt.imshow(matrix,cmap='hot',interpolation='hermite')
    plt.colorbar()
    plt.show()

    txt_string = "Voltage: %d \nCurrent: %d \nTemp: %d \nAAAAAA: %d" % (volts,curr,temp,AAAAAA)
    # Write txt string to .txt here



# Listening in parallel process/thread
def listen(UDPClient, buffersize,server_ip,data_list):    # listen for incoming messages
    print("t1:Starting listening thread.\n")
    t2 = threading.Thread(target=analysis,args=(packet))    # getting data analysis thread ready
    while True:

        # Recieving a message:
        data,address = UDPClient.resvfrom(buffersize)
        now_rec = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        # Want to make sure recieved message is actually from RPi
        if str(address) == server_ip:   
            # message is from RPi :)

            try:
                data = data.decode("utf-8")
            except:
                print("Error: msg not decodable in UTF-8. Bytes lost.")   # Might want to write to a file or print or something so that message isnt completely lost?
                continue
            print("Message recieved from ",address," at ",now_rec," : ",data)

            if data[0] == "{" and data[-1] == "}":
                
                try:
                    msg = json.loads(data)
                    print("JSON string decoded into python library: ",msg)
                except json.JSONDecodeError as e:
                    print("Error: JSON string not decodable:", e) # Again, as above, might want to write to a file or print the utf-8 or something so that message isnt completely lost?
                    print("Original message: ", data)
                    continue

                # This indent = JSON string successfully decoded into python dicitonary
                # Need to determine if it's from stream or data request
                # Can do so by analysing keys list
                keysList = list(msg.keys())

                if (keysList[0] == "STREAM") and (len(keysList)==1):
                    # Stream JSON {"STREAM": [8x8 matrix]}
                    print("Is a STREAM data packet")
                    quick_plot(msg["STREAM"])
                    # Send to plot function (still part of p1)

                elif len(keysList) == len(data_list):
                    # Data JSON {"TCAM":[8x8],"VOLT":5,"TEMP":25}
                    print("Is a DATA packet")
                    packet = msg
                    t2.start() 
                    ## WILL THIS WORK? DEFINED P2(args) BEFORE MSG WAS ESTABLISHED ##
                else:
                    print("Error: JSON contents not recognised.")
                
            else:
                print("Message not identified as JSON, printing:\n")
                print(data)    


        else:
            print("Error: message not from RPi (server_ip != resvfrom address)")


### Client -> Server ###
# Data JSON
def get_data_req():
    """Checks dataconfig.json is readble and returns config_dict (dict)
    """
    try:
        with open("dataconfig.json", "r") as jsonfile:
            config_dict = json.load(jsonfile)   # Checking it can be decoded OK before sending to server
    except:     # Error reading file. Might want to specify type of error later
        print("Error: dataconfig.json read unsuccessful")  
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
