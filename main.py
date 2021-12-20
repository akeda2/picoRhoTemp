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

while True:
    T, H = dht22.read()
    now = time.localtime()
    
    if T is None:
        print("T=----\xdfC H=----}%")
    else:
        if T >= 8:
            led.high()
            if H >= 40:
                relay.high()
            print("Temp > 8, relay ON!")
        else:
            led.low()
            relay.low()
            print("Deactivated...")
        print(T,H)
        print("T={:3.1f}{}C H={:3.1f}%".format(T,degree,H))
    time.sleep_ms(500)

