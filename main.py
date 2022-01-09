from machine import Pin
from DHT22 import DHT22
import time
import sys
import _thread
from _thread import start_new_thread
import utime
import gc
import collections
#import queue

gc.enable()
# DHT22 library is available at
# https://github.com/danjperron/PicoDHT22

# init DHT22 on Pin 4
dht22 = DHT22(Pin(4,Pin.IN,Pin.PULL_UP))
led = Pin(25, Pin.OUT)
relay = Pin(15, Pin.OUT)
flott = Pin(16, Pin.IN,Pin.PULL_DOWN)
led.low()
relay.low()
degree = chr(176)

board = "pico"
# Time to sleep in main loop
sleeptime = 6000
# Temperature threshold:
TT = 8
# RH threshold:
RT = 40

LATCH = 2

def readser():
    global LATCH
    while True:
        arawdata = sys.stdin.readline()
        #print(arawdata)
        try:
            rawdata = int(arawdata)
        except:
            pass
        if board == "tiny":
            #blue.duty_u16(0)
            #green.duty_u16(65535)
            print("lkj")
        else:
            led.high()
            #led.duty_u16(65535)
        try:
            if rawdata > 299000:
                print("Latch on auto!")
                LATCH = 2
            elif rawdata > 199000:
                print("Latch on signal!")
                relay.high()
                LATCH = 1
            elif rawdata > 99000:
                print("Latch off signal!")
                LATCH = 0
                relay.low()
        except:
            pass
        gc.collect()
            
readserialThread = _thread.start_new_thread(readser, ())

mT = []
mRH = []
llen = 20
while True:
    led.low()
    #LATCH
    T, RH = dht22.read()
    
    if len(mT) < llen:
        mT.append(T)
    else:
        mT.pop(0)
        mT.append(T)
    if len(mRH) < llen:
        mRH.append(RH)
    else:
        mRH.pop(0)
        mRH.append(RH)
    
    sT = sum(mT)/len(mT)
    sRH = sum(mRH)/len(mRH)
    print(str(len(mRH)))
    print(mT, mRH)
    #print("AVG::: {:3.1f} {:3.1f}".format(sT,sRH))
    
    #notfull = flott.high() == False
    if flott.value() == True:
        relay.low()
        print("Container full!")
        ran = range(6)
        for r in ran:
            print("{}".format(999999), '\r')
            utime.sleep(1)
            print("{}".format(999999), '\r')
            utime.sleep(1)
        #utime.sleep(2)
    elif T is None:
        print("T=----", degree, "C RH=----}%")
    else:
        if sT >= TT and flott.value() != True:
            led.high()
            print("Temp:", sT, "> TT:", TT )
            if sRH >= RT and LATCH >= 1:
                relay.high()
                print("RH:", sRH, ">", RT, ", Relay ON")
            elif LATCH == 0:
                print("LATCH OFF")
            else:
                print("RH:", sRH, "<", RT)
        else:
            led.low()
            relay.low()
            print(sT, sRH, "Relay OFF")
        #print(T,RH)
        #print("T={:3.1f}{}C RH={:3.1f}%".format(T,degree,RH))
    time.sleep_ms(int(sleeptime/3))
    led.high()
    print("{:3.1f}".format(sT+10000), '\r')
    led.low()
    time.sleep_ms(int(sleeptime/3))
    led.high()
    print("{:3.1f}".format(sRH+20000), '\r')
    led.low()
    time.sleep_ms(int(sleeptime/3))
    led.high()
    sT = sRH = T = RH = None
    gc.collect()
    

