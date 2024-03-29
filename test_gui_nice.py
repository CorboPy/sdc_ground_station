import customtkinter as tk
tk.set_appearance_mode("Light")
from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.axes_grid1 import make_axes_locatable
from datetime import datetime
import time
import socket
import json
import threading
import numpy as np
from matplotlib import cm,ticker
import matplotlib
matplotlib.use('TkAgg')
import os
import signal
import sys
import subprocess
import queue
from funcs_TCP import *

# Stream needs to be added server side

# AOCS to be added:
# zero point text box input (default = 0) -> gets read when calculating angle
# manual left/right controls 
# "hold this attitude" ON/OFF control (IF ON -> cannot use manual controls? ^)
# Reorientation: text box input of desired angle, button then reads it and sends it to Pi

# AOCS calibration:
# Orientate correctly without stabilisation enabled
# Get DATA
# Manually type out IMU angle into zero point text box and hit OK (this command will overwrite the self.zero_point variable) (+ maybe it could also update the IMU angle text label for real time update, so the user can see their calibration taking effect)
# IMU is now calibrated

class LabeledEntry(tk.CTkEntry):
    def __init__(self, master=None, label="Search", **kwargs):
        tk.CTkEntry.__init__(self, master, **kwargs)
        self.label = label
        self.on_exit()
        self.bind('<FocusIn>', self.on_entry)
        self.bind('<FocusOut>', self.on_exit)

    def on_entry(self, event=None):
        if self.get() == self.label:
            self.delete(0, tk.END)

    def on_exit(self, event=None):
        if not self.get():
            self.insert(0, self.label)

class App:
    def __init__(self, root):

        # Backend stuff
        #self.TCPsocket,self.address,self.t1,self.data_list,self.q = network_setup()

        #setting title
        root.title("Prometheus CubeSat")

        #red x protocol
        root.protocol("WM_DELETE_WINDOW", self.on_closing)

        #grid
        root.columnconfigure((0,1),weight=1,uniform='a')
        root.columnconfigure(2,weight=5,uniform='a')
        root.rowconfigure((0,1,2,3,4),weight=1,uniform='a')
        root.rowconfigure(5,weight=4,uniform='a')
        root.rowconfigure(6,weight=1,uniform='a')
        root.rowconfigure(7,weight=4,uniform='a')

        #setting window size
        width=1280
        height=720
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        root.geometry(alignstr)
        root.resizable(width=True, height=True)

        # Title banner
        GLabel_446=tk.CTkLabel(root,text="Prometheus CubeSat",font=tk.CTkFont(family="Helvetica",size=25,weight='bold'),text_color='#942911',bg_color='#1A1A1A')
        # #GLabel_446["bg"] = "#942911" #C18282 hex colour
        # #GLabel_446["font"] = 
        # #GLabel_446["fg"] = "#ffffff"
        # #GLabel_446["justify"] = "center"
        GLabel_446.grid(row=0,sticky='nesw',columnspan=2)

        # Logo image
        # image = Image.open('gui_utility/SDCpatch_fullsize.png')
        # image = image.resize((100, 100))
        # logo = ImageTk.PhotoImage(image)
        #label1 = tk.CTkLabel(root,image=logo,text='')
        #label1.image = logo
        #label1.place(relx=1, rely=0, anchor='nw')
        #label1.grid(column=0,row=0, sticky='nw')
        root.iconbitmap(r"C:\Users\alexc\Documents\Git\sdc_ground_station\gui_utility\SDCpatch_fullsize.ico")

        # Text box for AOCS zero point
        self.ZeroEntry = LabeledEntry(root,label='Insert IMU Zero Point')
        self.ZeroEntry.grid(row=6,column=0)

        # Buttons
        #buttons_font = tkFont.Font(family="Helvetica",size=10)

        DataButton=tk.CTkButton(root,text = 'DATA',command=self.Data_command,fg_color='grey',hover_color='#942911')
        DataButton.grid(row=1,column=0,padx=10)

        ShutdownButton=tk.CTkButton(root,text = 'SHUTDOWN',command=self.Shutdown_command,fg_color='grey',hover_color='#942911')
        ShutdownButton.grid(row=1,column=1,padx=10)

        StreamOnButton=tk.CTkButton(root,text = 'STREAM ON',command=self.StreamOn_command,fg_color='grey',hover_color='#942911')
        StreamOnButton.grid(row=2,column=0,padx=10)

        StreamOffButton=tk.CTkButton(root,text = 'STREAM OFF',command=self.StreamOff_command,fg_color='grey',hover_color='#942911')
        StreamOffButton.grid(row=2,column=1,padx=10)

        ReadZeroButton=tk.CTkButton(root, text= "Update",command= self.Imu_zero_read,fg_color='grey',hover_color='#942911')
        ReadZeroButton.grid(row=6,column=1,padx=10)

        # Health data text label
        placeholder_text = "\nTime: 0 \nVoltage: 0 \nTemp: 0 degC \nPi Ip: 0 \nWLAN: 0"
        self.TextHealth = tk.CTkLabel(root, height = 5, width = 52,text=placeholder_text,justify='left',anchor='w',font=tk.CTkFont(family="Courier New",size=13,weight='bold'))
        self.TextHealth.grid(row=7,column=0,sticky='nw',padx=25)

        # Matplotlib tk widget
        self.fig, self.ax = plt.subplots(figsize=(4, 5),facecolor ='#D4D4D4')
        #placeholder_image = plt.imread("gui_utility/SDCpatch_fullsize.png")
        #self.ax.imshow(placeholder_image)
        #self.ax.tick_params(colors='white')
        self.ax.imshow(np.zeros((8,8)),cmap='hot')   # Placeholder plot
        self.divider = make_axes_locatable(self.ax)
        self.cax = self.divider.append_axes('right', size='5%', pad=0.05)
        self.cbar = self.fig.colorbar(cm.ScalarMappable(norm=None, cmap='hot'),pad=0.2,cax=self.cax)
        # plt.axis('off')
        self.canvas = FigureCanvasTkAgg(self.fig, master=root) # A tk.DrawingArea
        self.canvas.get_tk_widget().grid(row=0, column=2,rowspan=8,sticky='nsew')

        # when root.mainloop() is run, root.after(x,func) will happen x milliseconds after
        root.after(1,self.Refresher)
        root.mainloop()

    def close(self):
        self.TCPsocket.shutdown(socket.SHUT_RDWR)
        if self.t1.is_alive():
            self.t1.join()
        self.TCPsocket.close()
        root.destroy()
    
    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit? Client will disconnect from the Pi."):
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
            self.close()

    def draw_chart(self,matrix):
        self.ax.clear()
        self.canvas.draw()
        self.fig.suptitle("TCAM Image",y=0.85)
        im = self.ax.imshow(matrix,interpolation='hermite',cmap='hot') 
        self.fig.colorbar(im,pad=0.2,cax=self.cax)
        self.canvas.draw_idle()
        self.fig.canvas.flush_events()

    def Refresher(self):
        if not self.q.empty():
            #print("\nQueue not empty\n")
            data = self.q.get() # Get data from the queue 
            data_keysList = list(data.keys())   # Extract keys

            if data_keysList[0] == "KILL":
                self.close()

            elif data_keysList[0] == "DATA":  # One-off data request
                # get image and health data from queue
                # write code to calculate IMU angle from raw IMU data using self.zero_point (= 0 by default before calibration - will need a calibration button + function to change it)
                matrix = data["DATA"][0]
                self.draw_chart(matrix)
                self.TextHealth.config(text="MOST RECENT DATA PACKET\n" + str(data["DATA"][1]))

            elif data_keysList[0] == "STREAM":
                print("Update plot only")
                # get image data
                # plot it and refresh tkinter GUI
            else:
                print("Error: data from thread queue not identifiable.")
            #txt_string = "Time: null \nVoltage: null \nTemp: null degC \nPi Ip: null \nWLAN: %s" % np.random.randint(100)
        #else:
            #print("Queue empty")
        root.after(1000,self.Refresher)

    def Data_command(self):
        data_req = get_data_req()

        if data_req == None:
            print("Error, resetting...")
            return()
        #else: all is OK
        msg = json.dumps(data_req)
        self.TCPsocket.sendall(msg.encode('utf-8'))
        if self.t1.is_alive():
            return()
        #else:
        self.t1.start()
        return()
      
    def Shutdown_command(self):
        msg = json.dumps({"SHUTDOWN":True})
        self.TCPsocket.sendall(msg.encode('utf-8'))
        if not self.t1.is_alive():
            self.t1.start()
        time.sleep(3)
        self.t1.join()
        print("Ending client.")
        root.destroy()

    def StreamOn_command(self):
        print("command")
    def StreamOff_command(self):
        print("command")

    def Imu_zero_read(self):
        entry = self.ZeroEntry.get()
        print(type(entry),entry)
        if entry=='Insert IMU Zero Point':
            return()
        # msg = json.dumps(entry)
        # self.TCPsocket.sendall(msg.encode('utf-8'))
        # if self.t1.is_alive():
        #     return()
        # #else:
        # self.t1.start()
        # return()

        # send IMU zero point JSON

########################################################################

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

def network_setup():
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

    data_list=["TIME","TCAM","VOLT","TEMP","IPAD","WLAN"] # For additional identifiable data reqs, add them here and then add them to parse_data() in funcs.py!!!!!!
    
    q = queue.Queue()
    t1 = threading.Thread(target=listen, args=(GROUNDClient,buffersize,listeningAddress,q,data_list))    # Listening
    #cmmd_list=["AOCS","CMD2","CMD3"] # For additional identifiable 4-character cmmd's, add them here and then add them to parse_cmd() in funcs.py!!!!!!
    #cmmd_params=[3,2,1]     # NUMBER OF PARAMS FOR COMMAND IN cmmd_list (MUST BE IN SAME ORDER!!!)

    return(GROUNDClient,listeningAddress,t1,data_list,q)

    #############

    # while True:
    #     user_input = input("Please input a command: 'DATA' for data request, 'COMMAND' to send a command, 'STREAM' for TCAM stream, 'SHUTDOWN' to shutdown server (implement full Pi p-off later), 'EXIT' to close client: \n")

    #     if (user_input.lower() == "command"):   #check command first, want to be quick
    #         cmmd_req = get_cmmd_req(cmmd_list,cmmd_params)
    #         if cmmd_req == False:
    #             print("Returning to menu...")
    #             continue
    #         elif isinstance(cmmd_req, dict) == False:  
    #             print("Error: cmmd_req not a dictionary. Returning to menu...")
    #             continue
    #         #else:       Everything is OK
    #         msg = json.dumps(cmmd_req)
    #         GROUNDClient.sendall(msg.encode('utf-8'))

    #         if t1.is_alive():
    #             continue
    #         #else:
    #         t1.start()
    #         #need to add try excepts to catch errors in the code above ^
        
    #     elif (user_input.lower() == "data"):
            
    #         data_req = get_data_req()

    #         if data_req == None:
    #             print("Error, resetting...")
    #             continue
    #         #else: all is OK
    #         msg = json.dumps(data_req)
    #         GROUNDClient.sendall(msg.encode('utf-8'))
    #         if t1.is_alive():
    #             continue
    #         #else:
    #         t1.start()

    #         #need to add try excepts to catch errors in the code above ^

    #     elif (user_input.lower() == "stream"):
    #         confirm_stream = None
    #         while (confirm_stream.lower() == 'exit') or (confirm_stream.lower() == 'start') or (confirm_stream.lower() == 'end'):
    #             confirm_stream = input("STREAM: To start, type 'Start'. To end, type 'End'. Or, to exit this menu, type 'Exit':")
            
    #         if confirm_stream.lower() == 'exit':
    #             print("Returning to menu...")
    #             continue

    #         elif confirm_stream.lower() == 'start':
    #             msg = json.dumps({"STREAM":True})
    #             GROUNDClient.sendall(msg.encode('utf-8'))
            
    #         elif confirm_stream.lower() == 'end':
    #             msg = json.dumps({"STREAM":False})
    #             GROUNDClient.sendall(msg.encode('utf-8'))

    #         if t1.is_alive():
    #             continue
    #         #else:
    #         t1.start()
    #         #need to add try excepts to catch errors in the code above ^
        
    #     elif (user_input.lower() == "shutdown"):
    #         print("(not yet implimented) shutting down server....")
    #         msg = json.dumps({"SHUTDOWN":True})
    #         GROUNDClient.sendall(msg.encode('utf-8'))
    #         if not t1.is_alive():
    #             t1.start()
    #         time.sleep(3)
    #         t1.join()
    #         print("Ending client.")
    #         break
  
    #     elif (user_input.lower() == "exit"):
    #         print("Ending TCP connection.")
    #         #need to check/shutdown other threads, and then join them up here before breaking https://stackoverflow.com/questions/18018033/how-to-stop-a-looping-thread-in-python
    #         #look at the stack overflow link? (top answer)
    #         # if t1.is_alive():
    #         #     print("Attempting to shutdown listening thread.")
    #         #     GROUNDClient.shutdown(socket.SHUT_RDWR)
    #         #     print("Waiting for thread to finish...")
    #         #     t1.join()
    #         #     print("Listening thread successfully terminated.")
    #         print("\nClosing socket.")
    #         GROUNDClient.shutdown(socket.SHUT_RDWR)
    #         if t1.is_alive():
    #             t1.join()
    #         GROUNDClient.close()

    #         break
    #     else:
    #         print("Unidentified input, please try again.")

    # print("Escaped successfully. Goodbye.")

if __name__ == "__main__":
    root = tk.CTk()
    app = App(root)
    root.mainloop()
