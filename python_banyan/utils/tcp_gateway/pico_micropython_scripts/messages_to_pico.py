import network, rp2, time
import socket
import umsgpack
from machine import Pin

led = Pin("LED", Pin.OUT)
led.on()

# set your WiFi Country
rp2.country('US')

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

# set power mode to get WiFi power-saving off (if needed)
wlan.config(pm = 0xa11140)

wlan.connect('A-Net', 'Sam2Curly')


while not wlan.isconnected() and wlan.status() >= 0:
 print("Waiting to connect:")
 time.sleep(1)

print(wlan.ifconfig())

# create a socket server
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

addr = ("",31335)
serversocket.bind(addr)
serversocket.listen()
(clientsocket, address) = serversocket.accept()
print((clientsocket, address))
led.off()

count = 0
while True:
    data = clientsocket.recv(1024)
    if data:
        z = umsgpack.loads(data)
        print(z)
    # payload = {'from_the_pico': count}
    # count += 1
    # packed = umsgpack.dumps(payload)
    # clientsocket.sendall(packed)
    # print('sending')



