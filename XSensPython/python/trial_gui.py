import tkinter as tk
from threading import Thread
from XSensDOT_connect_trial_modularized import main # your script needs to be properly modularized into callable functions

def start_script():
    thread = Thread(target=main)
    thread.start()

root = tk.Tk()
frame = tk.Frame(root)
frame.pack()

button = tk.Button(frame, 
                   text="QUIT", 
                   fg="red",
                   command=quit)
button.pack(side=tk.LEFT)
start_button = tk.Button(frame,
                   text="Start",
                   command=start_script)
start_button.pack(side=tk.LEFT)

root.mainloop()
