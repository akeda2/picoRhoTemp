from machine import Pin
from DHT22 import DHT22
import time

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

# Time to sleep in main loop
sleeptime = 6000
# Temperature threshold:
TT = 8
# RH threshold:
RT = 40

while True:
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
            if RH >= RT:
                relay.high()
                print("RH:", RH, ">", RT, ", Relay ON")
            else:
                print("RH:", RH, "<", RT, ", Relay OFF")
        else:
            led.low()
            relay.low()
            print(T, RH, "Relay OFF")
        #print(T,RH)
        print("T={:3.1f}{}C RH={:3.1f}%".format(T,degree,RH))
    time.sleep_ms(sleeptime)

