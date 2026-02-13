import time
import serial
import customtkinter as ctk
from configs import *
from tkinter import DoubleVar, IntVar, StringVar

font = "Century"
smallfontsize = 20
headingfontsize = 27
backgroundcolor = "#000000"
textcolor = "#FFFFFF"
titletextcolor = "#EAB504"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.geometry("1110x800")
root.iconbitmap('assets/icon.ico')
root.title("TREV-4 BSPD Test Board Control")
root.configure(fg_color=backgroundcolor)
root.resizable(False, False)

sliderPercentDisplay = True
arduino = None
runningTest = False
start_time = 0

comnumber = IntVar(value=1)
voltage1 = DoubleVar(value=brakeInitVoltage)
lastVoltage1 = DoubleVar(value=0)
voltage2 = DoubleVar(value=throttleInitVoltage)
lastVoltage2 = DoubleVar(value=0)
slider1 = DoubleVar()
slider2 = DoubleVar()
slider3 = DoubleVar()
slider4 = DoubleVar()
percentage1 = DoubleVar()
percentage2 = DoubleVar()
customInput1 = StringVar(value="0")
customInput2 = StringVar(value="0")
stringTestDuration = StringVar(value="0")
serialReset = IntVar(value=0)


def changeCom(update):
    try:
        global arduino
        if arduino is not None:
            arduino.close()
        port = "COM" + str(comnumber.get())
        connectFeedback.configure(fg_color="blue")
        arduino = serial.Serial(port=port, baudrate=9600, timeout=1, write_timeout=0)
        connectFeedback.configure(fg_color="green")
        receiveData()
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
    
def sendData():
    global arduino
    try:
        voltagea = round(voltage1.get() / 5 * 255) + 1
        voltageb = round(voltage2.get() / 5 * 255) + 1
        sendString = f"[{voltagea},{voltageb}]"
        encodedvoltages = sendString.encode('ascii')
        print("Sending...")
        arduino.write(encodedvoltages)
        print(f"Sent: {sendString.strip()}")
    except serial.SerialException:
        print("Failure!")
        arduino = None
        connectFeedback.configure(fg_color="red")

def checkSend():
    if voltage1.get() != lastVoltage1.get() or voltage2.get() != lastVoltage2.get():
        lastVoltage1.set(voltage1.get())
        lastVoltage2.set(voltage2.get())
        sendData()
        root.after(10, checkSend)

def receiveData():
    global arduino
    global V1
    global V2
    global AcRef
    global BrRef
    global FAULT
    global AccBrakeDebug
    serialReset.set(serialReset.get() + 1)
    if(serialReset.get() > 200):
        arduino.flush()
        serialReset.set(0)
    if(arduino != None):
        try:
            if(arduino.in_waiting > 0):
                line = arduino.readline()
                line = line.decode('ascii')
                if(line[0] == "["):
                    try:
                        splitVals = line.split(",")
                        Voltage1 = splitVals[0]
                        Voltage1 = Voltage1[1:]
                        V1 = float(Voltage1)
                        Voltage2 = splitVals[1]
                        V2 = float(Voltage2)
                        AcRefTemp = splitVals[2]
                        AcRef = float(AcRefTemp)
                        BrRefTemp = splitVals[3]
                        BrRef = float(BrRefTemp)
                        FAULTTemp = splitVals[4]
                        if(FAULTTemp == "HI"):
                            FAULT = True
                        else:
                            FAULT = False    
                        AccBrakeDebugTemp = splitVals[5]
                        if(AccBrakeDebugTemp == "HI]"):
                            AccBrakeDebug = True
                        else:
                            AccBrakeDebug = False

                        if(serialReset.get() % 25 == 0):
                            actualVoltage1.configure(text = f"{V1:.3f} V")
                            actualVoltage2.configure(text = f"{V2:.3f} V")
                            refVoltageBrake.configure(text = f"{BrRef:.3f} V")
                            refVoltageThrottle.configure(text = f"{AcRef:.3f} V")
                            tempPercent1 = ((V1 - .5) / 4) * 100
                            tempPercent2 = ((V2 - .5) / 4) * 100
                            if(tempPercent1 > 100 or tempPercent1 < 0):
                               actualValue1.configure(text="N/A") 
                            else:
                                actualValue1.configure(text=f"{tempPercent1:.1f} %")
                            if(tempPercent2 > 100 or tempPercent2 < 0):
                                actualValue2.configure(text="N/A")
                            else:
                                actualValue2.configure(text=f"{tempPercent1:.1f} %")
                            
                    except Exception as e:
                        raise(e)
                        
        except Exception as e:
            raise(e)
        root.after(10, receiveData)
        root.after(5, checkSend)

def waitForFault(): 
    global timerVal
    global runningTest
    global start_time
    global AcRef
    global BrRef
    try:
        if(not arduino == None):
            if(not runningTest):
                start_time = time.perf_counter()
                runningTest = True
                timerVal = 0
                voltage1.set(throttleFaultVoltage + 0.1)
                voltage2.set(BrRef + 0.1)
            if(not FAULT):
                root.after(1, waitForFault)
                timerVal += 1
                timer.configure(text=f"{timerVal/1000:.3f}")
            if(FAULT):
                stop_time = time.perf_counter()
                timeElapsed = stop_time - start_time
                timer.configure(text=f"{timeElapsed:.3f}")
                runningTest = False
    except Exception as e:
        print("Test FAILED!")
        raise(e)
    
def timedFaultTest():
    global runningTest
    global start_time
    global timedTestDuration
    if(arduino != None):
        if(not runningTest):
            start_time = time.perf_counter()
            try:
                timedTestDuration = float(stringTestDuration.get())
                runningTest = True
            except Exception:
                print("Invalid Test Duration")
                return
        if(time.perf_counter() - start_time > timedTestDuration):
            runningTest = False
            if(FAULT):
                pass
                #Display Fault
            else:
                pass
                #Display No Fault
        else:
            root.after(1, timedFaultTest)
        
        

top_row_container = ctk.CTkFrame(root, fg_color="transparent")
top_row_container.pack(side="top", fill="both", expand=True)

bottom_row_container = ctk.CTkFrame(root, fg_color="transparent")
bottom_row_container.pack(side="bottom", fill="x", pady=10)

comControls = ctk.CTkFrame(top_row_container, fg_color=backgroundcolor)
brake_frame = ctk.CTkFrame(top_row_container, fg_color=backgroundcolor)
center_frame = ctk.CTkFrame(top_row_container, fg_color=backgroundcolor)
throttle_frame = ctk.CTkFrame(top_row_container, fg_color=backgroundcolor)
faultTimer_frame = ctk.CTkFrame(top_row_container, fg_color=backgroundcolor)

faultStatus_frame = ctk.CTkFrame(bottom_row_container, fg_color=backgroundcolor)


comControls.pack(side="left", expand=False, padx=20, pady=5, anchor="nw")
brake_frame.pack(side="left", expand=False, padx=10, pady=5, anchor="nw")
center_frame.pack(side="left", expand=False,padx=10, pady=5, anchor="nw")
throttle_frame.pack(side="left", expand=False, padx=10, pady=5, anchor="nw")
faultTimer_frame.pack(side="left", expand=False, padx=10, pady=5, anchor="nw")


faultStatus_frame.pack(side="top", expand=False, padx=10, pady=5)


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


spacingFrame50yb = ctk.CTkCanvas(brake_frame, bg=backgroundcolor, width=1, height=50, highlightthickness=0)
spacingFrame50yt = ctk.CTkCanvas(throttle_frame, bg=backgroundcolor, width=1, height=50, highlightthickness=0)
actualBreak = ctk.CTkLabel(brake_frame, text="Actual Brake Voltages:", font=(font, smallfontsize), text_color=titletextcolor)
actualValue1 = ctk.CTkLabel(brake_frame, text="0.0 %", font=(font, headingfontsize), text_color=titletextcolor)
actualVoltage1 = ctk.CTkLabel(brake_frame, text="0.500 V", font=(font, headingfontsize), text_color=titletextcolor)
actualThrottle = ctk.CTkLabel(throttle_frame, text="Actual Throttle Voltages:", font=(font, smallfontsize), text_color=titletextcolor)
actualValue2 = ctk.CTkLabel(throttle_frame, text="0.0 %", font=(font, headingfontsize), text_color=titletextcolor)
actualVoltage2 = ctk.CTkLabel(throttle_frame, text="0.500 V", font=(font, headingfontsize), text_color=titletextcolor)
refVoltageBrakeLable = ctk.CTkLabel(brake_frame, text="Ref Voltage", font=(font, headingfontsize), text_color=titletextcolor)
refVoltageThrottleLabel = ctk.CTkLabel(throttle_frame, text="Ref Voltage", font=(font, headingfontsize), text_color=titletextcolor)
refVoltageBrake = ctk.CTkLabel(brake_frame, text="0.000 V", font=(font, headingfontsize), text_color=titletextcolor)
refVoltageThrottle = ctk.CTkLabel(throttle_frame, text="0.000 V", font=(font, headingfontsize), text_color=titletextcolor)

for w in [spacingFrame50yb, spacingFrame50yt, actualBreak, actualThrottle, actualValue1, actualVoltage1, actualValue2, actualVoltage2, refVoltageBrakeLable, refVoltageThrottleLabel, refVoltageBrake, refVoltageThrottle]:
    w.pack(pady=5)

timerTitle = ctk.CTkLabel(faultTimer_frame, text="Time Elapsed", font=(font, headingfontsize), text_color=titletextcolor)
timer = ctk.CTkLabel(faultTimer_frame, text="0.000", font=(font, headingfontsize), text_color=textcolor)
testButton = ctk.CTkButton(faultTimer_frame, text="Run Fault Test", font=(font, smallfontsize), command=waitForFault)
spacingFrame50y = ctk.CTkFrame(faultTimer_frame, fg_color=backgroundcolor, height= 75, width= 10)
testDurationLabel = ctk.CTkLabel(faultTimer_frame, text="Timed Test", font=(font, headingfontsize), text_color=titletextcolor, justify="right")
testDurationLabel2 = ctk.CTkLabel(faultTimer_frame, text="Test Duration (ms)", font=(font, smallfontsize), justify="right")
testDurationEntry = ctk.CTkEntry(faultTimer_frame, textvariable=stringTestDuration, font=(font, smallfontsize), justify="right", width=75)
timedFaultTestButton = ctk.CTkButton(faultTimer_frame, text="Start Test", font=(font, smallfontsize), command=timedFaultTest, bg_color=backgroundcolor)

for w in [timerTitle, timer, testButton, spacingFrame50y, testDurationLabel, testDurationLabel2, testDurationEntry, timedFaultTestButton]:
    w.pack(pady=5)

faultLabel = ctk.CTkLabel(faultStatus_frame, text="Fault Status",text_color=titletextcolor, font=(font, smallfontsize), justify="right")
faultFrame = ctk.CTkFrame(faultStatus_frame, width=150, height=150, fg_color="green")
faultVoltage = ctk.CTkLabel(faultStatus_frame, text="0.000 V", font=(font, headingfontsize), justify="right")

for w in [faultLabel, faultFrame]:
    w.pack(pady=5)


root.mainloop()