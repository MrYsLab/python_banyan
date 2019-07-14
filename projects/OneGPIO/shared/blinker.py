#!/usr/bin/env python3

"""
 This is the Python Banyan GUI that communicates with
 the Raspberry Pi Banyan Gateway

 Copyright (c) 2019 Alan Yorinks All right reserved.

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


class Blinker(BanyanBase):
    """
    This class may be instantiated and may communicate with any of the
    Banyan GPIO gateways to blink an LED.

    The default board type is Arduino, and the default GPIO pin
    is 10.

    Use the command line options to set the board type of your choice
    and the GPIO pin.
    """

    def __init__(self, **kwargs):
        super(Blinker, self).__init__(
            back_plane_ip_address=kwargs['back_plane_ip_address'],
            subscriber_port=kwargs['subscriber_port'],
            publisher_port=kwargs['publisher_port'],
            process_name=kwargs['process_name'])

        self.device_type = kwargs['device_type']
        if self.device_type not in ['arduino', 'esp8266', 'rpi']:
            raise RuntimeError('Invalid device type.')

        self.led_pin = int(kwargs['gpio_pin'])
        self.publish_topic = 'to_' + self.device_type + '_gateway'

        value = 0

        # set the pin mode

        payload = {'command': 'set_mode_digital_output',
                   'pin': self.led_pin, 'tag': 'blinker'}
        self.publish_payload(payload, self.publish_topic)

        while True:

            # blink the blinker led
            payload = {'command': 'digital_write', 'tag': 'blinker',
                       'value': value}
            self.publish_payload(payload, self.publish_topic)

            value = value ^ 1
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                sys.exit(0)


def blinker():
    parser = argparse.ArgumentParser()

    parser.add_argument("-b", dest="back_plane_ip_address", default="None",
                        help="None or IP address used by Back Plane")
    # allow the user to specify a name for the component and have it shown on
    # the console banner.
    # modify the default process name to one you wish to see on the banner.
    # change the default in the derived class to set the name

    # add a device type - choices are arduino, eps8266, and rpi
    parser.add_argument("-d", dest="device_type", default="arduino",
                        help="Set the device type: arduino, esp8266, or rpi")
    parser.add_argument("-g", dest="gpio_pin", default="10",
                        help="Set the LED GPIO pin number.")
    parser.add_argument("-n", dest="process_name", default="blinker",
                        help="Set process name in banner")
    parser.add_argument("-p", dest="publisher_port", default='43124',
                        help="Publisher IP port")
    parser.add_argument("-s", dest="subscriber_port", default='43125',
                        help="Subscriber IP port")

    args = parser.parse_args()

    if args.back_plane_ip_address == 'None':
        args.back_plane_ip_address = None
    kw_options = {'back_plane_ip_address': args.back_plane_ip_address,
                  'publisher_port': args.publisher_port,
                  'subscriber_port': args.subscriber_port,
                  'process_name': args.process_name,
                  'device_type': args.device_type,
                  'gpio_pin': args.gpio_pin}

    # replace with the name of your class
    Blinker(**kw_options)


def signal_handler(sig, frame):
    print('Exiting Through Signal Handler')
    raise KeyboardInterrupt


# listen for SIGINT
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


if __name__ == '__main__':
    blinker()
