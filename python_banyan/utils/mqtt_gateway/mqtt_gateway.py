"""
mqtt_gateway.py

 Copyright (c) 2018 - 2019 Alan Yorinks All right reserved.

 Python Banyan is free software; you can redistribute it and/or
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

import argparse
import signal
import sys
import zmq
import json

from python_banyan.banyan_base import BanyanBase
# noinspection PyPackageRequirements
import paho.mqtt.client as mqtt


# noinspection PyUnusedLocal
class MqttGateway(BanyanBase):
    """
    This class allows a subscription to multiple MQTT topics published on an MQTT
    broker and will republish these messages to the Banyan backplane.

    This class also allows a Banyan application to publish messages to an MQTT broker.
    The MQTT topic is set to the value of the mqtt_pub_topic parameter. The MQTT payload
    is the same as the Banyan payload
    """

    # noinspection PyUnusedLocal
    def __init__(self, back_plane_ip_address=None,
                 subscriber_port='43125', publisher_port='43124',
                 process_name='MQTT Gateway', loop_time=.0001,
                 numpy=False,
                 banyan_sub_topics='to_mqtt',
                 banyan_pub_topic='from_mqtt',
                 mqtt_addr='localhost',
                 mqtt_port=1883,
                 mqtt_sub_topics=None,
                 mqtt_pub_topic='from_banyan'):
        """

        :param back_plane_ip_address: Banyan backplane IP address
        :param subscriber_port: Banyan subscriber IP port
        :param publisher_port: Banyan publisher IP port
        :param process_name: Name to display in this component's header
        :param loop_time: Banyan idle loop time
        :param numpy: Numpy flag
        :param banyan_sub_topics: A list of Banyan topics we wish to receive
                                  that will forwarded to the MQTT network.
        :param banyan_pub_topic: Topic string for publishing "MQTT messages"
                                 to the Banyan network
        :param mqtt_addr: MQTT IP address
        :param mqtt_port: MQTT port
        :param mqtt_sub_topics: A list of MQTT topics we wish to receive from MQTT
                                and will forwarded to the Banyan network.
        :param mqtt_pub_topic: Topic string for publishing "Banyan messages"
                               to the MQTT network
        """

        # initialize the base class
        super(MqttGateway, self).__init__(back_plane_ip_address, subscriber_port,
                                          publisher_port, process_name='MqttGateway',
                                          loop_time=0.1,
                                          numpy=numpy)

        # save the publication topics
        self.banyan_pub_topic = banyan_pub_topic
        self.mqtt_pub_topic = mqtt_pub_topic

        # save the banyan subscription topics
        self.banyan_sub_topics = banyan_sub_topics

        # make sure it is in the form of a list
        if type(self.banyan_sub_topics) is not list:
            self.banyan_sub_topics = [self.banyan_sub_topics]

        # these topics are used by banyan components when they wish to publish a payload
        # to mqtt
        if self.banyan_sub_topics:
            for sub in self.banyan_sub_topics:
                self.set_subscriber_topic(sub)

        # save the mqtt topic list, ip addr and publication topic
        self.mqtt_sub_topics = mqtt_sub_topics

        # make sure it is in the form of a list
        if type(self.mqtt_sub_topics) is not list:
            self.mqtt_sub_topics = [self.mqtt_sub_topics]

        self.mqtt_addr = mqtt_addr
        self.mqtt_port = mqtt_port

        # establish the mqtt client and connect
        self.client = mqtt.Client()
        self.client.connect(self.mqtt_addr, self.mqtt_port, 60)
        self.client.on_connect = self.mqtt_on_connect
        self.client.on_message = self.mqtt_on_message
        self.client.loop_start()

        try:
            self.receive_loop()
        except zmq.error.ZMQError:
            sys.exit()
        except KeyboardInterrupt:
            sys.exit()

    def mqtt_on_connect(self, client, userdata, flags, rc):
        """
        standard mqtt on connect - see mqtt documentation for
        meaning of parameters
        :param client:
        :param userdata:
        :param flags:
        :param rc:
        :return:
        """
        print("MQTT Gateway Connected to MQTT {}:{} with result code {}.".format(self.mqtt_addr,
                                                                                 self.mqtt_port,
                                                                                 str(rc)))
        # when mqtt is connected to subscribe to mqtt topics
        if self.mqtt_sub_topics:
            for sub in self.mqtt_sub_topics:
                self.client.subscribe(sub)

    def mqtt_on_message(self, client, userdata, msg):
        """
        Republish mqtt messages in a Banyan format.
        See mqtt documentation for
        meaning of parameters.
        :param client:
        :param userdata:
        :param msg:
        :return:
        """
        m = msg.payload.decode()
        payload = json.loads(m)
        self.publish_payload(payload, self.banyan_pub_topic)

    def incoming_message_processing(self, topic, payload):
        """
        Publish a banyan message to the mqtt network
        :param topic: topic string
        :param payload: payload
        :return:
        """
        if topic == 'to_mqtt':
            payload = json.dumps(payload).encode()
            self.client.publish(self.mqtt_pub_topic, payload)


def mqtt_gateway():
    # allow user to bypass the IP address auto-discovery. This is necessary if the component resides on a computer
    # other than the computing running the backplane.

    parser = argparse.ArgumentParser()

    parser.add_argument("-a", dest="mqtt_ip_address", default="localhost",
                        help="IP address of mqtt broker")
    parser.add_argument("-b", dest="back_plane_ip_address", default="None",
                        help="None or IP address used by Back Plane", )
    parser.add_argument("-d", dest="mqtt_port", default=1883,
                        help="MQTT Port Number")
    parser.add_argument("-e", dest="banyan_pub_topic", default="from_mqtt",
                        help="Topic for messages to MQTT")
    parser.add_argument("-g", dest="banyan_sub_topics", nargs='+', default="to_mqtt",
                        help="Banyan topics space delimited: topic1 topic2 topic3"),
    parser.add_argument("-i", dest="mqtt_pub_topic", default="from_banyan",
                        help="Topic for messages sent to MQTT")
    parser.add_argument("-j", dest="mqtt_sub_topics", nargs='+', default="mqtt_network",
                        help="MQTT topics space delimited: topic1 topic2 topic3")
    parser.add_argument("-n", dest="process_name", default="MQTT Gateway", help="Set process name in banner")
    parser.add_argument("-p", dest="publisher_port", default='43124',
                        help="Publisher IP port")
    parser.add_argument("-s", dest="subscriber_port", default='43125',
                        help="Subscriber IP port")
    parser.add_argument("-t", dest="loop_time", default=".1", help="Event Loop Timer in seconds")

    args = parser.parse_args()
    kw_options = {}

    if args.back_plane_ip_address != 'None':
        kw_options['back_plane_ip_address'] = args.back_plane_ip_address

    kw_options = {'publisher_port': args.publisher_port,
                  'subscriber_port': args.subscriber_port,
                  'process_name': args.process_name,
                  'loop_time': float(args.loop_time),
                  'banyan_sub_topics': args.banyan_sub_topics,
                  'banyan_pub_topic': args.banyan_pub_topic,
                  'mqtt_addr': args.mqtt_ip_address,
                  'mqtt_port': args.mqtt_port,
                  'mqtt_sub_topics': args.mqtt_sub_topics,
                  'mqtt_pub_topic': args.mqtt_pub_topic,
                  }

    # replace with the name of your class
    MqttGateway(**kw_options)


# noinspection PyShadowingNames,PyUnusedLocal,PyUnusedLocal
# signal handler function called when Control-C occurs
# noinspection PyShadowingNames,PyUnusedLocal,PyUnusedLocal
def signal_handler(sig, frame):
    print('Exiting Through Signal Handler')
    raise KeyboardInterrupt


# listen for SIGINT
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == '__main__':
    mqtt_gateway()
