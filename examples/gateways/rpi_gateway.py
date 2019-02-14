"""
 Copyright (c) 2018-2019 Alan Yorinks All rights reserved.

 This program is free software; you can redistribute it and/or
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
import pigpio
from gateway_base import GatewayBase


# noinspection PyAbstractClass,PyMethodMayBeStatic
class RPiGateway(GatewayBase):
    def __init__(self, *subscription_list, back_plane_ip_address=None, subscriber_port='43125',
                 publisher_port='43124', process_name='RpiGateway', loop_time=.1,
                 publisher_topic='rpi_callback_data'):

        # pin 2 is for i2c - normally not used as a GPIO pin
        self.gpio_pins = [2, 4, 5, 6, 11, 12, 13, 16, 17, 18, 22, 23, 24, 25, 26, 27]

        super(RPiGateway, self).__init__(back_plane_ip_address=back_plane_ip_address,
                                         subscriber_port=subscriber_port,
                                         publisher_port=publisher_port,
                                         process_name=process_name,
                                         loop_time=loop_time,
                                         subscription_list=subscription_list,
                                         board_type=GatewayBase.RPi)

        self.publisher_topic = publisher_topic

        # create a pigpio instance
        self.rpi = pigpio.pi()
        self.i2c_handle = None

        try:
            self.receive_loop()
        except KeyboardInterrupt:
            self.clean_up()
            sys.exit(0)

    def init_pins_dictionary(self):
        # initialize all gpio pins as digital input pins in the data
        # structure.

        for pin in self.gpio_pins:
            self.pins_dictionary[pin] = [GatewayBase.DIGITAL_INPUT_MODE, 0, False]

    def set_mode(self, pin, mode, payload):
        try:
            pin_record = self.pins_dictionary[pin]
        except KeyError:
            raise KeyError('pin record not found in set_mode')

        if mode == GatewayBase.DIGITAL_INPUT_MODE:
            self.rpi.set_mode(pin, pigpio.INPUT)
            if pin_record[GatewayBase.PULL_UP]:
                self.rpi.set_pull_up_down(pin, pigpio.PUD_UP)
            self.rpi.set_glitch_filter(pin, 400)
            self.rpi.callback(pin, pigpio.EITHER_EDGE,
                              self.rpi_callback)

        elif mode == GatewayBase.DIGITAL_OUTPUT_MODE:
            self.rpi.set_mode(pin, pigpio.OUTPUT)

        elif mode == GatewayBase.PWM_OUTPUT_MODE:
            self.rpi.set_mode(pin, pigpio.OUTPUT)
        elif mode == GatewayBase.I2C_MODE:
            # self.i2c_handle = self.rpi.i2c_open(1, payload['addr'], 0)
            self.i2c_handle = self.rpi.i2c_open(1, payload['addr'])

        else:
            raise RuntimeError('Unsupported mode: ', mode)

    def digital_write(self, pin, value):
        self.rpi.write(pin, value)

    def pwm_write(self, pin, value):
        self.rpi.set_PWM_dutycycle(pin, value)

    def additional_banyan_messages(self, topic, payload):
        print('additional message for rpi: {}  {}'.format(topic, payload))

    def i2c_write(self, addr, mem, buf):
        """
        If i2c mode has been established using
        set_pin_mode_i2c, then this method
        will write the data contained in the buffer
        to the device register address specified in mem,
        for the i2c device that has an i2c address of addr.

        :param addr: i2c device address
        :param mem: i2c device memory location
        :param buf: data or command
        """
        self.rpi.i2c_write_byte_data(self.i2c_handle, mem, buf)

    def i2c_read(self, addr, mem, length):
        """
        If i2c mode has been established using
        set_pin_mode_i2c, then this method will read
        the number of bytes specified in length, from
        the device register specified as mem, for the
        i2c device that has a i2c address of addr.

        :param addr: i2c device address
        :param mem: memory location
        :param length: number of bytes
        """
        data = self.rpi.i2c_read_i2c_block_data(self.i2c_handle, mem, length)
        print('i2c data: ', data)

    def the_i2c_callback(self, data):
        """
        This is a generic callback routine for i2c read.
        You can optionally publish the data as a message
        where applicable.
        :param data:
        """
        print(data)

    def rpi_callback(self, gpio, level, tick):
        print('digital_input_change: pin {}, value {}, tick {}'.format(gpio, level, tick))
        self.publish_payload({'command': 'digital_input_change',
                              'pin': gpio,
                              'value': level}, 'rpi_callback_data')


def rpi_gateway():
    # allow user to bypass the IP address auto-discovery. This is necessary if the component resides on a computer
    # other than the computing running the backplane.

    parser = argparse.ArgumentParser()
    parser.add_argument("-b", dest="back_plane_ip_address", default="None",
                        help="None or IP address used by Back Plane")
    # allow the user to specify a name for the component and have it shown on the console banner.
    # modify the default process name to one you wish to see on the banner.
    # change the default in the derived class to set the name
    parser.add_argument("-m", dest="subscription_list", default="all", help="A list of subscription topics")
    parser.add_argument("-n", dest="process_name", default="EchoClient", help="Set process name in banner")
    parser.add_argument("-p", dest="publisher_port", default='43124',
                        help="Publisher IP port")
    parser.add_argument("-r", dest="publisher_topic", default="from_rpi_gpio", help="Report topic")
    parser.add_argument("-s", dest="subscriber_port", default='43125',
                        help="Subscriber IP port")
    parser.add_argument("-t", dest="loop_time", default=".1", help="Event Loop Timer in seconds")

    args = parser.parse_args()


    if args.subscription_list == "all":
        subscription_list = 'all', 'rpi'
    else:
        subscription_list = args.subscription_list.split(',')
        subscription_list.insert(0, "all")

    kw_options = {
        'publisher_port': args.publisher_port,
        'subscriber_port': args.subscriber_port,
        'process_name': args.process_name,
        'loop_time': float(args.loop_time),
        # 'subscription_list': subscription_list,
        'publisher_topic': args.publisher_topic
    }

    if args.back_plane_ip_address != 'None':
        kw_options['back_plane_ip_address'] = args.back_plane_ip_address

    # replace with the name of your class
    app = RPiGateway(*subscription_list, **kw_options)

    # signal handler function called when Control-C occurs
    # noinspection PyShadowingNames,PyUnusedLocal,PyUnusedLocal
    def signal_handler(signal, frame):
        print("Control-C detected. See you soon.")
        app.clean_up()
        sys.exit(0)

    # listen for SIGINT
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


if __name__ == '__main__':
    # replace with name of function you defined above
    rpi_gateway()
