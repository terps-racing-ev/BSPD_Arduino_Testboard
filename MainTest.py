import serial
import customtkinter as ctk
from tkinter import DoubleVar, IntVar

# ------------------- CustomTkinter Configuration -------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

font = "Century"
tinyfontsize = 15
smallfontsize = 20
headingfontsize = 27
titlefontsize = 35
backgroundcolor = "#000000"
textcolor = "#FFFFFF"
titletextcolor = "#EAB504"

# ------------------- Root Window -------------------
root = ctk.CTk()
root.geometry("1220x800")
root.title("TREV-4 BSPD Test Board Control")
root.configure(fg_color=backgroundcolor)
root.resizable(False, False)

# ------------------- Variables -------------------
sliderPercentDisplay = True
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

# ------------------- Functions -------------------
def changeCom(update):
    global arduino
    try:
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
    new_color = "#8B0000" if current_color == "red" else "red"
    connectFeedback.configure(fg_color=new_color)
    root.after(200, flashCOMIndicator)

def displayUpdate(case):
    match case:
        case 1:
            percentage1.set(((voltage1.get() - .5) / 4) * 100)
            pot1Voltage.configure(text=f"{voltage1.get():.3f} V")
            pot1Value.configure(text=f"{percentage1.get():.1f} %")
            if not (0 <= percentage1.get() <= 100):
                pot1Value.configure(text="N/A")
                voltage1.set(max(0.5, min(4.5, voltage1.get())))
            slider1.set(voltage1.get())
            slider3.set(percentage1.get())
        case 2:
            percentage2.set(((voltage2.get() - .5) / 4) * 100)
            pot2Voltage.configure(text=f"{voltage2.get():.3f} V")
            pot2Value.configure(text=f"{percentage2.get():.1f} %")
            if not (0 <= percentage2.get() <= 100):
                pot2Value.configure(text="N/A")
                voltage2.set(max(0.5, min(4.5, voltage2.get())))
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
        case 1: voltage1.set(slider1.get())
        case 2: voltage2.set(slider2.get())
        case 3: percentage1.set(slider3.get())
        case 4: percentage2.set(slider4.get())
    displayUpdate(case)

def toggleSliderType():
    global sliderPercentDisplay
    if sliderPercentDisplay:
        currentSliderState.configure(text="Current State: Voltage")
        potSliderPercent3.grid_forget()
        potSliderPercent4.grid_forget()
        potSlider1.grid(column=6, row=4)
        potSlider2.grid(column=7, row=4)
        sliderPercentDisplay = False
    else:
        currentSliderState.configure(text="Current State: Percentage")
        potSlider1.grid_forget()
        potSlider2.grid_forget()
        potSliderPercent3.grid(column=6, row=4)
        potSliderPercent4.grid(column=7, row=4)
        sliderPercentDisplay = True

def applyCustom(number, voltage):
    if number == 1:
        response = responseApply1
        value = customInput1.get()
        vset, pset = voltage1, percentage1
        caseV, caseP = 1, 3
    else:
        response = responseApply2
        value = customInput2.get()
        vset, pset = voltage2, percentage2
        caseV, caseP = 2, 4

    response.configure(text="")
    try:
        value = float(value)
    except Exception:
        response.configure(text="Invalid Input")
        return

    if voltage and validateVoltage(value):
        vset.set(value)
        response.configure(text="Applied")
        displayUpdate(caseV)
    elif not voltage and validatePercentage(value):
        pset.set(value)
        response.configure(text="Applied")
        displayUpdate(caseP)
    else:
        response.configure(text="Invalid Input")

def validateVoltage(v): return 0 <= v <= 5
def validatePercentage(p): return 0 <= p <= 100

def sendVoltages():
    global arduino
    if arduino:
        try:
            voltagea = round(voltage1.get() / 5 * 255) + 1
            voltageb = round(voltage2.get() / 5 * 255) + 1
            sendString = f"[{voltagea},{voltageb}]"
            arduino.write(sendString.encode('utf-8'))
            print(f"Sent: {sendString}")
            root.after(20, sendVoltages)
        except serial.SerialException:
            print("Failure!")
            arduino = None
            connectFeedback.configure(fg_color="red")
    else:
        print("No Connection to Arduino")

# ------------------- UI -------------------

comLabel = ctk.CTkLabel(root, text="Select COM Port", font=(font, headingfontsize), text_color=titletextcolor)
connectLabel = ctk.CTkLabel(root, text="Connected To Arduino?", font=(font, smallfontsize), text_color=textcolor)
connectFeedback = ctk.CTkFrame(root, width=150, height=150, fg_color="red", corner_radius=10)

scanButton = ctk.CTkButton(root, text="Scan COM Ports", font=(font, smallfontsize), command=scanCom)

R1 = ctk.CTkRadioButton(root, text="COM1", variable=comnumber, value=1, command=lambda: changeCom(True))
R2 = ctk.CTkRadioButton(root, text="COM2", variable=comnumber, value=2, command=lambda: changeCom(True))
R3 = ctk.CTkRadioButton(root, text="COM3", variable=comnumber, value=3, command=lambda: changeCom(True))
R4 = ctk.CTkRadioButton(root, text="COM4", variable=comnumber, value=4, command=lambda: changeCom(True))
R5 = ctk.CTkRadioButton(root, text="COM5", variable=comnumber, value=5, command=lambda: changeCom(True))
R6 = ctk.CTkRadioButton(root, text="COM6", variable=comnumber, value=6, command=lambda: changeCom(True))
R7 = ctk.CTkRadioButton(root, text="COM7", variable=comnumber, value=7, command=lambda: changeCom(True))

# --- Layout for COM Section ---
comLabel.grid(column=1, row=1, pady=25, columnspan=5)
connectLabel.grid(column=2, row=2)
connectFeedback.grid(column=2, row=3, rowspan=10)
R1.grid(column=1, row=2, padx=10)
R2.grid(column=1, row=3, padx=10)
R3.grid(column=1, row=4, padx=10)
R4.grid(column=1, row=5, padx=10)
R5.grid(column=1, row=6, padx=10)
R6.grid(column=1, row=7, padx=10)
R7.grid(column=1, row=8, padx=10)
scanButton.grid(column=1, row=9, pady=20)

# --- Pot Section ---
pot1Lable = ctk.CTkLabel(root, text="Brake Sensor", font=(font, headingfontsize), text_color=titletextcolor)
pot2Lable = ctk.CTkLabel(root, text="Throttle Sensor", font=(font, headingfontsize), text_color=titletextcolor)
pot1Value = ctk.CTkLabel(root, text="0.0 %", font=(font, headingfontsize), text_color=titletextcolor)
pot2Value = ctk.CTkLabel(root, text="0.0 %", font=(font, headingfontsize), text_color=titletextcolor)
pot1Voltage = ctk.CTkLabel(root, text="0.500 V", font=(font, headingfontsize), text_color=titletextcolor)
pot2Voltage = ctk.CTkLabel(root, text="0.500 V", font=(font, headingfontsize), text_color=titletextcolor)

potSlider1 = ctk.CTkSlider(root, from_=0.5, to=4.5, variable=slider1, command=lambda _: sliderUpdate(1))
potSlider2 = ctk.CTkSlider(root, from_=0.5, to=4.5, variable=slider2, command=lambda _: sliderUpdate(2))
potSliderPercent3 = ctk.CTkSlider(root, from_=0, to=100, variable=slider3, command=lambda _: sliderUpdate(3))
potSliderPercent4 = ctk.CTkSlider(root, from_=0, to=100, variable=slider4, command=lambda _: sliderUpdate(4))

toggleSliderButton = ctk.CTkButton(root, text="Toggle Input Type", font=(font, smallfontsize), command=toggleSliderType)
currentSliderState = ctk.CTkLabel(root, text="Current State: Percentage", font=(font, smallfontsize), text_color=textcolor)

pot1Lable.grid(column=6, row=1)
pot2Lable.grid(column=7, row=1)
pot1Value.grid(column=6, row=2)
pot2Value.grid(column=7, row=2)
pot1Voltage.grid(column=6, row=3)
pot2Voltage.grid(column=7, row=3)
potSliderPercent3.grid(column=6, row=4)
potSliderPercent4.grid(column=7, row=4)
currentSliderState.grid(column=6, columnspan=3, row=10)
toggleSliderButton.grid(column=6, columnspan=3, row=11, pady=10)

# --- Custom Input ---
customInputEntry1 = ctk.CTkEntry(root, textvariable=customInput1, font=(font, smallfontsize), width=100)
customInputEntry2 = ctk.CTkEntry(root, textvariable=customInput2, font=(font, smallfontsize), width=100)
applyCustomButton1 = ctk.CTkButton(root, text="Apply", command=lambda: applyCustom(1, currentSliderState.cget("text") == "Current State: Voltage"))
applyCustomButton2 = ctk.CTkButton(root, text="Apply", command=lambda: applyCustom(2, currentSliderState.cget("text") == "Current State: Voltage"))
responseApply1 = ctk.CTkLabel(root, text="", font=(font, headingfontsize), text_color=titletextcolor)
responseApply2 = ctk.CTkLabel(root, text="", font=(font, headingfontsize), text_color=titletextcolor)

customInputEntry1.grid(column=6, row=5, pady=10)
applyCustomButton1.grid(column=6, row=6)
responseApply1.grid(column=6, row=7)
customInputEntry2.grid(column=7, row=5, pady=10)
applyCustomButton2.grid(column=7, row=6)
responseApply2.grid(column=7, row=7)

# --- Actual Voltage Display ---
actualVoltageLable = ctk.CTkLabel(root, text="Actual Voltages", font=(font, headingfontsize), text_color=titletextcolor)
actualValue1 = ctk.CTkLabel(root, text="0.0 %", font=(font, headingfontsize), text_color=titletextcolor)
actualValue2 = ctk.CTkLabel(root, text="0.0 %", font=(font, headingfontsize), text_color=titletextcolor)
actualVoltage1 = ctk.CTkLabel(root, text="0.500 V", font=(font, headingfontsize), text_color=titletextcolor)
actualVoltage2 = ctk.CTkLabel(root, text="0.500 V", font=(font, headingfontsize), text_color=titletextcolor)

actualVoltageLable.grid(column=6, columnspan=2, row=14)
actualValue1.grid(column=6, row=15)
actualValue2.grid(column=7, row=15)
actualVoltage1.grid(column=6, row=16)
actualVoltage2.grid(column=7, row=16)

# ------------------- Run -------------------
root.mainloop()
