from machine import Pin
#import DHT22.py
from DHT22 import DHT22
import time

# DHT22 libray is available at
# https://github.com/danjperron/PicoDHT22

# init DHT22 on Pin 15
dht22 = DHT22(Pin(4,Pin.IN,Pin.PULL_UP))
led = Pin(25, Pin.OUT)
relay = Pin(15, Pin.OUT)
led.low()
relay.low()
degree = chr(176)

# Temperature threshold:
TT = 8
# RH threshold:
RT = 40

while True:
    T, H = dht22.read()
    
    if T is None:
        print("T=----", degree, "C H=----}%")
    else:
        if T >= TT:
            led.high()
            print("Temp >", TT )
            if H >= RT:
                relay.high()
                print("RH >", RT, ", Relay ON!")
        else:
            led.low()
            relay.low()
            print("Deactivated...")
        print(T,H)
        print("T={:3.1f}{}C H={:3.1f}%".format(T,degree,H))
    time.sleep_ms(500)

