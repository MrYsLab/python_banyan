import socket
import select
import rp2
from machine import Pin
import network
import time
import umsgpack


led = Pin("LED", Pin.OUT)
led.on()


wlan = network.WLAN(network.STA_IF)
wlan.active(True)

# set power mode to get Wi-Fi power-saving off (if needed)
wlan.config(pm=0xa11140)

wlan.connect('A-Net', 'Sam2Curly')

while not wlan.isconnected() and wlan.status() >= 0:
    print("Waiting to connect:")
    time.sleep(1)

print(wlan.ifconfig())

count = 0

# create a socket server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setblocking(0)

addr = ("", 31335)
server_socket.bind(addr)
server_socket.listen()


readable = [server_socket ] # list of readable sockets.  s is readable if a client is waiting.
i = 0
while True:
    # r will be a list of sockets with readable data
    r,w,e = select.select(readable,[],[],0)
    for rs in r: # iterate through readable sockets
        if rs is server_socket: # is it the server
            c,a = server_socket.accept()
            print((c, a))
            led.off()
            readable.append(c) # add the client
        else:
            # read from a client
            length = rs.recv(1)
            length = int.from_bytes(length, "big")
            if length:
                data = rs.recv(length)
                data = umsgpack.loads(data)
                print(data)

                payload = {'from pico_data': count}
                count += 1
                packed = umsgpack.dumps(payload)

                # get the length of the payload and express as a bytearray
                p_length = bytearray(len(packed).to_bytes(1, 'big'))

                # append the length to the packed bytarray
                p_length.extend(packed)

                # convert from bytearray to bytes
                packed = bytes(p_length)

                rs.sendall(packed)
                
    time.sleep(.001)
    
