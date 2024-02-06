# Functions / Processes for client 

def listen(UDPClient, buffersize,server_ip,data_list):    # listen for incoming messages
    while True:

        # Recieving a message:
        data,address = UDPClient.resvfrom(buffersize)
        now_rec = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        print("Message recieved from ",address," at ",now_rec," : ",data)

        # Want to make sure recieved message is actually from RPi
        if str(address) == server_ip:   
            # message is from RPi :)

            try:    # try json first as want it to be quickest
                msg = json.loads(data)
            except:
                try:    # try utf-8 next
                    msg = data.decode('utf-8')
                except:
                    # this indent: completely unrecognised
                    print("Data not regosnied by json.loads or utf-8")

                # this indent: msg is utf-8
                print("Message decoded in utf-8: ",msg)

            # this indent: msg is JSON
            # Need to determine if it's from stream or data request
            # Can do so by analysing keys list
            keysList = list(msg.keys())

            if keysList[0] == "STREAM":
                # Stream JSON {"STREAM": [8x8 matrix]}
                # Send to plot function in process 3
                print("Is a STREAM data packet")
            elif len(keysList) == len(data_list):
                # Data JSON {"TCAM":[8x8],"VOLT":5,"TEMP":25}
                # Send to 
                print("Is a DATA packet")



        else:
            print("Error: message not from RPi (server_ip != resvfrom address)")


def get_data_req():
    try:
        with open("dataconfig.json", "r") as jsonfile:
            config_dict = json.load(jsonfile)   # Checking it can be decoded OK before sending to server
    except:     # Error reading file. Might want to specify type of error later
        print("Error: dataconfig.json read unsuccessful")  
        return(None)

    if isinstance(config_dict, dict):       
        print("dataconfig.json read successful.")
        return(config_dict)
    else:
        print("Error: dataconfig.json read unsuccessful.")
        return(None)