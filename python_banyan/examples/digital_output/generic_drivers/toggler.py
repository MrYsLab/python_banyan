# !/usr/bin/env python3

"""
Copyright (c) 2016 Alan Yorinks All right reserved.

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

import sys
import signal
import argparse
import time

from python_banyan.banyan_base import BanyanBase


class Toggler(BanyanBase):
    """
    This class is a subscriber for "tick" messages. When a tick message is received, it will toggle
    a state variable and then  publish a digital_output message with a payload reflecting the current state.

    It is independent of any specific hardware platform.
    """

    def __init__(self, back_plane_ip_address=None, subscriber_port='43125',
                 publisher_port='43124', process_name=None, loop_time=.1):
        """


        :param back_plane_ip_address:
        :param subscriber_port:
        :param publisher_port:
        :param process_name:
        :param loop_time:
        """

        # initialize the parent
        super().__init__(back_plane_ip_address, subscriber_port, publisher_port, process_name=process_name,
                         loop_time=loop_time)

        # allow time for zmq connections to be established
        time.sleep(.03)

        # subscribe to topics
        self.set_subscriber_topic('tick')

        # last digital output state
        self.tick_tock = 0

        self.receive_loop()

    def incoming_message_processing(self, topic, payload):
        """
        This method will toggle the tick_tock state with each incoming tick.
        It will then publish the new state as a digital_output topic message
        :param topic: Message Topic string
        :param payload: Message Data
        :return:
        """
        if topic == 'tick':
            self.tick_tock ^= 1
            payload = {'command': 'set_state', 'state': self.tick_tock}
            self.publish_payload(payload, 'digital_output', )


def toggler():
    # noinspection PyShadowingNames

    parser = argparse.ArgumentParser()
    parser.add_argument("-b", dest="back_plane_ip_address", default="None",
                        help="None or IP address used by Back Plane")
    parser.add_argument("-n", dest="process_name", default="Arduino Digital Output",
                        help="Set process name in banner")
    parser.add_argument("-t", dest="loop_time", default=".1", help="Event Loop Timer in seconds")

    args = parser.parse_args()
    kw_options = {}

    if args.back_plane_ip_address != 'None':
        kw_options['back_plane_ip_address'] = args.back_plane_ip_address

    kw_options['process_name'] = args.process_name
    kw_options['loop_time'] = float(args.loop_time)

    my_tick_listener = Toggler(**kw_options)

    # signal handler function called when Control-C occurs
    # noinspection PyShadowingNames,PyUnusedLocal,PyUnusedLocal
    def signal_handler(signal, frame):
        print('Control-C detected. See you soon.')

        my_tick_listener.clean_up()
        sys.exit(0)

    # listen for SIGINT
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


if __name__ == '__main__':
    toggler()
