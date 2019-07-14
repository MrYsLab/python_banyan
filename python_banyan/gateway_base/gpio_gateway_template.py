#!/usr/bin/env python3

"""
crickit_gatewaySAVE.py

 Copyright (c) 2017-2019 Alan Yorinks All right reserved.

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

from python_banyan.gateway_base import GatewayBase
import argparse
import signal
import sys


class GpioGatewayTemplate(GatewayBase):
    """
    This is a good starting point for creating your own Banyan GPIO Gateway

    Search for GpioGatewayTemplate and gpio_gateway_template, and then replace
    with a names of your own making.

    Change the -l and -n options at the bottom of this file
    to be consistent with the specific board type
    """

    # noinspection PyDefaultArgument,PyRedundantParentheses
    def __init__(self, *subscriber_list, **kwargs):
        """

        :param subscriber_list: a tuple or list of topics to be subscribed to
        :param kwargs: contains the following parameters:

            back_plane_ip_address: banyan_base back_planeIP Address -
               if not specified, it will be set to the local computer
            subscriber_port: banyan_base back plane subscriber port.
               This must match that of the banyan_base backplane
            publisher_port: banyan_base back plane publisher port.
                               This must match that of the banyan_base
                               backplane
            process_name: Component identifier
            board_type: target micro-controller type ID

        """
        # initialize the parent
        super(GpioGatewayTemplate, self).__init__(
            subscriber_list=subscriber_list,
            back_plane_ip_address=kwargs[
                'back_plane_ip_address'],
            subscriber_port=kwargs[
                'subscriber_port'],
            publisher_port=kwargs[
                'publisher_port'],
            process_name=kwargs[
                'process_name'],
            board_type=kwargs['board_type']
        )
        # start the banyan receive loop
        try:
            self.receive_loop()
        except KeyboardInterrupt:
            self.clean_up()
            sys.exit(0)

    def init_pins_dictionary(self):
        """
        The pins dictionary is an array of dictionary items that you create
        to describe each GPIO pin. In this dictionary, you can store things
        such as the pins current mode, the last value reported for an input pin
        callback method for an input pin, etc.
        :return:
        """
        self.pins_dictionary = []

    def additional_banyan_messages(self, topic, payload):
        """
        This method will pass any messages not handled by this class to the
        specific gateway class. Must be overwritten by the hardware gateway
        class.
        :param topic: message topic
        :param payload: message payload
        """
        raise NotImplementedError

    def analog_write(self, topic, payload):
        """
        This method will pass any messages not handled by this class to the
        specific gateway class. Must be overwritten by the hardware gateway
        class.
        :param topic: message topic
        :param payload: message payload
        """
        raise NotImplementedError

    def digital_write(self, topic, payload):
        """
        This method will pass any messages not handled by this class to the
        specific gateway class. Must be overwritten by the hardware gateway
        class.
        :param topic: message topic
        :param payload: message payload
        """
        raise NotImplementedError

    def disable_analog_reporting(self, topic, payload):
        """
        This method will pass any messages not handled by this class to the
        specific gateway class. Must be overwritten by the hardware gateway
        class.
        :param topic: message topic
        :param payload: message payload
        """
        raise NotImplementedError

    def disable_digital_reporting(self, topic, payload):
        """
        This method will pass any messages not handled by this class to the
        specific gateway class. Must be overwritten by the hardware gateway
        class.
        :param topic: message topic
        :param payload: message payload
        """
        raise NotImplementedError

    def enable_analog_reporting(self, topic, payload):
        """
        This method will pass any messages not handled by this class to the
        specific gateway class. Must be overwritten by the hardware gateway
        class.
        :param topic: message topic
        :param payload: message payload
        """
        raise NotImplementedError

    def enable_digital_reporting(self, topic, payload):
        """
        This method will pass any messages not handled by this class to the
        specific gateway class. Must be overwritten by the hardware gateway
        class.
        :param topic: message topic
        :param payload: message payload
        """
        raise NotImplementedError

    def i2c_read(self, topic, payload):
        """
        This method will pass any messages not handled by this class to the
        specific gateway class. Must be overwritten by the hardware gateway
        class.
        :param topic: message topic
        :param payload: message payload
        """
        raise NotImplementedError

    def i2c_write(self, topic, payload):
        """
        This method will pass any messages not handled by this class to the
        specific gateway class. Must be overwritten by the hardware gateway
        class.
        :param topic: message topic
        :param payload: message payload
        """
        raise NotImplementedError

    def play_tone(self, topic, payload):
        """
        This method will pass any messages not handled by this class to the
        specific gateway class. Must be overwritten by the hardware gateway
        class.
        :param topic: message topic
        :param payload: message payload
        """
        raise NotImplementedError

    def pwm_write(self, topic, payload):
        """
        This method will pass any messages not handled by this class to the
        specific gateway class. Must be overwritten by the hardware gateway
        class.
        :param topic: message topic
        :param payload: message payload
        """
        raise NotImplementedError

    def servo_position(self, topic, payload):
        """
        This method will pass any messages not handled by this class to the
        specific gateway class. Must be overwritten by the hardware gateway
        class.
        :param topic: message topic
        :param payload: message payload
        """
        raise NotImplementedError

    def set_mode_analog_input(self, topic, payload):
        """
        This method will pass any messages not handled by this class to the
        specific gateway class. Must be overwritten by the hardware gateway
        class.
        :param topic: message topic
        :param payload: message payload
        """
        raise NotImplementedError

    def set_mode_digital_input(self, topic, payload):
        """
        This method will pass any messages not handled by this class to the
        specific gateway class. Must be overwritten by the hardware gateway
        class.
        :param topic: message topic
        :param payload: message payload
        """
        raise NotImplementedError

    def set_mode_digital_input_pullup(self, topic, payload):
        """
        This method will pass any messages not handled by this class to the
        specific gateway class. Must be overwritten by the hardware gateway
        class.
        :param topic: message topic
        :param payload: message payload
        """
        raise NotImplementedError

    def set_mode_digital_output(self, topic, payload):
        """
        This method will pass any messages not handled by this class to the
        specific gateway class. Must be overwritten by the hardware gateway
        class.
        :param topic: message topic
        :param payload: message payload
        """
        raise NotImplementedError

    def set_mode_i2c(self, topic, payload):
        """
        This method will pass any messages not handled by this class to the
        specific gateway class. Must be overwritten by the hardware gateway
        class.
        :param topic: message topic
        :param payload: message payload
        """
        raise NotImplementedError

    def set_mode_pwm(self, topic, payload):
        """
        This method will pass any messages not handled by this class to the
        specific gateway class. Must be overwritten by the hardware gateway
        class.
        :param topic: message topic
        :param payload: message payload
        """
        raise NotImplementedError

    def set_mode_servo(self, topic, payload):
        """
        This method will pass any messages not handled by this class to the
        specific gateway class. Must be overwritten by the hardware gateway
        class.
        :param topic: message topic
        :param payload: message payload
        """
        raise NotImplementedError

    def set_mode_sonar(self, topic, payload):
        """
        This method will pass any messages not handled by this class to the
        specific gateway class. Must be overwritten by the hardware gateway
        class.
        :param topic: message topic
        :param payload: message payload
        """
        raise NotImplementedError

    def set_mode_stepper(self, topic, payload):
        """
        Set the mode for the specific board.
        Must be overwritten by the hardware gateway class.
        :param topic: message topic
        :param payload: message payload
        """
        raise NotImplementedError

    def set_mode_tone(self, topic, payload):
        """
        Must be overwritten by the hardware gateway class.
        Handles a digital write
        :param topic: message topic
        :param payload: message payload
        """
        raise NotImplementedError

    def digital_read(self, pin):
        raise NotImplementedError

    def stepper_write(self, topic, payload):
        """
        Must be overwritten by the hardware gateway class.
        Handles a pwm write
        :param topic: message topic
        :param payload: message payload
        """
        raise NotImplementedError


def gpio_gateway_template():
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", dest="back_plane_ip_address", default="None",
                        help="None or IP address used by Back Plane")
    parser.add_argument("-d", dest="board_type", default="None",
                        help="This parameter identifies the target GPIO "
                             "device")
    parser.add_argument("-l", dest="subscriber_list",
                        default="from_device_gui", nargs='+',
                        help="Banyan topics space delimited: topic1 topic2 "
                             "topic3")
    parser.add_argument("-n", dest="process_name", default="DeviceGateway",
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
    if args.board_type == 'None':
        args.back_plane_ip_address = None
    kw_options = {
        'back_plane_ip_address': args.back_plane_ip_address,
        'publisher_port': args.publisher_port,
        'subscriber_port': args.subscriber_port,
        'process_name': args.process_name,
        'loop_time': float(args.loop_time),
        'board_type': args.board_type}

    try:
        GpioGatewayTemplate(args.subscriber_list, **kw_options)
    except KeyboardInterrupt:
        sys.exit()


# signal handler function called when Control-C occurs
# noinspection PyShadowingNames,PyUnusedLocal,PyUnusedLocal
def signal_handler(sig, frame):
    print('Exiting Through Signal Handler')
    raise KeyboardInterrupt


# listen for SIGINT
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == '__main__':
    # replace with name of function you defined above
    gpio_gateway_template()
