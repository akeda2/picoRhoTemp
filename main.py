from machine import Pin
from DHT22 import DHT22
import time
import sys
import _thread
from _thread import start_new_thread
import utime
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
        print(arawdata)
        rawdata = int(arawdata)
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
            
readserialThread = _thread.start_new_thread(readser, ())

while True:
    led.high()
    LATCH
    T, RH = dht22.read()
    #notfull = flott.high() == False
    if flott.value() == True:
        relay.low()
        print("Container full!")
    elif T is None:
        print("T=----", degree, "C RH=----}%")
    else:
        if T >= TT and flott.value() != True:
            led.high()
            print("Temp:", T, "> TT:", TT )
            if RH >= RT and LATCH >= 1:
                relay.high()
                print("RH:", RH, ">", RT, ", Relay ON")
            elif LATCH == 0:
                print("LATCH OFF")
            else:
                print("RH:", RH, "<", RT)
        else:
            led.low()
            relay.low()
            print(T, RH, "Relay OFF")
        #print(T,RH)
        #print("T={:3.1f}{}C RH={:3.1f}%".format(T,degree,RH))
    time.sleep_ms(int(sleeptime/3))
    print("{:3.1f}".format(T+10000), '\r')
    time.sleep_ms(int(sleeptime/3))
    print("{:3.1f}".format(RH+20000), '\r')
    time.sleep_ms(int(sleeptime/3))
    

