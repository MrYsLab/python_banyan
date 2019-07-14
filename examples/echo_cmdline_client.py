#!/usr/bin/env python3

"""
echo_cmdline_client.py

 Copyright (c) 2018-2019 Alan Yorinks All right reserved.

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
import time

from python_banyan.banyan_base import BanyanBase


class EchoCmdClient(BanyanBase):
    """
    This is an echo client that will allow the user
    to specify command line arguments to change the default behavior
    of the client.

    It sends out a series of messages and expects an
    echo reply from the server. When it completes, press enter, and it
    will send a message to the server so that it also quits

    To use: 1. Start the backplane.
            2. Start the server.
            3. Start this client.

    usage: echo_cmdline_client.py [-h] [-b BACK_PLANE_IP_ADDRESS]
                      [-m NUMBER_OF_MESSAGES] [-n PROCESS_NAME]
                      [-p PUBLISHER_PORT] [-s SUBSCRIBER_PORT] [-t LOOP_TIME]

    optional arguments:
      -h, --help            show this help message and exit
      -b BACK_PLANE_IP_ADDRESS
                            None or IP address used by Back Plane
      -m NUMBER_OF_MESSAGES
                            Number of messages to publish
      -n PROCESS_NAME       Set process name in banner
      -p PUBLISHER_PORT     Publisher IP port
      -s SUBSCRIBER_PORT    Subscriber IP port
      -t LOOP_TIME          Event Loop Timer in seconds
    """

    def __init__(self, **kwargs):

        """
        kwargs is a dictionary that will contain the following keys:

        :param back_plane_ip_address: banyan_base back_planeIP Address -
                                    if not specified, it will be set to the
                                    local computer
        :param subscriber_port: banyan_base back plane subscriber port.
               This must match that of the banyan_base backplane
        :param publisher_port: banyan_base back plane publisher port.
                               This must match that of the
                               banyan_base backplane.
        :param number_of_messages: number of message to transmit
        :param process_name: Component identifier
        :param loop_time: receive loop sleep time

        """

        # initialize the parent
        super(EchoCmdClient, self).__init__(back_plane_ip_address=kwargs['back_plane_ip_address'],
                                            subscriber_port=kwargs['subscriber_port'],
                                            publisher_port=kwargs['publisher_port'],
                                            process_name=kwargs['process_name'],
                                            loop_time=kwargs['loop_time'])

        # allow zmq connections to establish
        time.sleep(.3)

        # accept banyan messages with the topic of reply
        self.set_subscriber_topic('reply')

        # sequence number of messages
        self.message_number = kwargs['number_of_messages']

        # number of messages to send
        self.number_of_messages = kwargs['number_of_messages']

        # send the first message - make sure that the server is already started
        self.publish_payload({'message_number': self.message_number}, 'echo')
        self.message_number -= 1

        # get the reply messages
        try:
            self.receive_loop()
        except KeyboardInterrupt:
            self.clean_up()
            sys.exit(0)

    def incoming_message_processing(self, topic, payload):
        """
        Messages are sent here from the receive_loop
        :param topic: Message Topic string
        :param payload: Message Data
        :return:
        """

        # When a message is received and its number is zero, finish up.
        if payload['message_number'] == 0:
            print(str(self.number_of_messages) + ' messages sent and received. ')
            input('Press enter to exit.')
            self.clean_up()
            sys.exit(0)
        # bump the message number and send the message out
        else:
            self.message_number -= 1
            if self.message_number >= 0:
                self.publish_payload({'message_number': self.message_number}, 'echo')


def echo_cmdline_client():
    parser = argparse.ArgumentParser()
    # allow user to bypass the IP address auto-discovery.
    # This is necessary if the component resides on a computer
    # other than the computing running the backplane.
    parser.add_argument("-b", dest="back_plane_ip_address", default="None",
                        help="None or IP address used by Back Plane")
    parser.add_argument("-m", dest="number_of_messages", default="10",
                        help="Number of messages to publish")
    # allow the user to specify a name for the component and have it shown on the console banner.
    # modify the default process name to one you wish to see on the banner.
    # change the default in the derived class to set the name
    parser.add_argument("-n", dest="process_name", default="EchoCmdClient",
                        help="Set process name in banner")
    parser.add_argument("-p", dest="publisher_port", default='43124',
                        help="Publisher IP port")
    parser.add_argument("-s", dest="subscriber_port", default='43125',
                        help="Subscriber IP port")
    parser.add_argument("-t", dest="loop_time", default=".1",
                        help="Event Loop Timer in seconds")

    args = parser.parse_args()

    if args.back_plane_ip_address == 'None':
        args.back_plane_ip_address = None
    kw_options = {'back_plane_ip_address': args.back_plane_ip_address,
                  'number_of_messages': int(args.number_of_messages),
                  'publisher_port': args.publisher_port,
                  'subscriber_port': args.subscriber_port,
                  'process_name': args.process_name,
                  'loop_time': float(args.loop_time)}

    # replace with the name of your class
    EchoCmdClient(**kw_options)


# signal handler function called when Control-C occurs
# noinspection PyShadowingNames,PyUnusedLocal,PyUnusedLocal
def signal_handler(sig, frame):
    print('Exiting Through Signal Handler')
    raise KeyboardInterrupt


# listen for SIGINT
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


if __name__ == '__main__':
    echo_cmdline_client()
