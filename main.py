from machine import Pin, WDT
from DHT22 import DHT22
import time
import sys
import _thread
from _thread import start_new_thread
import utime
import gc
import collections
#import queue

#watchdog1 = WDT(timeout=20000)
gc.enable()
# DHT22 library is available at
# https://github.com/danjperron/PicoDHT22

# init DHT22 on Pin 4. Do not forget to connect 3.3V and GND with a 10k pull-up resistor between 3.3V and data (4).
dht22 = DHT22(Pin(4,Pin.IN,Pin.PULL_UP))
# The LED is the pico built-in.
led = Pin(25, Pin.OUT)
# Relay on 15. For a 5V relay, connect 5V and GND to relay.
relay = Pin(15, Pin.OUT)
# For a "flottör" (float switch), connect it to 16 and 3.3V (NOT 5V!).
flott = Pin(16, Pin.IN,Pin.PULL_DOWN)
led.low()
relay.low()
degree = chr(176)

board = "pico"
# Time to sleep in main loop. DHT22 needs a few seconds between readouts.
sleeptime = 6000
# Temperature threshold: (at what temperature should the dehumidifier turn off due to low temperature?)
TT = 10
# RH threshold: (when should dehumidifier turn ON/OFF?)
RT = 47

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
# llen: How long should the list to calculate a mean be?
llen = 40
countdown = 0
recountdown = 0
cd = 10

foo, bar = dht22.read()
print("Init dht22", foo, bar, "and waiting...")
utime.sleep(6)

while True:
    led.low()
    #LATCH
    T, RH = dht22.read()
    #Prefill all values up to llen
    if len(mT) < llen:
        print("PREFILL", llen, len(mT))
        for i in range(llen):
            mT.append(T)
            mRH.append(RH)
            #print(i, llen)
            #print(mT[i], mRH[i])

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
    #print(str(len(mRH)))
    #print(mT, mRH)
    
    firstRH = (mRH[0] + mRH[1]) /2 #+ mRH[5]) / 3
    lastRH = (mRH[-10] + mRH[-11]) /2 # + mRH[-12]) / 3
    firstT = (mT[0] + mT[1]) /2 # + mT [5]) / 3
    lastT = (mT[-10] + mT[-11]) /2 # + mT[-12]) / 3
    
    RHdiff = round((lastRH - firstRH), 5)
    Tdiff = round((lastT - firstT), 5)
    
    # Future: (40-10 = 30)*2 = 60 iterations from current
    
    futureRH = round((lastRH + (RHdiff * 2)), 3)
    futureT = round((lastT + (Tdiff * 2)), 3)
    #for f in range((llen - 10)):
    #    futureRH += RHdiff
    #    futureT += Tdiff
    futureRHdiff = round((futureRH - mRH[-1]), 3)
    futureTdiff = round((futureT - mT[-1]), 3)
    print("------------------------------------------------------------------------")
    print("RHdiff =", RHdiff, "Tdiff =", Tdiff)
    print("firstRH [0] =", firstRH, ", lastRH [",(llen-10),"] =", lastRH, ", RH [now] =", RH, ", futureRH [",((llen-10)*2),"] =", futureRH)
    print(" firstT [0] =", firstT,  ",  lastT [",(llen-10),"] =",  lastT, ",  T [now] =", T,  ",  futureT [",((llen-10)*2),"] =", futureT)
    #print("Latest reading: RH =", RH, "T =", T)
    print("futureRHdiff =", futureRHdiff, "futureTdiff =", futureTdiff)
    
    #print("Tdiff:", Tdiff, " RHdiff:", RHdiff)
    if RHdiff >= 0.1:
        print("RHdiff:", RHdiff, "RH UP")
        RHup = True
    else:
        print("RHdiff:", RHdiff, "RH DOWN")
        RHup = False
    if Tdiff <= -0.1:
        print("Tdiff:", Tdiff, "T DOWN")
        Tup = False
    else:
        print("Tdiff:", Tdiff, "T UP")
        Tup = True
        
    #print("AVG::: {:3.1f} {:3.1f}".format(sT,sRH))
    #notfull = flott.high() == False
    if flott.value() == True:
        relay.low()
        print("Container full!")
        ran = range(6)
        for r in ran:
            led.high()
            print("{}".format(999999), '\r')
            utime.sleep(1)
            led.low()
            print("{}".format(999999), '\r')
            utime.sleep(1)
        #utime.sleep(2)
    #elif T is None:
    #    print("T=----", degree, "C RH=----}%")
    else:
        if sT >= TT: #and flott.value() != True:
            led.high()
            print("Temp:", sT, "> TT:", TT )
            if LATCH == 1:
                relay.high()
                print("LATCH =", LATCH, "Relay ON")
            elif LATCH > 1:
                print("LATCH =", LATCH)
                if recountdown > 0:
                    relay.low()
                    print("Staying OFF, recountdown =", recountdown)
                    recountdown -= 1
                    
                elif sRH > RT and RHup:
                    relay.high()
                    print("sRH >", RT, "RHup =", RHup, ", Relay ON")
                    countdown = cd
                elif sRH > (RT-4) and RHdiff > 0.4:
                    relay.high()
                    print("RHdiff:", RHdiff, "> 0.4", "Relay ON")
                    countdown = cd
                elif sRH > (RT-2) and RHup and not Tup:
                    relay.high()
                    print("sRH >", (RT-2), "RH up, Temp down, Relay ON")
                    countdown = cd
                elif sRH > (RT+2) and not Tup:
                    relay.high()
                    print("RH >", (RT+2), "Temp DOWN", Tup, "Relay ON")
                    countdown = cd
                elif sRH > (RT+10):
                    relay.high()
                    print("RH >", (RT+10), "Relay ON")
                    countdown = cd
                elif futureRH > RT:
                    relay.high()
                    print("futureRH >", RT, "Relay ON")
                    countdown = cd
                elif (futureT - lastT) < -2:
                    relay.high()
                    print("futureT - lastT < -2, Relay ON")
                    countdown = cd
                else:
                    print("No latch >1 errorlevels true")
                    if countdown <= 0:
                        relay.low()
                        print("Countdown done, Relay OFF")
                        recountdown = cd
                    else:
                        print("Staying ON, countdown =", countdown)
                        countdown -= 1

            elif LATCH == 0:
                print("LATCH =", LATCH)
                relay.low()
            else:
                print("RH:", sRH, "<", RT, ", Relay OFF")
                relay.low()
        else:
            led.low()
            relay.low()
            print(sT,"<",TT, sRH, "Relay OFF")
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
    #watchdog1.feed()
    

