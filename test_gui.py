import tkinter as tk
import tkinter.font as tkFont
from tkinter import messagebox
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg

class App:
    def __init__(self, root):
        #setting title
        root.title("Prometheus CubeSat")

        #red x protocol
        root.protocol("WM_DELETE_WINDOW", self.on_closing)

        #grid
        root.columnconfigure((0,1),weight=1,uniform='a')
        root.columnconfigure(2,weight=1,uniform='a')
        root.columnconfigure(3,weight=2,uniform='a')
        root.rowconfigure(0,weight=2,uniform='a')
        root.rowconfigure((1,2,3,4,5),weight=1,uniform='a')
        root.rowconfigure(6,weight=10,uniform='a')

        #setting window size
        width=800
        height=600
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        root.geometry(alignstr)
        root.resizable(width=False, height=False)

        GLabel_446=tk.Label(root)
        GLabel_446["bg"] = "#c18282" #C18282 hex colour
        ft = tkFont.Font(family='Times',size=18)
        GLabel_446["font"] = ft
        GLabel_446["fg"] = "#ffffff"
        GLabel_446["justify"] = "center"
        GLabel_446["text"] = "Prometheus CubeSat - BristolSEDS"
        GLabel_446.grid(row=0,sticky='nesw',columnspan=4)

        image1 = Image.open("gui_utility/SDCpatch.png")
        test = ImageTk.PhotoImage(image1)
        label1 = tk.Label(image=test)
        label1.image = test
        # Position image
        label1.place(relx=1, rely=0, anchor='ne')

        DataButton=tk.Button(root,text = 'DATA',bg='#90bef2',font=tkFont.Font(family='Times',size=10),fg='#000000',command=self.GButton_49_command)
        DataButton.grid(row=1,column=0,columnspan=2,sticky='nsew')

        ShutdownButton=tk.Button(root,text = 'SHUTDOWN',bg='#90bef2',font=tkFont.Font(family='Times',size=10),fg='#000000',command=self.GButton_49_command)
        ShutdownButton.grid(row=2,column=0,columnspan=2,sticky='nsew')

        StreamOnButton=tk.Button(root,text = 'STREAM ON',bg='#90bef2',font=tkFont.Font(family='Times',size=10),fg='#000000',command=self.GButton_49_command)
        StreamOnButton.grid(row=3,column=0,sticky='nsew')

        StreamOffButton=tk.Button(root,text = 'STREAM OFF',bg='#90bef2',font=tkFont.Font(family='Times',size=10),fg='#000000',command=self.GButton_49_command)
        StreamOffButton.grid(row=3,column=1,sticky='nsew')

        # TextHealth = tk.Text(root, height = 5, width = 52)
        # TextHealth.grid(row=0,column=3,sticky='nsew')

        self.Refresher()
        root.mainloop()

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit? Client will disconnect from the Pi."):
            root.destroy()

    def Refresher(self):
        # root.after(2000, self.receive_data,*TextHealth)
        # TextHealth.insert(tk.END, Fact)
        return("None")

    def GButton_49_command(self):
        print("command")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
