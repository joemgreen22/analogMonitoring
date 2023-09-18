import psutil
import wmi
import time, signal, serial
from datetime import datetime
import GPUtil


SLEEP_SECONDS = 0.05
ITERATION_TIME = SLEEP_SECONDS + 0.48#sleep plus compile time

# Network usage calc
NET_MBps = 600  # MegaBITS per second, use something like https://speedtest.net to find out
NET_MAX_BPS = NET_MBps * 125000  # bytes per second
g_networkBytes = 0


# catch ctrl-c
def ctrl_c_handler(signal, frame):
    print('Goodbye!')
    UpdateGauges(0, 0, 0, 0)
    exit()

def invalidRange(dialRange):
    if (dialRange < 0) or (dialRange > 100):
        print("Invalid dial range ! [ 0 <= dialRange <= 100 ]!")
        return True
    else:
        return False

# Update all four gauges
def UpdateGauges(dial1, dial2, dial3, dial4, dial5, dial6):
    if invalidRange(dial1):
        return
    elif invalidRange(dial2):
        return
    elif invalidRange(dial3):
        return
    elif invalidRange(dial4):
        return
    elif invalidRange(dial5):
        return
    elif invalidRange(dial6):
        return

    sendString = "s%d:%d:%d:%d:%d:%d:\r" % (dial1, dial2, dial3, dial4, dial5, dial6)
    return sendString
    # ser.write(sendString.encode())
    



def CycleDial(step=1, delay=0.5):
    # Increment
    for i in range(0,101,step):
        UpdateGauges(i, i, i, i)
        time.sleep(delay)

    # Decrement
    for i in range(0,101,step):
        UpdateGauges(100-i, 100-i, 100-i, 100-i)
        time.sleep(delay)

def tmpToPercent(temp): ## temp gauges will run from 40C to 100C
    x = temp -40
    if(x<0):
        x=0
    percent = x/60 *100
    return round(percent, 1)
    


### RAM ###
def usageRAM():
    return psutil.virtual_memory().percent


### CPU ###
# TEMP
def tempCPU():
    w = wmi.WMI(namespace="root\OpenHardwareMonitor")
    temperature_infos = w.Sensor()
    for sensor in temperature_infos:
        if sensor.SensorType==u'Temperature' and sensor.Name == u'CPU Package':
            return tmpToPercent(round(sensor.Value, 1))
    return "CPU Temp not found"


# Utilization
# def oldUsageCPU():
#     w = wmi.WMI(namespace="root\OpenHardwareMonitor")
#     temperature_infos = w.Sensor()
#     for sensor in temperature_infos:
#         if sensor.SensorType==u'Load' and sensor.Name == u'CPU Total':
#             return round(sensor.Value, 1)
#     return "CPU usage not found"
def usageCPU():
    return psutil.cpu_percent()




###  GPU  ###
# TEMP
# def OldTempGPU():
#     w = wmi.WMI(namespace="root\OpenHardwareMonitor")
#     temperature_infos = w.Sensor()
#     for sensor in temperature_infos:
#         if sensor.SensorType==u'Temperature' and sensor.Name == u'GPU Core':
#             return tmpToPercent(round(sensor.Value, 1))
#     return "GPU Temp not found"

def tempGPU():
    GPUs = GPUtil.getGPUs()
    try:
        gpuTemp = int(GPUs[0].temperature)
    except:
        gpuTemp = 0
    return tmpToPercent(gpuTemp)


# Utilization
# def OldUsageGPU():
#     w = wmi.WMI(namespace="root\OpenHardwareMonitor")
#     temperature_infos = w.Sensor()
#     for sensor in temperature_infos:
#         if sensor.SensorType==u'Load' and sensor.Name == u'GPU Core':
#             return round(sensor.Value, 1)
#     return "GPU usage not found"
def usageGPU():
    GPUs = GPUtil.getGPUs()
    try:
        gpuLoad = int(GPUs[0].load*100)
    except:
        gpuLoad = 0
    
    return gpuLoad


###  Network  ###
def network_usage():
    global g_networkBytes
    net_total = (psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv)

    # Edge case, on first start capture net status 
    # so we can use it in the next iteration of the loop
    if g_networkBytes == 0:
        g_networkBytes = net_total
        percent = 0
    else:
        bytesPerSec = (net_total - g_networkBytes) / ITERATION_TIME
        percent = bytesPerSec / NET_MAX_BPS * 100
        if percent > 100:
            percent = 100

    g_networkBytes = net_total
    return round(percent, 1)



def main():
    start = datetime.now()
    print('RAM % Utalization', usageRAM())
    ramTime = datetime.now()
    print("RAMtime: ", ramTime-start)

    print("CPU Temp:", tempCPU())
    cpuTempTime = datetime.now()
    print("cpu temp time ", cpuTempTime-ramTime)

    print("CPU % Utalization:", usageCPU())
    cpuUseTime = datetime.now()
    print("cpuUseTime: ", cpuUseTime-cpuTempTime)

    print("GPU Temp:", tempGPU())
    gpuTempTime = datetime.now()
    print("gpuTempTime ", gpuTempTime-cpuUseTime)

    print("GPU % Utalization:", usageGPU())
    useGPUTime = datetime.now()
    print("useGPUTime ", useGPUTime-gpuTempTime)
    
    print("Network Utilization", network_usage())
    netTime = datetime.now()
    print("netTime ", netTime-useGPUTime)

    print(UpdateGauges(usageRAM(), tempCPU(), usageCPU(), tempGPU(), usageGPU(), network_usage()))
    compileTime = datetime.now()
    print("compileTime ", compileTime-netTime)

    print("total",compileTime-start)


    print("connecting gauges")
    arduionData=serial.Serial('com3', 115200)
    while True:
        cmd = UpdateGauges(usageRAM(), tempCPU(), usageCPU(), tempGPU(), usageGPU(), network_usage())
        arduionData.write(cmd.encode())
        time.sleep(SLEEP_SECONDS)
        print("working...", datetime.now())
    exit()




if __name__ == '__main__':
    signal.signal(signal.SIGINT, ctrl_c_handler)
    main()