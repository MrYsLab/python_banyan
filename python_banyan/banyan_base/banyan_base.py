"""
Copyright (c) 2016, 2017 Alan Yorinks All right reserved.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public
License as published by the Free Software Foundation; either
version 3 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

banyan_base.py

"""

import socket
import sys
import time
import signal
import argparse
import umsgpack
import zmq


class BanyanBase(object):
    """

    This is the base class for all Python Banyan components. It encapsulates zeromq and message pack
    functionality. It methods should be overridden by the user in the derived class to meet the needs of the component.

    To import into  the derived class use:

           from python_banyan.banyan_base import BanyanBase

    """

    def __init__(self, back_plane_ip_address=None, subscriber_port='43125',
                 publisher_port='43124', process_name='None', loop_time=.1):
        """
        The __init__ method sets up all the ZeroMQ "plumbing"

        :param back_plane_ip_address: banyan_base back_planeIP Address - if not specified, it will be set to the
               local computer
        :param subscriber_port: banyan_base back plane subscriber port.
               This must match that of the banyan_base backplane
        :param publisher_port: banyan_base back plane publisher port. This must match that of the banyan_base backplane
        :param process_name: Component identifier
        :return:
        """

        self.back_plane_ip_address = None

        # If no back plane address was specified, determine the IP address of the local machine
        if back_plane_ip_address:
            self.back_plane_ip_address = back_plane_ip_address
        else:
            # determine this computer's IP address
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # use the google dns
            s.connect(('8.8.8.8', 0))
            self.back_plane_ip_address = s.getsockname()[0]

        self.subscriber_port = subscriber_port
        self.publisher_port = publisher_port

        self.loop_time = loop_time

        print('\n************************************************************')
        print(process_name + ' using Back Plane IP address: ' + self.back_plane_ip_address)
        print('Subscriber Port = ' + self.subscriber_port)
        print('Publisher  Port = ' + self.publisher_port)
        print('Loop Time = ' + str(loop_time) + ' seconds')
        print('************************************************************')

        # establish the zeriomq sub and pub sockets and connect to the backplane
        self.context = zmq.Context()
        self.subscriber = self.context.socket(zmq.SUB)
        connect_string = "tcp://" + self.back_plane_ip_address + ':' + self.subscriber_port
        self.subscriber.connect(connect_string)

        self.publisher = self.context.socket(zmq.PUB)
        connect_string = "tcp://" + self.back_plane_ip_address + ':' + self.publisher_port
        self.publisher.connect(connect_string)

    def set_subscriber_topic(self, topic):
        """
        This method sets a subscriber topic.

        You can subscribe to multiple topics by calling this method for
        each topic.

        :param topic: A topic string
        :return:
        """
        if not type(topic) is str:
            raise TypeError('Subscriber topic must be python_banyan string')

        self.subscriber.setsockopt(zmq.SUBSCRIBE, topic.encode())

    def publish_payload(self, payload, topic=''):
        """
        This method will publish a python_banyan payload and its associated topic

        :param payload: Protocol message to be published
        :param topic: A string value
        :return:
        """
        if not type(topic) is str:
            raise TypeError('Publish topic must be python_banyan string', 'topic')

        # create python_banyan message ack payload
        message = umsgpack.packb(payload)

        pub_envelope = topic.encode()
        self.publisher.send_multipart([pub_envelope, message])

    def receive_loop(self):
        """
        This is the receive loop for zmq messages.

        This method may be overwritten to meet the needs
        of the application before handling received messages.

        :return:
        """
        while True:
            try:
                data = self.subscriber.recv_multipart(zmq.NOBLOCK)
                self.incoming_message_processing(data[0].decode(), umsgpack.unpackb(data[1]))
            except zmq.error.Again:
                try:
                    time.sleep(self.loop_time)
                except KeyboardInterrupt:
                    self.clean_up()

    def incoming_message_processing(self, topic, payload):
        """
        Override this method with a custom python_banyan message processor for subscribed messages

        :param topic: Message Topic string
        :param payload: Message Data
        :return:
        """
        print('this method should be overwritten in the child class', topic, payload)

    def clean_up(self):
        """
        Clean up before exiting - override if additional cleanup is necessary

        :return:
        """
        self.publisher.close()
        self.subscriber.close()
        self.context.term()
        sys.exit(0)


# When creating a derived component, replicate the code below and replace banyan_base with a  name of your choice

def banyan_base():

    # allow user to bypass the IP address auto-discovery. This is necessary if the component resides on a computer
    # other than the computing running the backplane.

    parser = argparse.ArgumentParser()
    parser.add_argument("-b", dest="back_plane_ip_address", default="None",
                        help="None or IP address used by Back Plane")

    # allow the user to specify a name for the component and have it shown on the console banner.
    # modify the default process name to one you wish to see on the banner.
    # change the default in the derived class to set the name
    parser.add_argument("-n", dest="process_name", default="YOUR PROCESS NAME", help="Set process name in banner")

    parser.add_argument("-t", dest="loop_time", default=".1", help="Event Loop Timer in seconds")

    args = parser.parse_args()
    kw_options = {}

    if args.back_plane_ip_address != 'None':
        kw_options['back_plane_ip_address'] = args.back_plane_ip_address

    kw_options['process_name'] = args.process_name

    kw_options['loop_time'] = float(args.loop_time)

    # replace with the name of your class
    app = BanyanBase(**kw_options)

    # optionally add any subscriber topics here
    app.set_subscriber_topic('python_banyan')

    # optionally start the receive loop here or start it in your __init__
    app.receive_loop()

    # signal handler function called when Control-C occurs
    # noinspection PyShadowingNames,PyUnusedLocal,PyUnusedLocal
    def signal_handler(signal, frame):
        print("Control-C detected. See you soon.")
        app.clean_up()
        sys.exit(0)

    # listen for SIGINT
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

if __name__ == '__main__':
    # replace with name of function you defined above
    banyan_base()
