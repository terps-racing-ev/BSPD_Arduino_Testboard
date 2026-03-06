# Here Configs For Startup Voltages along with Test Case Voltages are Stored #

brakeInitVoltage = 2.5
throttleInitVoltage = 2.5

brakeFaultVoltage = 0
throttleFaultVoltage = 5

voltageChangePropagationDelay = 23 # ms
timeMultiplierForTimedTest = 0.94925 # Unfortunately Based on CPU and Memory Speeds of Host Device :(







if __name__ == "__main__":
    print("INFO: configs not meant to be run, executing main instead.")
    exec(open("main.py").read())