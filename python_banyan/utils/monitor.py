#!/usr/bin/env python3

"""
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

# monitor.py

import argparse
import signal
import sys
import time

from python_banyan.banyan_base import BanyanBase


# noinspection PyMethodMayBeStatic
class Monitor(BanyanBase):
    """
    This class subscribes to all messages on the back plane and prints out both topic and payload.
    """

    def __init__(self, back_plane_ip_address=None, subscriber_port='43125', publisher_port='43124', process_name=None):
        """
        This is constructor for the Monitor class
        :param back_plane_ip_address: IP address of the currently running backplane
        :param subscriber_port: subscriber port number - matches that of backplane
        :param publisher_port: publisher port number - matches that of backplane
        """

        # initialize the base class
        super().__init__(back_plane_ip_address, subscriber_port, publisher_port, process_name=process_name)

        # allow time for connection
        time.sleep(.03)
        self.set_subscriber_topic('')

        # receive loop is defined in the base class
        self.receive_loop()

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
    parser.add_argument("-n", dest="process_name", default="Monitor", help="Set process name in banner")

    args = parser.parse_args()
    kw_options = {}

    if args.back_plane_ip_address != 'None':
        kw_options['back_plane_ip_address'] = args.back_plane_ip_address

    kw_options['process_name'] = args.process_name

    my_monitor = Monitor(**kw_options)

    # signal handler function called when Control-C occurs
    # noinspection PyShadowingNames,PyUnusedLocal,PyUnusedLocal
    def signal_handler(signal, frame):
        print('Control-C detected. See you soon.')

        my_monitor.clean_up()
        sys.exit(0)

    # listen for SIGINT
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

if __name__ == '__main__':
    monitor()
