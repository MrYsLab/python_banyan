"""
tcp_gateway.py

 Copyright (c) 2022 Alan Yorinks All right reserved.

 The tcp_gateway is free software; you can redistribute it and/or
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
import asyncio
import signal
import sys
import zmq

from python_banyan.banyan_base_aio import BanyanBaseAIO
from python_banyan.utils.tcp_gateway.tcp_socket import TcpSocket


class TcpGateWay(BanyanBaseAIO):
    """
    This class is a gateway between a python-banyan network and a TCP socket.

    The TcpGateway serves as a simple connector between a python-banyan network and a TCP
    server. It acts as a TCP client and connects to a TCP server.
    The connected TCP server must have the capability to both MessagePack encode and
    decode messages. The TcpGateway does not provide any encoding or decoding of its own.
    """

    # noinspection PyUnusedLocal
    def __init__(self, tcp_server_ip_address=None, tcp_server_ip_port=31335,
                 subscriber_list=None, banyan_pub_topic=None, back_plane_ip_address=None,
                 subscriber_port='43125', publisher_port='43124',
                 process_name='TCPGateWay', event_loop=None, auto_start=True):
        """
        :param tcp_server_ip_address: TCP IP address of server in string format
        :param tcp_server_ip_port: TCP IP port of server in numerical format
        :param subscriber_list: A list of banyan topics
        :param banyan_pub_topic: published message topic
        :param back_plane_ip_address: Banyan backplane IP address - will be auto-detected
        :param subscriber_port: Banyan subscriber port
        :param publisher_port: Banyan publisher port
        :param process_name: TCP Gateway
        :param event_loop: asyncio event loop
        :param auto_start: automatically start the tasks
        """
        # initialize the base class
        super(TcpGateWay, self).__init__(back_plane_ip_address, subscriber_port,
                                          publisher_port, process_name=process_name)

        if not tcp_server_ip_address:
            raise RuntimeError("A TCP IP address for the TCP server must be provided.")

        self.tcp_server_ip_address = tcp_server_ip_address

        self.tcp_server_ip_port = tcp_server_ip_port

        # save the publication topic
        if not banyan_pub_topic:
            raise RuntimeError('A publishing topic must be provided')

        # encode the topic
        self.banyan_pub_topic = banyan_pub_topic.encode()

        if not subscriber_list:
            raise RuntimeError('A list of subscription topics must be provided')

        self.subscriber_list = subscriber_list

        if not self.back_plane_ip_address:
            self.back_plane_ip_address = back_plane_ip_address

        self.subscriber_port = subscriber_port

        self.publisher_port = publisher_port

        # if the user passes in a single topic, convert the topic to a list of topics
        if type(self.subscriber_list) is not list:
            self.subscriber_list = [self.subscriber_list]

        if not event_loop:
            self.event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.event_loop)

        # tcp client socket
        self.sock = None

        self.tcp_recv_task = None

        if auto_start:
            self.event_loop.run_until_complete(self.start_aio())

    async def start_aio(self):
        """
        Start up the tasks
        """

        await self.begin()

        self.sock = TcpSocket(self.tcp_server_ip_address, self.tcp_server_ip_port,
                              self.event_loop)
        await self.sock.start()

        self.the_task = self.event_loop.create_task(self._receive_tcp_data())

        while True:
            await asyncio.sleep(.1)

    async def _receive_tcp_data(self):
        while True:
            # get the length of the next packet
            byte_val = await self.sock.read(1)
            length = int.from_bytes(byte_val, "big")

            pico_packet = await self.sock.read(length)

            await self.publisher.send_multipart([self.banyan_pub_topic, pico_packet])

    async def receive_loop(self):
        """
        This is the receive loop for Banyan messages.

        This method may be overwritten to meet the needs
        of the application before handling received messages.

        """
        while True:
            data = await self.subscriber.recv_multipart()
            msg = data[1]
            # p_length = len(msg)
            # msg = await self.unpack(data[1])
            # get the length of the payload and express as a bytearray
            p_length = bytearray(len(msg).to_bytes(1, 'big'))

            # append the length to the packed bytearray
            p_length.extend(msg)

            # convert from bytearray to bytes
            msg = bytes(p_length)
            # print(f'Message from PC host: {msg}')
            await self.sock.write(msg)


def tcp_gateway():
    # allow user to bypass the IP address auto-discovery. This is necessary if the component resides on a computer
    # other than the computing running the backplane.

    parser = argparse.ArgumentParser()

    parser.add_argument("-a", dest="tcp_ip_address", default="None",
                        help="IP address TCP Server")
    parser.add_argument("-b", dest="back_plane_ip_address", default="None",
                        help="None or IP address used by Back Plane", )
    parser.add_argument("-e", dest="banyan_pub_topic", default="from_pico",
                        help="Topic for messages to the host PC")
    parser.add_argument("-g", dest="subscription_list", nargs='+', default="figura",
                        help="Banyan topics space delimited: topic1 topic2 topic3"),
    parser.add_argument("-l", dest="event_loop", default="None",
                        help="asyncio event loop")
    parser.add_argument("-n", dest="tcp_port", default=31335,
                        help="TCP Server Port Number")
    parser.add_argument("-p", dest="publisher_port", default='43124',
                        help="Publisher IP port")
    parser.add_argument("-s", dest="subscriber_port", default='43125',
                        help="Subscriber IP port")
    parser.add_argument("-z", dest="process_name", default="TcpGateway",
                        help="Name of this gateway")

    args = parser.parse_args()
    kw_options = {}

    if args.back_plane_ip_address != 'None':
        kw_options['back_plane_ip_address'] = args.back_plane_ip_address
    else:
        args.back_plane_ip_address = None

    if args.event_loop == 'None':
        args.event_loop = None
    else:
        kw_options['event_loop'] = args.event_loop

    kw_options = {
                  'back_plane_ip_address': args.back_plane_ip_address,
                  'tcp_server_ip_address': args.tcp_ip_address,
                  'tcp_server_ip_port': args.tcp_port,
                  'publisher_port': args.publisher_port,
                  'subscriber_port': args.subscriber_port,
                  'process_name': args.process_name,
                  'subscriber_list': args.subscription_list,
                  'banyan_pub_topic': args.banyan_pub_topic,
                  'event_loop': args.event_loop
                  }

    TcpGateWay(**kw_options)


# noinspection PyShadowingNames,PyUnusedLocal,PyUnusedLocal
# signal handler function called when Control-C occurs
# noinspection PyShadowingNames,PyUnusedLocal,PyUnusedLocal
def signal_handler(sig, frame):
    print('Exiting Through Signal Handler')
    sys.exit(0)


# listen for SIGINT
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == '__main__':
    tcp_gateway()
