"""
banyan_base_aio.py

 Copyright (c) 2018-2021 Alan Yorinks All right reserved.

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

import zmq.asyncio
import socket
import asyncio
import msgpack
import msgpack_numpy as m
import sys
import zmq
import psutil


# noinspection PyMethodMayBeStatic
class BanyanBaseAIO(object):
    """

    This is the asyncio base class for Python Banyan components,
    encapsulating and acting as an abstraction layer for zeromq and message pack
    functionality.

    Banyan components are derived by inheriting from this class and
    overriding its methods as necessary.

    Banyan components have the capability to both publish and subscribe to user
    defined messages using the Banyan backplane.

    To import into  the derived class use:

           from python_banyan.banyan_base import BanyanBase

    """

    # noinspection PyBroadException
    def __init__(self, back_plane_ip_address=None, subscriber_port='43125',
                 publisher_port='43124', process_name='None', numpy=False,
                 external_message_processor=None, receive_loop_idle_addition=None,
                 connect_time=0.3, subscriber_list=None, event_loop=None):

        """
        The __init__ method sets up all the ZeroMQ "plumbing"

        :param back_plane_ip_address: banyan_base back_planeIP Address -
                                      if not specified, it will be set to the
                                      local computer.

        :param subscriber_port: banyan_base back plane subscriber port.
               This must match that of the banyan_base backplane

        :param publisher_port: banyan_base back plane publisher port.
                               This must match that of the banyan_base backplane.

        :param process_name: Component identifier in banner at component startup.

        :param numpy: Set true if you wish to include numpy matrices in your messages.

        :param external_message_processor: external method to process messages

        :param receive_loop_idle_addition: an external method called in the idle section
                                           of the receive loop

        :param connect_time: a short delay to allow the component to connect to the Backplane
        """

        # call to super allows this class to be used in multiple inheritance
        # scenarios when needed
        super(BanyanBaseAIO, self).__init__()

        self.backplane_exists = False

        self.back_plane_ip_address = None
        self.numpy = numpy
        self.external_message_processor = external_message_processor
        self.receive_loop_idle_addition = receive_loop_idle_addition
        self.connect_time = connect_time
        self.subscriber_list = subscriber_list
        self.my_context = None
        self.subscriber = None
        self.publisher = None
        self.the_task = None

        if event_loop:
            self.event_loop = event_loop
        else:
            # fix for "not implemented" bugs in Python 3.8
            if sys.platform == 'win32':
                asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            self.event_loop = asyncio.get_event_loop()

        # if using numpy apply the msgpack_numpy monkey patch
        if numpy:
            m.patch()

        # If no back plane address was specified, determine the IP address of
        # the local machine
        if back_plane_ip_address:
            self.back_plane_ip_address = back_plane_ip_address
        else:
            # check for a running backplane
            for pid in psutil.pids():
                p = psutil.Process(pid)
                try:
                    p_command = p.cmdline()
                # ignore these psutil exceptions
                except (psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                try:
                    if any('backplane' in s for s in p_command):
                        self.backplane_exists = True
                    else:
                        continue
                except UnicodeDecodeError:
                    continue

            if not self.backplane_exists:
                raise RuntimeError('Backplane is not running - please start it.')
            # determine this computer's IP address
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # use the google dns
            try:
                s.connect(('8.8.8.8', 1))
                self.back_plane_ip_address = s.getsockname()[0]
            except Exception:
                self.back_plane_ip_address = '127.0.0.1'
            finally:
                s.close()

        self.subscriber_port = subscriber_port
        self.publisher_port = publisher_port

        print('\n************************************************************')
        print(process_name + ' using Back Plane IP address: ' + self.back_plane_ip_address)
        print('Subscriber Port = ' + self.subscriber_port)
        print('Publisher  Port = ' + self.publisher_port)
        print('************************************************************')

    async def get_subscriber(self):
        """
        Retrieve the zmq subscriber object

        :return: self.subscriber
        """
        return self.subscriber

    async def get_publisher(self):
        """
        Retrieve the zmq subscriber object

        :return: self.subscriber
        """
        return self.publisher

    # noinspection PyUnresolvedReferences
    async def begin(self, start_loop=True):
        """
        Create the zmq socket objects and conditionally start the receive loop.

        :param start_loop: If true start the receive loop within this method.
        """
        # establish the zeromq sub and pub sockets and connect to the backplane
        if not self.my_context:
            self.my_context = zmq.asyncio.Context()
        # noinspection PyUnresolvedReferences
        self.subscriber = self.my_context.socket(zmq.SUB)
        connect_string = "tcp://" + self.back_plane_ip_address + ':' + self.subscriber_port
        self.subscriber.connect(connect_string)

        self.publisher = self.my_context.socket(zmq.PUB)
        connect_string = "tcp://" + self.back_plane_ip_address + ':' + self.publisher_port
        self.publisher.connect(connect_string)

        if self.subscriber_list:
            for topic in self.subscriber_list:
                await self.set_subscriber_topic(topic)

        # Allow enough time for the TCP connection to the Backplane complete.
        # time.sleep(self.connect_time)
        await asyncio.sleep(self.connect_time)

        # start the receive_loop if start_loop is True
        if start_loop:
            self.the_task = self.event_loop.create_task(self.receive_loop())

    async def begin_receive_loop(self):
        """
        Start the receive loop independent of the begin method.
        """
        self.the_task = self.event_loop.create_task(self.receive_loop())

    async def pack(self, data):
        """
        Pack the data using msgpack

        :param data: item to be packed

        :return: the packed data

        """
        return msgpack.packb(data, use_bin_type=True)

    async def unpack(self, data):
        """
        Unpack the data item using msgpack.

        :param data: data to be unpacked.

        :return: unpacked data
        """
        return msgpack.unpackb(data, raw=False)

    async def numpy_pack(self, data):
        """
        Pack data if using numpy.

        :param data: item to be packed

        :return: the packed data
        """
        return msgpack.packb(data, default=m.encode)

    async def numpy_unpack(self, data):
        """
        Unpack data if numpy is in use.

        :param data: item to be packed

        :return: the unpacked data
        """
        return msgpack.unpackb(data[1], object_hook=m.decode)

    async def publish_payload(self, payload, topic=''):
        """
        This method will publish a python_banyan payload and its associated topic

        :param payload: Protocol message to be published

        :param topic: A string value
        """

        # make sure the topic is a string
        if not type(topic) is str:
            raise TypeError('Publish topic must be python_banyan string', 'topic')

        if self.numpy:
            message = await self.numpy_pack(payload)
        else:
            message = await self.pack(payload)

        pub_envelope = topic.encode()
        await self.publisher.send_multipart([pub_envelope, message])
        # await asyncio.sleep(1)

    async def receive_loop(self):
        """
        This is the receive loop for Banyan messages.

        This method may be overwritten to meet the needs
        of the application before handling received messages.

        """
        while True:
            data = await self.subscriber.recv_multipart()
            if self.numpy:
                payload2 = {}
                payload = await self.numpy_unpack(data[1])
                # convert keys to strings
                # this compensates for the breaking change in msgpack-numpy 0.4.1 to 0.4.2
                for key, value in payload.items():
                    if not type(key) == str:
                        key = key.decode('utf-8')
                        payload2[key] = value

                if payload2:
                    payload = payload2
                await self.incoming_message_processing(data[0].decode(), payload)
            else:
                payload = await self.unpack(data[1])
                await self.incoming_message_processing(data[0].decode(), payload)

    async def start_the_receive_loop(self):
        """

        """
        self.the_task = self.event_loop.create_task(self.receive_loop())

    async def incoming_message_processing(self, topic, payload):
        """
        Override this method with a custom Banyan message processor for subscribed messages.

        :param topic: Message Topic string.

        :param payload: Message Data.
        """

        print('this method should be overwritten in the child class', topic, payload)

    # noinspection PyUnresolvedReferences
    async def set_subscriber_topic(self, topic):
        """
        This method sets a subscriber topic.

        You can subscribe to multiple topics by calling this method for
        each topic.

        :param topic: A topic string
        """

        if not type(topic) is str:
            raise TypeError('Subscriber topic must be python_banyan string')

        self.subscriber.setsockopt(zmq.SUBSCRIBE, topic.encode())

    async def clean_up(self):
        """
        Clean up before exiting - override if additional cleanup is necessary

        """
        await self.publisher.close()
        await self.subscriber.close()
        await self.my_context.term()
