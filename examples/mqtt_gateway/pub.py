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

import json

import paho.mqtt.client as mqtt

# This is a simple MQTT publisher example.
# It connects to an MQTT broker, builds a payload and
# then publishes the message with a topic of "mqtt_network".

my_client = mqtt.Client()
my_client.connect("localhost", 1883, 60)
z = {'from_mqtt_client': 'hello'}

payload = json.dumps(z).encode()
my_client.publish("mqtt_network", payload)
my_client.disconnect()
