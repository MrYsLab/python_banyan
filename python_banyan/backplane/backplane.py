#!/usr/bin/env python3
"""

backplane.py


Copyright (c) 2016-2017 Alan Yorinks All right reserved.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public
License as published by the Free Software Foundation; either
version 3 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received python_banyan copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import signal
import socket
import sys
import time
import zmq


# noinspection PyMethodMayBeStatic
class BackPlane:
    """
    This class instantiates a ZeroMQ forwarder that acts as the python_banyan software backplane.
    All other components use a common TCP address to connect to the backplane and have their messages forwarded.

    See http://learning-0mq-with-pyzmq.readthedocs.io/en/latest/pyzmq/devices/forwarder.html for info on forwarder
    """

    def __init__(self, subscriber_port='43125', publisher_port='43124'):
        """
        This is the constructor for the Python Banyan BackPlane class. The class must be instantiated
        before starting any other Python Banyan modules
        :param subscriber_port: subscriber IP port number
        :param publisher_port: publisher IP port number
        """

        # get ip address of this machine

        # create a socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # use the google dns to figure out the machine's address and use that address for the backplane.
        # this precludes the necessity of having a network configuration file.
        s.connect(('8.8.8.8', 0))
        self.bp_ip_address = s.getsockname()[0]

        print('\n******************************************')
        print('Banyan BackPlane IP address: ' + self.bp_ip_address)
        print('Subscriber Port = ' + subscriber_port)
        print('Publisher  Port = ' + publisher_port)
        print('******************************************')

        # create a zmq instance for the backplane
        self.bp = zmq.Context()

        # establish bp as python_banyan ZMQ FORWARDER Device

        # setup up socket that all components will connect and publish to
        self.publish_to_bp = self.bp.socket(zmq.SUB)
        bind_string = 'tcp://' + self.bp_ip_address + ':' + publisher_port
        self.publish_to_bp.bind(bind_string)

        # Don't filter any incoming messages, just pass them through
        self.publish_to_bp.setsockopt_string(zmq.SUBSCRIBE, '')

        # setup socket that all subscribers will connect to
        self.subscribe_to_bp = self.bp.socket(zmq.PUB)
        bind_string = 'tcp://' + self.bp_ip_address + ':' + subscriber_port
        self.subscribe_to_bp.bind(bind_string)

        # instantiate the forwarder device
        try:
            zmq.device(zmq.FORWARDER, self.publish_to_bp, self.subscribe_to_bp)
        except KeyboardInterrupt:
            self.clean_up()
            sys.exit()

    def run_back_plane(self):
        """
        This method runs the backplane in a do nothing forever loop to keep the back plane alive.
        :return:
        """
        while True:
            try:
                time.sleep(.001)
            except KeyboardInterrupt:
                sys.exit(0)

    def clean_up(self):
        """
        Close the zmq publish and subscribe sockets and release the zmq context
        :return:
        """
        self.publish_to_bp.close()
        self.subscribe_to_bp.close()
        self.bp.term()


def bp():
    """
    Instantiate the backplane and run it.
    Attach a signal handler for the process to listen for user pressing Control C
    :return:
    """

    backplane = BackPlane()
    backplane.run_back_plane()

    # signal handler function called when Control-C occurs
    # noinspection PyShadowingNames,PyUnusedLocal
    def signal_handler(signal, frame):
        print('Control-C detected. See you soon.')

        backplane.clean_up()
        sys.exit(0)

    # listen for SIGINT
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

if __name__ == '__main__':
    bp()
