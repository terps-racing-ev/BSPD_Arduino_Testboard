import time
import serial 

from tkinter import Canvas, Label, Radiobutton, Tk, IntVar

font = "Century"
tinyfontsize = 15
smallfontsize = 20
headingfontsize = 27
titlefontsize = 35
backgroundcolor = "#000000"
textcolor = "#FFFFFF"
titletextcolor = "#D4AF37"

root = Tk()
root.geometry("1220x800")
root.title("TREV-4 BSPD Test Board Control")
root.configure(background=backgroundcolor)
root.resizable(False, False)

comnumber = IntVar()
comnumber.set(1)

def changeCom():
    try:
        port = 'COM' + str(comnumber.get())
        print(port)
        arduino = serial.Serial(port=port, baudrate=9600, timeout=1)
        connectFeedback.config(background="green")
    except(serial.serialutil.SerialException):
        print("Invalid COM Number")
        connectFeedback.config(bg="#8B0000")
        flashNumber = 0
        root.after(200, flashCOMIndicator)
        
def flashCOMIndicator():
    if(connectFeedback.cget("bg") == "red"):
        connectFeedback.config(bg="#8B0000")
    else:
        connectFeedback.config(bg="red")
        root.after(200, flashCOMIndicator)
    

    


R1 = Radiobutton(
        root,
        text="COM1",
        variable=comnumber,
        value=1,
        command=changeCom,
        font=("font", smallfontsize),
        background=backgroundcolor,
        fg=textcolor,
        selectcolor=backgroundcolor,
)
R2 = Radiobutton(
    root,
    text="COM2",
    variable=comnumber,
    value=2,
    command=changeCom,
    font=("font", smallfontsize),
    background=backgroundcolor,
    fg=textcolor,
    selectcolor=backgroundcolor,
)
R3 = Radiobutton(
    root,
    text="COM3",
    variable=comnumber,
    value=3,
    command=changeCom,
    font=("font", smallfontsize),
    background=backgroundcolor,
    fg=textcolor,
    selectcolor=backgroundcolor,
)
R4 = Radiobutton(
    root,
    text="COM4",
    variable=comnumber,
    value=4,
    command=changeCom,
    font=("font", smallfontsize),
    background=backgroundcolor,
    fg=textcolor,
    selectcolor=backgroundcolor,
)
R5 = Radiobutton(
    root,
    text="COM5",
    variable=comnumber,
    value=5,
    command=changeCom,
    font=("font", smallfontsize),
    background=backgroundcolor,
    fg=textcolor,
    selectcolor=backgroundcolor,
)
R6 = Radiobutton(
    root,
    text="COM6",
    variable=comnumber,
    value=6,
    command=changeCom,
    font=("font", smallfontsize),
    background=backgroundcolor,
    fg=textcolor,
    selectcolor=backgroundcolor,
)
R7 = Radiobutton(
    root,
    text="COM7",
    variable=comnumber,
    value=7,
    command=changeCom,
    font=("font", smallfontsize),
    background=backgroundcolor,
    fg=textcolor,
    selectcolor=backgroundcolor,
)
comLabel = Label(
        root,
        text="Select COM Port",
        font=("font", headingfontsize),
        background=backgroundcolor,
        fg=titletextcolor,
    )
connectLabel = Label(
        root,
        text="Connected To Arduino?",
        font=("font", smallfontsize),
        background=backgroundcolor,
        fg=textcolor,
    )
connectFeedback = Canvas(root, width=150, height=150, bg="red")


comLabel.grid(column=2, row=1, pady=25, columnspan=10)
connectLabel.grid(column=2, row=3, rowspan=2)
connectFeedback.grid(column=2, row=4, rowspan=10)
R1.grid(column=1, row=2, padx= 0)
R2.grid(column=1, row=3, padx= 10)
R3.grid(column=1, row=4, padx= 10)
R4.grid(column=1, row=5, padx= 10)
R5.grid(column=1, row=6, padx= 10)
R6.grid(column=1, row=7, padx= 10)
R7.grid(column=1, row=8, padx= 10)
R1.invoke()

root.mainloop()