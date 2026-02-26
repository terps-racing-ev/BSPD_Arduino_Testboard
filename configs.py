# Here Configs For Startup Voltages along with Test Case Voltages are Stored #

brakeInitVoltage = 0.5
throttleInitVoltage = 0.5

brakeFaultVoltage = 2
throttleFaultVoltage = 2

voltageChangePropagationDelay = 23 # ms
timeMultiplierForTimedTest = 0.948 # Unfortunately Based on CPU and Memory Speeds of Host Device :(







if __name__ == "__main__":
    print("INFO: configs not meant to be run, executing main instead.")
    exec(open("main.py").read())