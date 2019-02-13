"""
 Copyright (c) 2016-2019 Alan Yorinks All right reserved.

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

import sys

import pigpio

from python_banyan.banyan_base import BanyanBase


class Single(BanyanBase):
    """
    This class will monitor a push button connected to a
    Raspberry Pi. When the button is pressed, an LED will light,
    and message will be published with changed state of the input pin.
    """

    def __init__(self, push_button=11, led=4, publish_topic='button'):
        """
        This method initialize the class for operation
        :param push_button: push_button pin
        :param led: led pin
        :param publish_topic: publishing topic
        """

        # initialize the parent
        super(Single, self).__init__(process_name='Single')

        # make the input parameters available to the entire class
        self.push_button = push_button
        self.led = led
        self.publish_topic = publish_topic

        # initialize the GPIO pins using pigpio
        self.pi = pigpio.pi()
        self.pi.set_mode(self.push_button, pigpio.INPUT)
        self.pi.set_pull_up_down(self.push_button, pigpio.PUD_DOWN)
        self.pi.set_mode(led, pigpio.OUTPUT)

        # set a glitch filter to debounce the switch
        self.pi.set_glitch_filter(push_button, 100)

        # set a callback for when the button is pressed
        self.pi.callback(self.push_button, pigpio.EITHER_EDGE,
                         self.button_callback)

        # this will keep the program running forever
        try:
            self.receive_loop()
        except KeyboardInterrupt:
            sys.exit(0)

    def button_callback(self, gpio, level, tick):
        """
        This method receives a change in state of the
        pushbutton.

        It will print the current state to the console
        and reflect that state by turning the LED on
        or OFF based on the state.

        It will also publish a message containing the state
        change.

        :param gpio: pin number
        :param level: pin level
        :param tick: timer tick
        """
        print('The pushbutton state is {} on pin {} '
              'and changed at tick {}'.format(level, gpio, tick))

        self.pi.write(self.led, level)

        # create a publishing payload
        payload = {'pushbutton state': level, 'gpio_pin': gpio,
                   'time_tick':tick}
        self.publish_payload(payload, self.publish_topic)


Single()
