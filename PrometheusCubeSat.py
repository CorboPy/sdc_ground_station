import customtkinter as tk
tk.set_appearance_mode("Light")
from tkinter import *
from tkinter import messagebox
from tkdial import Meter
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
        root.rowconfigure(5,weight=5,uniform='a')
        root.rowconfigure(6,weight=1,uniform='a')
        root.rowconfigure(7,weight=3,uniform='a')

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
        GLabel_446.grid(row=0,sticky='nesw',columnspan=2)

        # App icon
        root.iconbitmap("gui_utility/SDCpatch_fullsize.ico")

        # Text box for AOCS zero point
        self.ZeroEntry = LabeledEntry(root,label='Insert IMU Zero Point')
        self.ZeroEntry.grid(row=6,column=0)
        self.zeropoint = 0

        # Buttons
        #buttons_font = tkFont.Font(family="Helvetica",size=10)

        DataButton=tk.CTkButton(root,text = 'DATA',command=self.Data_command,fg_color='grey',hover_color='#942911')
        DataButton.grid(row=1,column=0,padx=10)

        ShutdownButton=tk.CTkButton(root,text = 'SHUTDOWN PI',command=self.Shutdown_command,fg_color='grey',hover_color='#942911')
        ShutdownButton.grid(row=1,column=1,padx=10)

        StreamOnButton=tk.CTkButton(root,text = 'STREAM ON',command=self.StreamOn_command,fg_color='grey',hover_color='#942911')
        StreamOnButton.grid(row=2,column=0,padx=10)

        StreamOffButton=tk.CTkButton(root,text = 'STREAM OFF',command=self.StreamOff_command,fg_color='grey',hover_color='#942911')
        StreamOffButton.grid(row=2,column=1,padx=10)

        ReadZeroButton=tk.CTkButton(root, text= "Update",command= self.Imu_zero_read,fg_color='grey',hover_color='#942911')
        ReadZeroButton.grid(row=6,column=1,padx=10)

        # AOCS Buttons
        self.jobid = None

        LeftButton = tk.CTkButton(root, text="LEFT",fg_color='#3D5A80',hover_color='#293241',cursor="hand2")
        LeftButton.grid(row=3,column=0,padx=10)
        LeftButton.bind('<ButtonPress-1>', lambda event, direction='LEFT': self.start_motor(direction))
        LeftButton.bind('<ButtonRelease-1>', lambda event: self.stop_motor())

        RightButton = tk.CTkButton(root, text="RIGHT",fg_color='#3D5A80',hover_color='#293241',cursor="hand2")
        RightButton.grid(row=3,column=1,padx=10)
        RightButton.bind('<ButtonPress-1>', lambda event, direction='RIGHT': self.start_motor(direction))
        RightButton.bind('<ButtonRelease-1>', lambda event: self.stop_motor())

        # IMU angle meter dial
        self.AngleDial = Meter(root, fg="#EBEBEB", radius=250, start=-180, end=180,
            major_divisions=30, minor_divisions=15,border_width=0, text_color="black",
            start_angle=270, end_angle=-360, scale_color="black", axis_color="black",
            needle_color="#942911",  scroll_steps=0.2,text_font=tk.CTkFont(family="Helvetica",size=30,weight='bold'))
        self.AngleDial.set(0)
        self.AngleDial.grid(row=5, column=0,columnspan=2, pady=30)

        # Health data text label
        placeholder_text = "\nTime: 0 \nVoltage: 0 \nTemp: 0 degC \nPi Ip: 0 \nWLAN: 0"
        self.TextHealth = tk.CTkLabel(root, height = 5, width = 52,text=placeholder_text,justify='left',anchor='w',font=tk.CTkFont(family="Courier New",size=13,weight='bold'))
        self.TextHealth.grid(row=7,column=0,columnspan=2,sticky='nw',padx=25)

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
        if messagebox.askyesno("Quit", "Do you want to quit? Client will disconnect from the Pi."):
            print("Ending TCP connection.")
            print("\nClosing socket.")
            self.close()

    def draw_chart(self,matrix):
        self.ax.clear()
        self.canvas.draw()
        im = self.ax.imshow(matrix,interpolation='hermite',cmap='hot') 
        self.fig.colorbar(im,pad=0.2,cax=self.cax)
        self.canvas.draw_idle()
        self.fig.canvas.flush_events()

    def append_txt(self,calibrated_angle,dir):
        # append calibrated angle and append zero point?
        with open(dir, "a") as f: 
            f.write(" \nZero Point: %s \nCalibrated Angle: %s" % (str(self.zeropoint),str(calibrated_angle))) 

    def zero_point_recalc(self,angz):
        calibrated_angle = angz - self.zeropoint
        return(calibrated_angle)

    def Refresher(self):    # NEED TO ENSURE ALL POINTS OF FAILURE DONT STOP CALLING REFRESH
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
                self.TextHealth.configure(text=str(data["DATA"][1]))

                try:
                    angz = float(data["DATA"][2])
                except Exception as err:
                    print("Error, unable to update IMU angle: ",err)
                    root.after(1000,self.Refresher)
                    return()
                
                angz_calibrated = self.zero_point_recalc(angz)
                self.append_txt(angz_calibrated,data["DATA"][3])
                self.AngleDial.set(angz_calibrated) # Update dial orientation angle 

            elif data_keysList[0] == "STREAM":
                print("Update plot and IMU angle only")
                # first entry in list value is matrix
                matrix = data["STREAM"][0]
                self.draw_chart(matrix)
                # second entry in list value is IMU angle
                try:
                    angz = float(data["STREAM"][1])
                except Exception as err:
                    print("Error, unable to update IMU angle: ",err)
                    root.after(200,self.Refresher)
                    return()
                angz_calibrated = self.zero_point_recalc(angz)
                self.AngleDial.set(angz_calibrated) # Update dial orientation angle 

            else:
                print("Error: data from thread queue not identifiable.")

        root.after(200,self.Refresher)  # Must be less than the stream frame rate

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
        if messagebox.askyesno("Shutdown Pi", "Are you sure you want to shutdown the Pi? This will also close the client."):
            msg = json.dumps({"SHUTDOWN":True})
            self.TCPsocket.sendall(msg.encode('utf-8'))
            if not self.t1.is_alive():
                self.t1.start()
            time.sleep(3)
            self.t1.join()
            print("Ending client.")
            root.destroy()

    def StreamOn_command(self):
        msg = json.dumps({"STREAM":True})
        self.TCPsocket.sendall(msg.encode('utf-8'))
        if not self.t1.is_alive():
            self.t1.start()
    def StreamOff_command(self):
        msg = json.dumps({"STREAM":False})
        self.TCPsocket.sendall(msg.encode('utf-8'))
        # t1 should already be running

    def Imu_zero_read(self):
        entry = self.ZeroEntry.get()
        print(type(entry),entry)
        if entry=='Insert IMU Zero Point':
            return()
        self.zeropoint = float(entry)
        print("Zero point updated")
        # update zero point label and dial?
        oldangle = self.AngleDial.get()
        self.AngleDial.set(self.zero_point_recalc(float(oldangle)))

    def move(self,direction):
        global jobid
        print("Moving (%s)" % direction)
        jobid = root.after(1000, self.move, direction)

    def start_motor(self,direction):
        print("starting motor...(%s)" % direction)

        # MESSAGE TO PI TO START MOTOR (here or below move()?)
        # Left = counterclockwise
        # Right = clockwise

        self.move(direction)

    def stop_motor(self):
        global jobid
        root.after_cancel(jobid)

        # MESSAGE TO PI TO STOP MOTOR
        
        print("stopping motor...")



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
        ip_input = input("\nPlease input the Pi IP manually, or type 'EXIT' to exit: ")
        if ip_input.lower() == 'exit':
            sys.exit()
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

    data_list=["TIME","TCAM","VOLT","TEMP","IPAD","WLAN","ANGZ"] # For additional identifiable data reqs, add them here and then add them to parse_data() in funcs_TCP.py!!!!!!
    
    q = queue.Queue()
    t1 = threading.Thread(target=listen, args=(GROUNDClient,buffersize,listeningAddress,q,data_list))    # Listening
    #cmmd_list=["AOCS","CMD2","CMD3"] # For additional identifiable 4-character cmmd's, add them here and then add them to parse_cmd() in funcs.py!!!!!!
    #cmmd_params=[3,2,1]     # NUMBER OF PARAMS FOR COMMAND IN cmmd_list (MUST BE IN SAME ORDER!!!)

    return(GROUNDClient,listeningAddress,t1,data_list,q)

    #############

if __name__ == "__main__":
    root = tk.CTk()
    app = App(root)
    root.mainloop()
