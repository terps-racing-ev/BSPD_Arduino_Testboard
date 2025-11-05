# Here Configs For Startup Voltages along with Test Case Voltages are Stored #

brakeInitVoltage = 0.5
throttleInitVoltage = 0.5

brakeFaultVoltage = 2
throttleFaultVoltage = 2









if __name__ == "__main__":
    print("INFO: configs not meant to be run, executing main instead.")
    exec(open("main.py").read())