"""
banyan_base.py

 Copyright (c) 2016, 2017 Alan Yorinks All right reserved.

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
from __future__ import unicode_literals

# Use argparse and signal if you wish to implement the argparse
# code located at the bottom of this file.

# import argparse
# import signal

import socket
import sys
import time
import umsgpack
import msgpack
import msgpack_numpy as m
import zmq
import psutil


class BanyanBase(object):
    """

    This is the base class for all Python Banyan components,
    encapsulating and acting as an abstraction layer for zeromq and message pack
    functionality.

    Banyan components are derived by inheriting from this class and
    overriding its methods as necessary.

    Banyan components have the capability to both publish and subscribe to user
    defined messages using the Banyan backplane.

    To import into  the derived class use:

           from python_banyan.banyan_base import BanyanBase

    """

    def __init__(self, back_plane_ip_address=None, subscriber_port='43125',
                 publisher_port='43124', process_name='None', loop_time=.1, numpy=False):
        """
        The __init__ method sets up all the ZeroMQ "plumbing"

        :param back_plane_ip_address: banyan_base back_planeIP Address -
                                      if not specified, it will be set to the
                                      local computer.

        :param subscriber_port: banyan_base back plane subscriber port.
               This must match that of the banyan_base backplane

        :param publisher_port: banyan_base back plane publisher port. This must match that of
                               the banyan_base backplane.

        :param process_name: Component identifier in banner at component startup.

        :param loop_time: Receive loop sleep time.

        :param numpy: Set true if you wish to include numpy matrices in your messages.
        """

        # call to super allows this class to be used in multiple inheritance scenarios when needed
        super(BanyanBase, self).__init__()

        self.backplane_exists = False

        self.back_plane_ip_address = None
        self.numpy = numpy

        # if using numpy apply the msgpack_numpy monkey patch
        if numpy:
            m.patch()

        # If no back plane address was specified, determine the IP address of the local machine
        if back_plane_ip_address:
            self.back_plane_ip_address = back_plane_ip_address
        else:
            # check for a running backplane
            for pid in psutil.pids():
                p = psutil.Process(pid)
                p_command = p.cmdline()
                if any('backplane' in s for s in p_command):
                    self.backplane_exists = True
                else:
                    continue

            if not self.backplane_exists:
                raise RuntimeError('Backplane is not running - please start it.')
            # determine this computer's IP address
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # use the google dns
            s.connect(('8.8.8.8', 0))
            self.back_plane_ip_address = s.getsockname()[0]

        self.subscriber_port = subscriber_port
        self.publisher_port = publisher_port

        self.loop_time = loop_time

        print()

        print('\n************************************************************')
        print(process_name + ' using Back Plane IP address: ' + self.back_plane_ip_address)
        print('Subscriber Port = ' + self.subscriber_port)
        print('Publisher  Port = ' + self.publisher_port)
        print('Loop Time = ' + str(loop_time) + ' seconds')
        print('************************************************************')

        # establish the zeromq sub and pub sockets and connect to the backplane
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
        """
        if sys.version_info[0] < 3:
            topic = topic.encode()
        if not type(topic) is str:
            raise TypeError('Subscriber topic must be python_banyan string')

        self.subscriber.setsockopt(zmq.SUBSCRIBE, topic.encode())

    def publish_payload(self, payload, topic=''):
        """
        This method will publish a python_banyan payload and its associated topic

        :param payload: Protocol message to be published

        :param topic: A string value
        """

        if not type(topic) is str:
            if sys.version_info[0] < 3:
                raise AttributeError('Publish topic must be python_banyan string', 'topic')
            else:
                raise TypeError('Publish topic must be python_banyan string', 'topic')

        # create python_banyan message pack payload
        if self.numpy:
            message = msgpack.packb(payload, default=m.encode)
        else:
            message = umsgpack.packb(payload)

        pub_envelope = topic.encode()
        self.publisher.send_multipart([pub_envelope, message])

    def receive_loop(self):
        """
        This is the receive loop for Banyan messages.

        This method may be overwritten to meet the needs
        of the application before handling received messages.

        """
        while True:
            try:
                data = self.subscriber.recv_multipart(zmq.NOBLOCK)
                if self.numpy:
                    payload = msgpack.unpackb(data[1], object_hook=m.decode)
                    self.incoming_message_processing(data[0].decode(), payload)
                else:
                    self.incoming_message_processing(data[0].decode(), umsgpack.unpackb(data[1]))
            # if no messages are available, zmq throws this exception
            except zmq.error.Again:
                try:
                    time.sleep(self.loop_time)
                except KeyboardInterrupt:
                    self.clean_up()
                    raise KeyboardInterrupt

    def incoming_message_processing(self, topic, payload):
        """
        Override this method with a custom Banyan message processor for subscribed messages.

        :param topic: Message Topic string.

        :param payload: Message Data.
        """
        print('this method should be overwritten in the child class', topic, payload)

    def clean_up(self):
        """
        Clean up before exiting - override if additional cleanup is necessary

        """
        self.publisher.close()
        self.subscriber.close()
        self.context.term()


# When creating a derived component, replicate the code below and replace
# banyan_base with a  name of your choice.

# def banyan_base():
#     # Allow user to bypass the IP address auto-discovery.
#     # This is necessary if the component resides on a computer
#     # other than the computing running the backplane.
#
#     parser = argparse.ArgumentParser()
#     parser.add_argument("-b", dest="back_plane_ip_address", default="None",
#                         help="None or IP address used by Back Plane")
#
#     # allow the user to specify a name for the component and have it shown on the console banner.
#     # modify the default process name to one you wish to see on the banner.
#     # change the default in the derived class to set the name
#     parser.add_argument("-n", dest="process_name", default="YOUR PROCESS NAME", help="Set process name in banner")
#
#     parser.add_argument("-t", dest="loop_time", default=".1", help="Event Loop Timer in seconds")
#
#     args = parser.parse_args()
#     kw_options = {}
#
#     if args.back_plane_ip_address != 'None':
#         kw_options['back_plane_ip_address'] = args.back_plane_ip_address
#
#     kw_options['process_name'] = args.process_name
#
#     kw_options['loop_time'] = float(args.loop_time)
#
#     # replace with the name of your class
#     app = BanyanBase(**kw_options)
#
#     # optionally add any subscriber topics here
#     app.set_subscriber_topic('python_banyan')
#
#     # optionally start the receive loop here or start it in your __init__
#     try:
#         app.receive_loop()
#     except KeyboardInterrupt:
#         sys.exit()
#
#     # signal handler function called when Control-C occurs
#     # noinspection PyShadowingNames,PyUnusedLocal,PyUnusedLocal
#     def signal_handler(signal, frame):
#         print("Control-C detected. See you soon.")
#         app.clean_up()
#         sys.exit(0)
#
#     # listen for SIGINT
#     signal.signal(signal.SIGINT, signal_handler)
#     signal.signal(signal.SIGTERM, signal_handler)
#
#
# if __name__ == '__main__':
#     # replace with name of function you defined above
#     banyan_base()
