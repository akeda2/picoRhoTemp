# Rhotemp for the pico W
from machine import Pin
from DHT22 import DHT22
#import time
import sys
import _thread
from _thread import start_new_thread
import utime
import utime as time
import gc
import collections
import utime
from wsett import wifisettings
from wifiwrap import wifiwrap
import uasyncio as asyncio
import rp2
from styrover import Relay, Onoff

gc.enable()

# DHT22 library is available at
# https://github.com/danjperron/PicoDHT22

# init DHT22 on Pin 4. Do not forget to connect 3.3V and GND with a 10k pull-up resistor between 3.3V and data (4).
dht22 = DHT22(Pin(4,Pin.IN,Pin.PULL_UP))
# The LED is the pico built-in.
#led = Pin(25, Pin.OUT)
led = Pin('LED', Pin.OUT)
# Relay on 15. For a 5V relay, connect 5V and GND to relay.
relay = Pin(15, Pin.OUT)
#relay = Pin(16, Pin.OUT)
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

# From bozon
offtime = 840
#offtime = 5
ontime = 60
#ontime = 5
ON = None
TIMERON = None


# WiFi starts here:
myWifi = wifiwrap()
myWifi.connect_to_network(wifisettings['ssid'], wifisettings['passwd'])

print(myWifi.ifconfig())
print(myWifi.getstatus())
myIP = myWifi.getip()

# Website values starts here:
urls = {
    'relayON': '/relay/on',
    'relayOFF': '/relay/off',
    'relayStatus': '/relay/status',
    'ozonToggle': '/ozon/toggle',
    'timerON': '/ozon/timeron',
    'timerOFF': '/ozon/timeroff',
    'timerToggle': '/ozon/timertoggle',
    'overrideOFF': '/ozon/overrideoff'
    }
html = f"""<!DOCTYPE html>
<html>
    <head> <title>{wifisettings['title']}</title> </head>
    <body>%s
    </body>
</html>
"""
redir = f'''<!DOCTYPE html>
<html>
    <head> <title>{wifisettings['title']}-redirecting</title> </head><meta http-equiv="Refresh" content="2; URL=http://{myIP}/">
    <body><pre>%s\n%s</pre>
    </body>
</html>'''

def memprint():
    print("Mem alloc: ",gc.mem_alloc(),"Mem free: ",gc.mem_free())

def checkwebpage():
    #kaUrl = "http://" + myWifi.getip() + "/"
    kaUrl = "https://" + "www.radioartor.se" + "/internal.html"
    try:
        myData = urequests.get(kaUrl)
        print(myData.text)
        print("OK")
        del myData
        return True
    except:
        #print(f"Could not get webpage {kaUrl}")
        return False

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


# Async webserver starts here:
async def serve_client(reader,writer):
        global ON
        global TIMERON
        global woverride
        global clients
        global LATCH
        print("Client connected")
        print("Clients before:", str(clients))
        request_line = await reader.readline()
        #request_line = b''
        print("Request:", str(request_line))
        if not request_line:
            print("========================================================================================================")
            request_line = b'GET / HTTP/1.1\r\n'
            #request_line = b"\r\n"
        i = 0
        while await reader.readline() != b'\r\n':
        #str(reader.readline()).endswith(b"\r\n"):#
            i += 1
            glenn = await reader.readline()
            #print(str(glenn))
            if glenn == b'\r\n':
                #print("GLENN=", glenn, "BREAKING")
                break
            #print(str(request_line))
            if i > 9:
                #print("---", i, "out of loop")
                break
            else:
                #print("---", i, "in loop")
                pass
            pass
        clientIP = reader.get_extra_info('peername')
        print(clientIP[0])
        await asyncio.sleep(0)
        request = str(request_line)        
        print(request)
        favicon = request.find('/favicon.ico')
        root = request.find('/ ', 6, 9)

#         led_on = request.find('/led/on')
#         led_off = request.find('/led/off')
#         led_toggle = request.find('/led/toggle')
#         
        relayON = request.find(urls['relayON'])
        relayOFF = request.find(urls['relayOFF'])
        relayStatus = request.find(urls['relayStatus'])
#         ozonToggle = request.find(urls['ozonToggle'])
#         timerON = request.find(urls['timerON'])
#         timerOFF = request.find(urls['timerOFF'])
#         timerToggle = request.find(urls['timerToggle'])
        overrideOFF = request.find(urls['overrideOFF'])
        #json = request.find('/json')
        #print('led on = ' + str(led_on))
        #print('led off = ' + str(led_off))
        #print('led toggle = ' + str(led_toggle))
#         print('ozon on = ' + str(ozonON))
#         print('ozon off = ' + str(ozonOFF))
#         print('ozon toggle = ' + str(ozonToggle))
#         print('ozon timer on = ' + str(timerON))
#         print('ozon timer off = ' + str(timerOFF))
#         print('ozon timer off = ' + str(timerToggle))
        print('override off = ' + str(overrideOFF))
        print('Relay status = ' + str(relayStatus))
        print('favicon = ' + str(favicon))
        print('root = ' + str(root))
        #print('rh = ' + str(rh))
        #print('json = ' + str(json))
        
        #Default webpage if just "/"
        myIP = myWifi.getip()
        if relay.value() == 1:
            isiton = "ON"
        else:
            isiton = "OFF"
        if TIMERON:
            isTimerOn = "Timer ON"
        else:
            isTimerOn = "Timer OFF"
        if woverride == True:
            isOverride = "Override ON"
        else:
            isOverride = "Override OFF"
        
        stateis = f"""<h1>Relay {isiton}</h1><br>
        <h2>{isTimerOn}</h2><br>
        <h3>{isOverride}</h3><br>
        <a href='http://{myIP}{urls['relayON']}'>Relay ON</a><br>
        <a href='http://{myIP}{urls['relayOFF']}'>Relay OFF</a><br>
        <a href='http://{myIP}{urls['relayStatus']}'>Relay status</a><br>
        <a href='http://{myIP}{urls['overrideOFF']}'>Relay auto</a><br>
        <pre>\n\nServer IP: {myIP}\nClient IP: {clientIP[0]}\n{request}\n{clients} requests.\n</pre>"""#   = " + str(RH) + "<br>Temp = " + str(T) + "</h1>"
        redirDebug = f"Server IP: {myIP}\nClient IP: {clientIP[0]}\n{request}\n{clients} requests.\n"
        stateis = html % stateis
        valid = False
        
#         <a href='http://{myIP}{urls['timerON']}'>OZON TIMER ON</a><br>
#         <a href='http://{myIP}{urls['timerOFF']}'>OZON TIMER OFF</a><br>
#         <!--<a href='http://{myIP}{urls['timerToggle']}'>OZON TIMER TOGGLE</a><br>-->
#<!--<a href='http://{myIP}{urls['ozonToggle']}'>OZON TOGGLE</a><br>-->        
        #stateis = "glenn"
#         if led_on == 6:
#             print("led on")
#             led.on()
#             stateis = "LED is on"
#         if led_off == 6:
#             print("led off")
#             led.off()
#             stateis = "LED is off"
#         if led_toggle == 6:
#             print("led toggle")
#             led.toggle()
#             stateis = "LED is toggled"
#         if ozonON == 6:
#             print("Ozon turning on")
#             stateis = redir % (f"Ozon has turned on\n{request}", redirDebug)
#             #relay.high()
#             ON = 1
#             woverride = True
#             valid = True
#         if ozonOFF == 6:
#             print("Ozon turning off")
#             stateis = redir % (f"Ozon has turned off\n{request}", redirDebug)
#             #relay.low()
#             ON = 0
#             woverride = True
#             valid = True
#         if ozonToggle == 6:
#             print("Ozon toggling...")
#             stateis = redir % (f"Ozon has toggled\n{request}", redirDebug)
#             relay.toggle()
#             woverride = True
#             valid = True
#         if timerON == 6:
#             print("Timer ON")
#             stateis = redir % (f"Timer is ON\n{request}", redirDebug)
#             TIMERON = 1
#             woverride = True
#             valid = True
#         if timerOFF == 6:
#             print("Timer OFF")
#             stateis = redir % (f"Timer is OFF\n{request}", redirDebug)
#             TIMERON = 0
#             woverride = True
#             valid = True
#         if timerToggle == 6:
#             print("Timer toggle")
#             stateis = redir % (f"Timer toggle\n{request}", redirDebug)
#             woverride = True
#             valid = True
        if relayON == 6:
            print("Relay turning on")
            stateis = redir % (f"Relay has turned on\n{request}", redirDebug)
            #relay.high()
            #ON = 1
            LATCH = 1
            woverride = True
            valid = True
        if relayOFF == 6:
            print("Relay turning off")
            stateis = redir % (f"Relay has turned off\n{request}", redirDebug)
            #relay.low()
            #ON = 0
            LATCH = 0
            woverride = True
            valid = True
        if relayStatus == 6:
            print("Relay status")
            stateis = (f"{str(relay.value())}")
            valid = True
        if overrideOFF == 6:
            print("Override OFF")
            stateis = redir % (f"Override is OFF\n{request}", redirDebug)
            woverride = False
            valid = True
            LATCH = 2
        #response = html % stateis
        response = stateis
        if root == 6:
            response = stateis
            valid = True
        if favicon >= 6:
            response = ''
            valid = True
        if valid:
            print("VALID")
            writer.write('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
            writer.write(response)
            await asyncio.sleep(0)
        await writer.drain()
        await writer.wait_closed()
        print('Client disconnected')
        clients += 1
        memprint()
        #led.toggle()




mT = []
mRH = []
# llen: How long should the list to calculate a mean be?
llen = 100
countdown = 0
recountdown = 0
cd = 10

# Initializing the dht22 - first values are bogus
try:
    foo, bar = dht22.read()
except:
    foo, bar = 31, 31

print("Init dht22", foo, bar, "and waiting...")
utime.sleep(6)


# Make this async:
#while True:
async def sensors():
    while True:
        global llen, countdown, recountdown, cd
        led.low()
        #LATCH
        try:
            T, RH = dht22.read()
            if not T or not RH:
                T, RH = 30, 30
        except:
            T, RH = 30, 30
            pass
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
        #print(mT)
        #print(mRH)
        
        firstRH = mRH[0]
        lastRH = mRH[-10]
        firstT = mT[0]
        lastT = mT[-10]
        
        for r in range(1, 5):
            #print(r)
            firstRH += mRH[r]
            firstT += mT[r]
        for q in range(-5, -1):
            #print(q)
            lastRH += mRH[q]
            lastT += mT[q]
        
        firstRH /= 5
        lastRH /= 5
        firstT /= 5
        lastT /= 5
        #firstRH = (mRH[0] + mRH[1]) /2 #+ mRH[5]) / 3
        #lastRH = (mRH[-10] + mRH[-11]) /2 # + mRH[-12]) / 3
        #firstT = (mT[0] + mT[1]) /2 # + mT [5]) / 3
        #lastT = (mT[-10] + mT[-11]) /2 # + mT[-12]) / 3
        
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
        print("firstRH [0] =", firstRH, ", lastRH [",(llen),"] =", lastRH, ", RH [now",llen,"] =", RH, ", futureRH [",((llen)*2),"] =", futureRH)
        print(" firstT [0] =", firstT,  ",  lastT [",(llen),"] =",  lastT, ",  T [now",llen,"] =", T,  ",  futureT [",((llen)*2),"] =", futureT)
        print("Latest mean: sRH =", sRH, "sT =", sT)
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
                #utime.sleep(1)
                await asyncio.sleep(1)
                led.low()
                print("{}".format(999999), '\r')
                #utime.sleep(1)
                await asyncio.sleep(1)
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
                        print("sRH:", sRH, ">", RT, "RHup =", RHup, ", Relay ON")
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
        await asyncio.sleep_ms(int(sleeptime/3))
        #time.sleep_ms(int(sleeptime/3))
        led.high()
        print("{:3.1f}".format(sT+10000), '\r')
        led.low()
        #time.sleep_ms(int(sleeptime/3))
        await asyncio.sleep_ms(int(sleeptime/3))
        led.high()
        print("{:3.1f}".format(sRH+20000), '\r')
        led.low()
        #time.sleep_ms(int(sleeptime/3))
        await asyncio.sleep_ms(int(sleeptime/3))
        led.high()
        sT = sRH = T = RH = None
        gc.collect()
        
clients = 1
woverride = False
async def main():
    global woverride
    global clients
    #buttonrun = asyncio.create_task(buttons())
    print("Setting up sensors...")
    sensor_worker = asyncio.create_task(sensors())
    #sensor_worker.run_forever()
    print("Setting up webserver")
    webserver = asyncio.create_task(asyncio.start_server(serve_client, "0.0.0.0", 80))
    
    ontime = 1
    offtime = 1
    countdownON = ontime
    countdownOFF = offtime
    POWER = True
    ka = 290

    while True:
            print(str(clients))
            #led.on()
            if ka >= 300:
                ka = 0
                if checkwebpage():
                    print("No prob")
                else:
                    print("Reconnect testing..")
                    myWifi.disconnect()
                    await asyncio.sleep(1)
                    myWifi.connect_to_network(wifisettings['ssid'], wifisettings['passwd'])
                    await asyncio.sleep(1)
                    memprint()
            else:
                ka += 1
            #while not wlan.isconnected() and wlan.status() >= 0:
            if not myWifi.getstatus() == 3:
                print(myWifi.getstatus())
                print(myWifi.ifconfig())
                myWifi.connect_to_network(wifisettings['ssid'], wifisettings['passwd'])
                await asyncio.sleep(2)
            print('.')
            #await asyncio.sleep(0.25)
            #led.off()
            
#             if ON and TIMERON:
#                 if countdownON > 1:
#                     relay.high()
#                     led.low()
#                     countdownON -= 1
#                     POWER = True
#                     print("countdownON =", countdownON)
#                     #utime.sleep(1)
#                     await asyncio.sleep(1)
#                 elif countdownON == 1:
#                     print("From ON to OFF in:", countdownON)
#                     #relay.low()
#                     #led.high()
#                     POWER = False
#                     countdownON = 0
#                     countdownOFF = offtime
#                     #utime.sleep(1)
#                     await asyncio.sleep(1)
#                 elif countdownOFF > 1:
#                     relay.low()
#                     led.high()
#                     countdownOFF -= 1
#                     POWER = False
#                     print("countdownOFF =", countdownOFF)
#                     #utime.sleep(1)
#                     await asyncio.sleep(1)
#                 elif countdownOFF == 1:
#                     print("From OFF to ON in:", countdownOFF)
#                     countdownOFF = 0
#                     countdownON = ontime
#                     POWER = True
#                     #utime.sleep(1)
#                     await asyncio.sleep(1)
#                 elif not TIMERON:
#                     print("ON :: Timer is OFF :: relay is on!")
#                     relay.high()
#                     led.low()
#                     POWER = True
#                     countdownON = ontime
#                     countdownOFF = offtime
#                     #utime.sleep(1)
#                     await asyncio.sleep(1)
#                 else:
#                     relay.high()
#                     led.low()
#                     #utime.sleep(1)
#                     await asyncio.sleep(1)
#             elif ON and not TIMERON:
#                 relay.high()
#                 led.low()
#                 print("ON :: Timer OFF")
#                 countdownON = ontime
#                 countdownOFF = offtime
#                 #utime.sleep(1)
#                 await asyncio.sleep(1)
#             else:
#                 relay.low()
#                 led.high()
#                 POWER = False
#                 print("OFF :: Relay OFF!")
#                 countdownON = ontime
#                 countdownOFF = offtime
#                 #utime.sleep(1)
#                 await asyncio.sleep(1)
#         
# #            else:
# #                print("WOVERRIDE =", str(woverride))
            await asyncio.sleep(1)
        
try:
    asyncio.run(main())
except:
    print("EPIC FAIL")
    raise
finally:
    print("in finally")
    asyncio.new_event_loop()