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
