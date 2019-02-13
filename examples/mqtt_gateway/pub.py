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
