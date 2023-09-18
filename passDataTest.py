import serial
arduionData=serial.Serial('com3', 115200)

while True:
    cmd=input('please enter: ')
    cmd = cmd +'\r'
    arduionData.write(cmd.encode())