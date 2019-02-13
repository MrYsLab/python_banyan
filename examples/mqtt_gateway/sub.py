"""
 Copyright (c) 2019 Alan Yorinks All right reserved.

 This program is free software; you can redistribute it and/or
 modify it under the terms of the GNU AFFERO GENERAL PUBLIC LICENSE
 Version 3 as published by the Free Software Foundation; either
 or (at your option) any later version.
 This library is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 General Public License for more details.

 You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
 along with this library; if not, write to the Free Software
 Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"""

import paho.mqtt.client as mqtt
import json


# This is a simple MQTT subscriber example.
# It connects to an MQTT broker and
# subscribes to "mqtt_network" messages
# and prints a message when one is received.

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("mqtt_network")
    client.subscribe("from_banyan")


def on_message(client, userdata, msg):
    m = msg.payload.decode()
    x = json.loads(m)
    print(x)


my_client = mqtt.Client()
my_client.connect("localhost", 1883, 60)

my_client.on_connect = on_connect
my_client.on_message = on_message

my_client.loop_forever()
