import serial

from tkinter import HORIZONTAL, Button, Canvas, DoubleVar, Entry, Label, Radiobutton, Scale, Tk, IntVar

font = "Century"
tinyfontsize = 15
smallfontsize = 20
headingfontsize = 27
titlefontsize = 35
backgroundcolor = "#000000"
textcolor = "#FFFFFF"
titletextcolor = "#EAB504"

root = Tk()
root.geometry("1220x800")
root.title("TREV-4 BSPD Test Board Control")
root.configure(background=backgroundcolor)
root.resizable(False, False)

sliderPercentDisplay = True

global arduino
arduino = None
comnumber = IntVar()
voltage1 = DoubleVar()
voltage2 = DoubleVar()
slider1 = DoubleVar()
slider2 = DoubleVar()
slider3 = DoubleVar()
slider4 = DoubleVar()
percentage1 = DoubleVar()
percentage2 = DoubleVar()
customInput1 = DoubleVar()
customInput2 = DoubleVar()
comnumber.set(1)
voltage1.set(0.5)
voltage2.set(0.5)


def changeCom(update):
    try:
        global arduino
        if not arduino == None:
            arduino.close()
        port = "COM" + str(comnumber.get())
        arduino = serial.Serial(port=port, baudrate=115200, timeout=1)
        connectFeedback.config(bg="green")
        sendVoltages()
        return True
    except serial.serialutil.SerialException:
        if update:
            arduino = None
            print("Invalid COM Number")
            connectFeedback.config(bg="red")
            root.after(100, flashCOMIndicator)
        return False


def scanCom():
    for i in range(1, 8):
        comnumber.set(i)
        if (changeCom(False)) == True:
            break
    function_list = [R1, R2, R3, R4, R5, R6, R7]
    function_list[i - 1].invoke()
    if i == 7:
        print("Scaning Failed to Find Arduino!")


def flashCOMIndicator():
    if connectFeedback.cget("bg") == "red":
        connectFeedback.config(bg="#8B0000")
        root.after(200, flashCOMIndicator)
    else:
        connectFeedback.config(bg="red")

def displayUpdate(case):
    match case:
        case 1:
            percentage1.set(((voltage1.get() - .5) / 4) * 100)
            pot1Voltage.config(text=str(format(voltage1.get(), f".{3}f")) + " V")
            pot1Value.config(text=str(format(percentage1.get(), f".{1}f")) + " %")
            if percentage1.get() < 0 or percentage1.get() > 100:
                pot1Value.config(text="N/A")
                if voltage1.get() > 4.5:
                    slider1.set(4.5)
                if voltage1.get() < 0.5:
                    slider1.set(0.5)
        case 2:
            percentage2.set(((voltage2.get() - .5) / 4) * 100)
            pot2Voltage.config(text=str(format(voltage2.get(), f".{3}f")) + " V")
            pot2Value.config(text=str(format(percentage2.get(), f".{1}f")) + " %")
            if percentage2.get() < 0 or percentage2.get() > 100:
                pot2Value.config(text="N/A")
                if voltage2.get() > 4.5:
                    slider2.set(4.5)
                if voltage2.get() < 0.5:
                    slider2.set(0.5)
        case 3:
            voltage1.set((percentage1.get()/100)*4 + .5)
            pot1Voltage.config(text=str(format(voltage1.get(), f".{3}f")) + " V")
            pot1Value.config(text=str(format(percentage1.get(), f".{1}f") + " %"))
            slider1.set(voltage1.get())
            slider3.set(percentage1.get())
        case 4:
            voltage2.set((percentage2.get()/100)*4 + .5)
            pot2Voltage.config(text=str(format(voltage2.get(), f".{3}f")) + " V")
            pot2Value.config(text=str(format(percentage2.get(), f".{1}f") + " %"))
            slider2.set(voltage2.get())
            slider4.set(percentage2.get())


def sliderUpdate(case):
    match case:
        case 1:
            voltage1.set(slider1.get())
        case 2: 
            voltage2.set(slider2.get())
        case 3:
            percentage1.set(slider3.get())
        case 4:
            percentage2.set(slider4.get())
    displayUpdate(case)

def toggleSliderType():
    global sliderPercentDisplay
    if sliderPercentDisplay:
        currentSliderState.config(text="Current State: Voltage")
        potSliderPercent3.grid_forget()
        potSliderPercent4.grid_forget()
        potSlider1.grid(column=6, row=4)
        potSlider2.grid(column=7, row=4)
        sliderPercentDisplay = False
    else:
        currentSliderState.config(text="Current State: Percent")
        potSlider1.grid_forget()
        potSlider2.grid_forget()
        potSliderPercent3.grid(column=6, row=4)
        potSliderPercent4.grid(column=7, row=4)
        sliderPercentDisplay = True

def applyCustom(number, voltage):
    if number == 1:
        responseApply1.config(text="")
        try:
            customInput1.get()
        except Exception:
            responseApply1.config(text="Invalid Input")
            return
        if voltage:
            if validateVoltage(customInput1.get()):
                voltage1.set(customInput1.get())
                responseApply1.config(text="Applied")
                displayUpdate(1)
            else:
                responseApply1.config(text="Invalid Input")
        else:
            if validatePercentage(customInput1.get()):
                percentage1.set(customInput1.get())
                responseApply1.config(text="Applied")
                displayUpdate(3)
            else:
                responseApply1.config(text="Invalid Input")
    else:
        responseApply2.config(text="")
        try:
            customInput2.get()
        except Exception:
            responseApply2.config(text="Invalid Input")
            return
        if voltage:
            if validateVoltage(customInput2.get()):
                voltage2.set(customInput2.get())
                responseApply2.config(text="Applied")
                displayUpdate(2)
            else:
                responseApply2.config(text="Invalid Input")
        else:
            if validatePercentage(customInput2.get()):
                percentage2.set(customInput2.get())
                responseApply2.config(text="Applied")
                displayUpdate(4)
            else:
                responseApply2.config(text="Invalid Input")

def validateVoltage(voltage):
    try:
        return voltage <= 5 and voltage >= 0
    except Exception:
        return False

def validatePercentage(percent):
    try:
        return percent <= 100 and percent >= 0
    except Exception:
        return False
    
def sendVoltages():
    global arduino
    if(arduino != None):
        try:
            voltagea = round(voltage1.get() / 5 * 255) + 1
            voltageb = round(voltage2.get() / 5 * 255) + 1
            sendString = ("[" + str(voltagea) + "," + str(voltageb) + "]")
            encodedvoltages = sendString.encode('utf-8') 
            arduino.write(encodedvoltages)
            print(f"Sent: {sendString.strip()}")
            root.after(20, sendVoltages)
        except serial.SerialException as e:
            print("Failure!")
            arduino = None
            connectFeedback.config(bg="red")

    else:
        print("NO Connection To Arduino")

# def recieveVoltages():
#     global arduino
#     if(arduino != None):
#         print("REading")
#         try:
#             line = arduino.readline()
#             if arduino.in_waiting > 0:
#                 decoded_line = line.decode('utf-8').strip()
#                 print(f"Received: {decoded_line}")
#             root.after(20, recieveVoltages)
#         except serial.SerialException as e:
#             print("Failure!")
#             arduino = None
#             connectFeedback.config(bg="red")

            
            
   
R1 = Radiobutton(
    root,
    text="COM1",
    variable=comnumber,
    value=1,
    command=lambda: changeCom(True),
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
    command=lambda: changeCom(True),
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
    command=lambda: changeCom(True),
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
    command=lambda: changeCom(True),
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
    command=lambda: changeCom(True),
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
    command=lambda: changeCom(True),
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
    command=lambda: changeCom(True),
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
scanButton = Button(
    root,
    text="Scan COM Ports",
    font=("font", smallfontsize),
    background=backgroundcolor,
    fg=textcolor,
    command=scanCom,
)
connectFeedback = Canvas(root, width=150, height=150, bg="red")


comLabel.grid(column=1, row=1, pady=25, columnspan=5)
connectLabel.grid(column=2, row=2, rowspan=2)
connectFeedback.grid(column=2, row=3, rowspan=10)
R1.grid(column=1, row=2, padx=10)
R2.grid(column=1, row=3, padx=10)
R3.grid(column=1, row=4, padx=10)
R4.grid(column=1, row=5, padx=10)
R5.grid(column=1, row=6, padx=10)
R6.grid(column=1, row=7, padx=10)
R7.grid(column=1, row=8, padx=10)
scanButton.grid(column=1, row=9, pady=20, padx=10)

pot1Lable = Label(
    root,
    text="Brake Sensor",
    font=("font", headingfontsize),
    background=backgroundcolor,
    fg=titletextcolor,
)
pot2Lable = Label(
    root,
    text="Throttle Sensor",
    font=("font", headingfontsize),
    background=backgroundcolor,
    fg=titletextcolor,
)
pot1Value = Label(
    root,
    text="0.0 %",
    font=("font", headingfontsize),
    background=backgroundcolor,
    fg=titletextcolor,
)
pot2Value = Label(
    root,
    text="0.0 %",
    font=("font", headingfontsize),
    background=backgroundcolor,
    fg=titletextcolor,
)
pot1Voltage = Label(
    root,
    text="0.500 V",
    font=("font", headingfontsize),
    background=backgroundcolor,
    fg=titletextcolor,
)
pot2Voltage = Label(
    root,
    text="0.500 V",
    font=("font", headingfontsize),
    background=backgroundcolor,
    fg=titletextcolor,
)
potSlider1 = Scale(
    root,
    variable=slider1,
    from_=0.5,
    to=4.5,
    orient=HORIZONTAL,
    length=150,
    resolution=.005,
    command=lambda case: sliderUpdate(1),
    background=backgroundcolor,
    fg=textcolor,
)
potSlider2 = Scale(
    root,
    variable=slider2,
    from_=0.5,
    to=4.5,
    orient=HORIZONTAL,
    length=150,
    resolution=.005,
    command=lambda case:  sliderUpdate(2),
    background=backgroundcolor,
    fg=textcolor,
)
potSliderPercent3 = Scale(
    root,
    variable=slider3,
    from_=0,
    to=100,
    orient=HORIZONTAL,
    length=150,
    resolution=.1,
    command=lambda case: sliderUpdate(3),
    background=backgroundcolor,
    fg=textcolor,
)
potSliderPercent4 = Scale(
    root,
    variable=slider4,
    from_=0,
    to=100,
    orient=HORIZONTAL,
    length=150,
    resolution=.1,
    command=lambda case: sliderUpdate(4),
    background=backgroundcolor,
    fg=textcolor,
)
toggleSliderButton = Button(
    root,
    text="Toggle Input Type",
    font=("font", smallfontsize),
    background=backgroundcolor,
    fg=textcolor,
    command=toggleSliderType,
)
currentSliderState = Label(
    root,
    text="Current State: Percentage",
    font=("font", smallfontsize),
    background=backgroundcolor,
    fg=textcolor,
)
responseApply1 = Label(
    root,
    text="",
    font=("font", headingfontsize),
    background=backgroundcolor,
    fg=titletextcolor,
)
responseApply2 = Label(
    root,
    text="",
    font=("font", headingfontsize),
    background=backgroundcolor,
    fg=titletextcolor,
)

pot1Lable.grid(column=6, row=1, padx=10)
pot1Value.grid(column=6, row=2, padx=10)
pot1Voltage.grid(column=6, row=3, padx=10)
pot2Lable.grid(column=7, row=1, padx=10)
pot2Value.grid(column=7, row=2, padx=10)
pot2Voltage.grid(column=7, row=3, padx=10)
potSliderPercent3.grid(column=6, row=4)
potSliderPercent4.grid(column=7, row=4)
currentSliderState.grid(column=6, columnspan=3, row=10)
toggleSliderButton.grid(column=6, columnspan=3, row=11, rowspan=2, padx=10, pady=10)

customInputEntry1 = Entry(
    root,
    textvariable=customInput1,
    font=("font", smallfontsize),
    background=backgroundcolor,
    insertbackground=textcolor,
    justify="right",
    fg=textcolor,
    borderwidth=0,
    highlightcolor=textcolor,
    highlightthickness=2,
    width=10
)
customInputEntry2 = Entry(
    root,
    textvariable=customInput2,
    font=("font", smallfontsize),
    background=backgroundcolor,
    insertbackground=textcolor,
    justify="right",
    fg=textcolor,
    borderwidth=0,
    highlightcolor=textcolor,
    highlightthickness=2,
    width=10
)
applyCustomButton1 = Button(
    root,
    text="Apply",
    font=("font", smallfontsize),
    background=backgroundcolor,
    fg=textcolor,
    command=lambda:applyCustom(1, currentSliderState.cget("text") == "Current State: Voltage"),
)
applyCustomButton2 = Button(
    root,
    text="Apply",
    font=("font", smallfontsize),
    background=backgroundcolor,
    fg=textcolor,
    command=lambda:applyCustom(2, currentSliderState.cget("text") == "Current State: Voltage"),
)
customInputEntry1.grid(column=6, row=5, pady=10, rowspan=2)
customInputEntry2.grid(column=7, row=5, pady=10, rowspan=2)
responseApply1.grid(column=6, row=7, pady=10, rowspan=2)
responseApply2.grid(column=7, row=7, pady=10, rowspan=2)
applyCustomButton1.grid(column=6, row=6, pady=10, rowspan=2)
applyCustomButton2.grid(column=7, row=6, pady=10, rowspan=2)
comnumber.set(1)
root.mainloop()
