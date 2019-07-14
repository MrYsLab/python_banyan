#!/usr/bin/env python3

"""
monitor.py

Copyright (c) 2016 - 2019 Alan Yorinks All right reserved.

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

# monitor.py

import argparse
import signal
import sys

import zmq

from python_banyan.banyan_base import BanyanBase


# noinspection PyMethodMayBeStatic
class Monitor(BanyanBase):
    """
    This class subscribes to all messages on the back plane and prints out both topic and payload.
    """

    def __init__(self, back_plane_ip_address=None,
                 subscriber_port='43125', publisher_port='43124', process_name=None,
                 numpy=False):
        """
        This is constructor for the Monitor class

        :param back_plane_ip_address: IP address of the currently running backplane

        :param subscriber_port: subscriber port number - matches that of backplane

        :param publisher_port: publisher port number - matches that of backplane

        :param process_name: default name is "Monitor". Change using this parameter
        """

        # initialize the base class
        super(Monitor, self).__init__(back_plane_ip_address, subscriber_port,
                                      publisher_port, process_name=process_name,
                                      # loop_time=0.0,
                                      numpy=numpy)

        self.set_subscriber_topic('')

        # receive loop is defined in the base class
        try:
            self.receive_loop()
        except zmq.error.ZMQError:
            sys.exit()
        except KeyboardInterrupt:
            sys.exit()

    def incoming_message_processing(self, topic, payload):
        """
        This method is overwritten in the inherited class to process the data_files
        :param topic: Message topic string
        :param payload: Message content
        :return:
        """
        print(topic, payload)


def monitor():
    # noinspection PyShadowingNames

    parser = argparse.ArgumentParser()
    parser.add_argument("-b", dest="back_plane_ip_address", default="None",
                        help="None or IP address used by Back Plane")
    parser.add_argument("-m", dest="numpy", default="False", help="Set to True for numpy matrices")
    parser.add_argument("-n", dest="process_name", default="Monitor", help="Set process name in banner")
    parser.add_argument("-p", dest="publisher_port", default='43124',
                        help="Publisher IP port")
    parser.add_argument("-s", dest="subscriber_port", default='43125',
                        help="Subscriber IP port")

    args = parser.parse_args()
    kw_options = {}

    if args.back_plane_ip_address != 'None':
        kw_options['back_plane_ip_address'] = args.back_plane_ip_address

    kw_options['process_name'] = args.process_name

    kw_options['publisher_port'] = args.publisher_port
    kw_options['subscriber_port'] = args.subscriber_port

    if args.numpy == "True":
        kw_options['numpy'] = True
    else:
        kw_options['numpy'] = False

    Monitor(**kw_options)

# signal handler function called when Control-C occurs
# noinspection PyShadowingNames,PyUnusedLocal
def signal_handler(sig, frame):
    print('Exiting Through Signal Handler')
    raise KeyboardInterrupt

# listen for SIGINT
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


if __name__ == '__main__':
    monitor()
