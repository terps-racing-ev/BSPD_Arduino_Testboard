import time
import serial
import customtkinter as ctk
from tkinter import NW, DoubleVar, IntVar, StringVar

font = "Century"
smallfontsize = 20
headingfontsize = 27
backgroundcolor = "#000000"
textcolor = "#FFFFFF"
titletextcolor = "#EAB504"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.geometry("1220x800")
root.iconbitmap('assets/icon.ico')
root.title("TREV-4 BSPD Test Board Control")
root.configure(fg_color=backgroundcolor)
root.resizable(False, False)

sliderPercentDisplay = True
arduino = None
runningTest = False

comnumber = IntVar(value=1)
voltage1 = DoubleVar(value=0.5)
voltage2 = DoubleVar(value=0.5)
slider1 = DoubleVar()
slider2 = DoubleVar()
slider3 = DoubleVar()
slider4 = DoubleVar()
percentage1 = DoubleVar()
percentage2 = DoubleVar()
customInput1 = StringVar(value="0")
customInput2 = StringVar(value="0")


def changeCom(update):
    try:
        global arduino
        if arduino is not None:
            arduino.close()
        port = "COM" + str(comnumber.get())
        arduino = serial.Serial(port=port, baudrate=115200, timeout=1)
        connectFeedback.configure(fg_color="green")
        sendVoltages()
        return True
    except serial.serialutil.SerialException:
        if update:
            arduino = None
            print("Invalid COM Number")
            connectFeedback.configure(fg_color="red")
            root.after(100, flashCOMIndicator)
        return False


def scanCom():
    for i in range(1, 8):
        comnumber.set(i)
        if changeCom(False):
            break
    function_list = [R1, R2, R3, R4, R5, R6, R7]
    function_list[i - 1].invoke()
    if i == 7:
        print("Scanning Failed to Find Arduino!")


def flashCOMIndicator():
    current_color = connectFeedback.cget("fg_color")
    if current_color == "red":
        connectFeedback.configure(fg_color="#8B0000")
        root.after(200, flashCOMIndicator)
    else:
        connectFeedback.configure(fg_color="red")


def displayUpdate(case):
    match case:
        case 1:
            percentage1.set(((voltage1.get() - .5) / 4) * 100)
            pot1Voltage.configure(text=f"{voltage1.get():.3f} V")
            pot1Value.configure(text=f"{percentage1.get():.1f} %")
            if percentage1.get() < 0 or percentage1.get() > 100:
                pot1Value.configure(text="N/A")
                if voltage1.get() > 4.5:
                    slider1.set(4.5)
                if voltage1.get() < 0.5:
                    slider1.set(0.5)
            slider1.set(voltage1.get())
            slider3.set(percentage1.get())
        case 2:
            percentage2.set(((voltage2.get() - .5) / 4) * 100)
            pot2Voltage.configure(text=f"{voltage2.get():.3f} V")
            pot2Value.configure(text=f"{percentage2.get():.1f} %")
            if percentage2.get() < 0 or percentage2.get() > 100:
                pot2Value.configure(text="N/A")
                if voltage2.get() > 4.5:
                    slider2.set(4.5)
                if voltage2.get() < 0.5:
                    slider2.set(0.5)
            slider2.set(voltage2.get())
            slider4.set(percentage2.get())
        case 3:
            voltage1.set((percentage1.get()/100)*4 + .5)
            pot1Voltage.configure(text=f"{voltage1.get():.3f} V")
            pot1Value.configure(text=f"{percentage1.get():.1f} %")
            slider1.set(voltage1.get())
            slider3.set(percentage1.get())
        case 4:
            voltage2.set((percentage2.get()/100)*4 + .5)
            pot2Voltage.configure(text=f"{voltage2.get():.3f} V")
            pot2Value.configure(text=f"{percentage2.get():.1f} %")
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
        currentSliderState.configure(text="Current State: Voltage")
        sliderPercentDisplay = False
    else:
        currentSliderState.configure(text="Current State: Percent")
        sliderPercentDisplay = True


def applyCustom(number, voltage):
    if number == 1:
        responseApply1.configure(text="")
        try:
            float(customInput1.get())
        except Exception:
            responseApply1.configure(text="Invalid Input")
            return
        if voltage:
            if validateVoltage(float(customInput1.get())):
                voltage1.set(float(customInput1.get()))
                responseApply1.configure(text="Applied")
                displayUpdate(1)
            else:
                responseApply1.configure(text="Invalid Input")
        else:
            if validatePercentage(float(customInput1.get())):
                percentage1.set(float(customInput1.get()))
                responseApply1.configure(text="Applied")
                displayUpdate(3)
            else:
                responseApply1.configure(text="Invalid Input")
    else:
        responseApply2.configure(text="")
        try:
            float(customInput2.get())
        except Exception:
            responseApply2.configure(text="Invalid Input")
            return
        if voltage:
            if validateVoltage(float(customInput2.get())):
                voltage2.set(float(customInput2.get()))
                responseApply2.configure(text="Applied")
                displayUpdate(2)
            else:
                responseApply2.configure(text="Invalid Input")
        else:
            if validatePercentage(float(customInput2.get())):
                percentage2.set(float(customInput2.get()))
                responseApply2.configure(text="Applied")
                displayUpdate(4)
            else:
                responseApply2.configure(text="Invalid Input")


def validateVoltage(voltage):
    try:
        return 0 <= voltage <= 5
    except Exception:
        return False


def validatePercentage(percent):
    try:
        return 0 <= percent <= 100
    except Exception:
        return False


def sendVoltages():
    global arduino
    if arduino is not None:
        try:
            voltagea = round(voltage1.get() / 5 * 255) + 1
            voltageb = round(voltage2.get() / 5 * 255) + 1
            sendString = f"[{voltagea},{voltageb}]"
            encodedvoltages = sendString.encode('utf-8')
            arduino.write(encodedvoltages)
            print(f"Sent: {sendString.strip()}")
            root.after(20, sendVoltages)
        except serial.SerialException:
            print("Failure!")
            arduino = None
            connectFeedback.configure(fg_color="red")
    else:
        print("NO Connection To Arduino")

start_time = 0
def waitForFault():  
    global runningTest
    global start_time
    if(not runningTest):
        start_time = time.perf_counter()
        runningTest = True
    if(): #COND FOR NO FAULT
        root.after(1, waitForFault)
    if(): #COND FOR FAULT
        stop_time = time.perf_counter()
        timeElapsed = stop_time - start_time
        timer.configure(text=f"{timeElapsed:.3f}")
        i = 0
        runningTest = False
    
    

# Left: COM controls
comControls = ctk.CTkFrame(root, fg_color=backgroundcolor)

center_frame = ctk.CTkFrame(root, fg_color=backgroundcolor)
brake_frame = ctk.CTkFrame(root, fg_color=backgroundcolor)
throttle_frame = ctk.CTkFrame(root, fg_color=backgroundcolor)
faultTimer_frame = ctk.CTkFrame(root, fg_color=backgroundcolor)
divLine1 = ctk.CTkCanvas(root, bg=backgroundcolor, width=5, height=750, highlightthickness=0)
divLine1.create_line(2,0,2,750,fill="grey",width=2)


comControls.pack(side="left", expand=False, padx=20, pady=5, anchor=NW)
brake_frame.pack(side="left", expand=False, padx=10, pady=5, anchor=NW)
center_frame.pack(side="left", expand=False,padx=10, pady=5, anchor=NW)
throttle_frame.pack(side="left", expand=False, padx=10, pady=5, anchor=NW)
divLine1.pack(side="left", expand=False, padx=10, pady=5, anchor=NW)
faultTimer_frame.pack(side="left", expand=False, padx=10, pady=5, anchor=NW)
center_frame.pack_propagate(False)


comLabel = ctk.CTkLabel(comControls, text="Select COM Port", font=(font, headingfontsize), text_color=titletextcolor)
R_frame = ctk.CTkFrame(comControls, fg_color=backgroundcolor)
R1 = ctk.CTkRadioButton(R_frame, text="COM1", variable=comnumber, value=1, command=lambda: changeCom(True))
R2 = ctk.CTkRadioButton(R_frame, text="COM2", variable=comnumber, value=2, command=lambda: changeCom(True))
R3 = ctk.CTkRadioButton(R_frame, text="COM3", variable=comnumber, value=3, command=lambda: changeCom(True))
R4 = ctk.CTkRadioButton(R_frame, text="COM4", variable=comnumber, value=4, command=lambda: changeCom(True))
R5 = ctk.CTkRadioButton(R_frame, text="COM5", variable=comnumber, value=5, command=lambda: changeCom(True))
R6 = ctk.CTkRadioButton(R_frame, text="COM6", variable=comnumber, value=6, command=lambda: changeCom(True))
R7 = ctk.CTkRadioButton(R_frame, text="COM7", variable=comnumber, value=7, command=lambda: changeCom(True))
scanButton = ctk.CTkButton(comControls, text="Scan COM Ports", font=(font, smallfontsize), command=lambda: scanCom())
connectLabel = ctk.CTkLabel(comControls, text="Connected To Arduino?", font=(font, smallfontsize), text_color=textcolor)
connectFeedback = ctk.CTkFrame(comControls, width=150, height=150, fg_color="red")

comLabel.pack(pady=(0, 20))
R_frame.pack()
for r in [R1, R2, R3, R4, R5, R6, R7]:
    r.pack(anchor="w", pady=2)
scanButton.pack(pady=10)
connectLabel.pack(pady=10)
connectFeedback.pack(pady=10)

pot1Lable = ctk.CTkLabel(brake_frame, text="Brake Sensor", font=(font, headingfontsize), text_color=titletextcolor)
pot1Value = ctk.CTkLabel(brake_frame, text="0.0 %", font=(font, headingfontsize), text_color=titletextcolor)
pot1Voltage = ctk.CTkLabel(brake_frame, text="0.500 V", font=(font, headingfontsize), text_color=titletextcolor)
potSlider1 = ctk.CTkSlider(brake_frame, variable=slider1, from_=0.5, to=4.5, number_of_steps=800, command=lambda case: sliderUpdate(1))
customInputEntry1 = ctk.CTkEntry(brake_frame, textvariable=customInput1, font=(font, smallfontsize), justify="right", width=100)
applyCustomButton1 = ctk.CTkButton(brake_frame, text="Apply", font=(font, smallfontsize), command=lambda: applyCustom(1, currentSliderState.cget("text") == "Current State: Voltage"))
responseApply1 = ctk.CTkLabel(brake_frame, text="", font=(font, headingfontsize), text_color=titletextcolor)

for w in [pot1Lable, pot1Value, pot1Voltage, potSlider1, customInputEntry1, applyCustomButton1, responseApply1]:
    w.pack(pady=5)

pot2Lable = ctk.CTkLabel(throttle_frame, text="Throttle Sensor", font=(font, headingfontsize), text_color=titletextcolor)
pot2Value = ctk.CTkLabel(throttle_frame, text="0.0 %", font=(font, headingfontsize), text_color=titletextcolor)
pot2Voltage = ctk.CTkLabel(throttle_frame, text="0.500 V", font=(font, headingfontsize), text_color=titletextcolor)
potSlider2 = ctk.CTkSlider(throttle_frame, variable=slider2, from_=0.5, to=4.5, number_of_steps=800, command=lambda case: sliderUpdate(2))
customInputEntry2 = ctk.CTkEntry(throttle_frame, textvariable=customInput2, font=(font, smallfontsize), justify="right", width=100)
applyCustomButton2 = ctk.CTkButton(throttle_frame, text="Apply", font=(font, smallfontsize), command=lambda: applyCustom(2, currentSliderState.cget("text") == "Current State: Voltage"))
responseApply2 = ctk.CTkLabel(throttle_frame, text="", font=(font, headingfontsize), text_color=titletextcolor)


for w in [pot2Lable, pot2Value, pot2Voltage, potSlider2, customInputEntry2, applyCustomButton2, responseApply2]:
    w.pack(pady=5)

currentSliderState = ctk.CTkLabel(center_frame, text="Current State: Percent", font=(font, smallfontsize), text_color=textcolor)
toggleSliderButton = ctk.CTkButton(center_frame, text="Toggle Input Type", font=(font, smallfontsize), command=lambda: toggleSliderType())

currentSliderState.pack(pady=10)
toggleSliderButton.pack(pady=10)


spacingFrame250y = ctk.CTkCanvas(center_frame, bg=backgroundcolor, width=1, height=250, highlightthickness=0)
spacingFrame50yb = ctk.CTkCanvas(brake_frame, bg=backgroundcolor, width=1, height=50, highlightthickness=0)
spacingFrame50yt = ctk.CTkCanvas(throttle_frame, bg=backgroundcolor, width=1, height=50, highlightthickness=0)
actualVoltageLable = ctk.CTkLabel(center_frame, text="Actual Voltages", font=(font, headingfontsize), text_color=titletextcolor)
actualValue1 = ctk.CTkLabel(brake_frame, text="0.0 %", font=(font, headingfontsize), text_color=titletextcolor)
actualVoltage1 = ctk.CTkLabel(brake_frame, text="0.500 V", font=(font, headingfontsize), text_color=titletextcolor)
actualValue2 = ctk.CTkLabel(throttle_frame, text="0.0 %", font=(font, headingfontsize), text_color=titletextcolor)
actualVoltage2 = ctk.CTkLabel(throttle_frame, text="0.500 V", font=(font, headingfontsize), text_color=titletextcolor)

for w in [spacingFrame50yb, spacingFrame50yt, spacingFrame250y, actualVoltageLable, actualValue1, actualVoltage1, actualValue2, actualVoltage2]:
    w.pack(pady=5)

timerTitle = ctk.CTkLabel(faultTimer_frame, text="Time Elapsed", font=(font, headingfontsize), text_color=titletextcolor)
timer = ctk.CTkLabel(faultTimer_frame, text="0.000", font=(font, headingfontsize), text_color=textcolor)
testButton = ctk.CTkButton(faultTimer_frame, text="Run Fault Test", font=(font, smallfontsize), command=waitForFault)

for w in [timerTitle, timer, testButton]:
    w.pack(pady=5)

root.mainloop()
