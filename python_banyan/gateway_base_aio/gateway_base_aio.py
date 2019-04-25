#!/usr/bin/env python3

"""
gateway_base_aio.py

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

import asyncio
from python_banyan.banyan_base_aio import BanyanBaseAIO


class GatewayBaseAIO(BanyanBaseAIO):
    """
    This class provides a common front end abstraction for all asyncio hardware gateways.
    """

    # pin modes
    DIGITAL_INPUT_MODE = 0
    DIGITAL_OUTPUT_MODE = 1
    PWM_OUTPUT_MODE = 2
    ANALOG_INPUT_MODE = 3
    ANALOG_OUTPUT_MODE = 4
    DIGITAL_INPUT_PULLUP_MODE = 5
    I2C_MODE = 6
    TONE_MODE = 7
    SERVO_MODE = 8
    STEPPER_MODE = 9
    SONAR_MODE = 10
    WILD_CARD_MODE = 11

    # index into pin database record
    PIN_MODE = 0
    LAST_VALUE = 1
    PULL_UP = 2

    # noinspection PyDefaultArgument,PyRedundantParentheses
    def __init__(self, back_plane_ip_address=None, subscriber_port='43125',
                 publisher_port='43124', process_name='',
                 subscriber_list=None, board_type=None, event_loop=None,):
        """

        :param back_plane_ip_address: banyan_base back_planeIP Address -
               if not specified, it will be set to the local computer
        :param subscriber_port: banyan_base back plane subscriber port.
               This must match that of the banyan_base backplane
        :param publisher_port: banyan_base back plane publisher port.
                               This must match that of the banyan_base
                               backplane
        :param process_name: Component identifier
        :param subscriber_list: a tuple or list of topics to be subscribed to
        :param board_type: micro-controller type ID
        :param event_loop: event loop that user may specify

        """
        if board_type:
            self.board_type = board_type

        # set up the event loop
        if event_loop:
            self.event_loop = event_loop
        else:
            self.event_loop = asyncio.get_event_loop()

        if subscriber_list:
            self.subscriber_list = subscriber_list
        else:
            self.subscriber_list = ('all')

        # dictionaries for pin modes set by user
        # an entry consists of a pin number key
        # with a value of a list containing 3 values:
        #   1. the current pin mode
        #   2. the last reported value for this pin (for input modes only)
        #   3. a flag to state if pull up was enabled (for digital input only)

        # this dictionary initially contains an entry for each default
        # digital input pin

        self.pins_dictionary = {}

        # a pin can optionally be give a tag, it is used as a key to find pin number
        # tag(string): pin(integer)
        self.tags_dictionary = {}

        self.init_pins_dictionary()

        # for arduinos - save the pin number of the first analog pin
        self.first_analog_pin = 0

        # subscribe to initial topics
        # for topic in subscription_topics:
        #     await self.set_subscriber_topic(topic)
        # initialize the parent
        super(GatewayBaseAIO, self).__init__(back_plane_ip_address=back_plane_ip_address,
                                             subscriber_port=subscriber_port,
                                             publisher_port=publisher_port,
                                             process_name=process_name,
                                             subscriber_list=self.subscriber_list,
                                             event_loop=self.event_loop)

        self.command_dictionary = {'analog_write': self.analog_write,
                                   'digital_write': self.digital_write,
                                   'disable_analog_reporting': self.disable_analog_reporting,
                                   'disable_digital_reporting': self.disable_digital_reporting,
                                   'enable_analog_reporting': self.disable_analog_reporting,
                                   'enable_digital_reporting': self.disable_digital_reporting,
                                   'i2c_read': self.i2c_read,
                                   'i2c_write': self.i2c_write,
                                   'play_tone': self.play_tone,
                                   'pwm_write': self.pwm_write,
                                   'servo_position': self.servo_position,
                                   'set_mode_analog_input': self.set_mode_analog_input,
                                   'set_mode_digital_input': self.set_mode_digital_input,
                                   'set_mode_digital_input_pullup': self.set_mode_digital_input_pullup,
                                   'set_mode_digital_output': self.set_mode_digital_output,
                                   'set_mode_i2c': self.set_mode_i2c,
                                   'set_mode_pwm': self.set_mode_pwm,
                                   'set_mode_servo': self.set_mode_servo,
                                   'set_mode_sonar': self.set_mode_sonar,
                                   'set_mode_stepper': self.set_mode_stepper,
                                   'set_mode_tone': self.set_mode_tone,
                                   'stepper_write': self.stepper_write,
                                   }

    def init_pins_dictionary(self):
        """
        This method will initialize the pins dictionary
        This is handled within the class for each hardware type
        """
        raise NotImplementedError

    async def incoming_message_processing(self, topic, payload):
        """
        Messages are sent here from the receive_loop
        :param topic: Message Topic string
        :param payload: Message Data
        :return:
        """
        # process payload command
        try:
            command = payload['command']
        except KeyError:
            print(payload)
            raise

        # pin = None
        # tag = ''

        # if a tag is provided and the tag is in the dictionary, fetch
        # the associated pin number
        if 'tag' in payload:
            tag = payload['tag']
            if tag:
                if tag in self.tags_dictionary:
                    pin = self.tags_dictionary[tag]
                    # the pin is optional if using tag, so add it to the payload
                    payload['pin'] = pin
                else:
                    self.tags_dictionary[payload['tag']] = payload['pin']

        # if command is in the command dictionary, execute the command
        if command in self.command_dictionary.keys():
            await self.command_dictionary[command](topic, payload)

        # for unknown requests, pass them along to the hardware gateway to handle
        else:
            await self.additional_banyan_messages(topic, payload)

    # all of the following methods should be overridden in the hardware
    # specific gateway when being used.

    async def additional_banyan_messages(self, topic, payload):
        """
        This method will pass any messages not handled by this class to the
        specific gateway class. Must be overwritten by the hardware gateway class.
        :param topic: message topic
        :param payload: message payload
        """
        raise NotImplementedError

    async def analog_write(self, topic, payload):
        """
        This method will pass any messages not handled by this class to the
        specific gateway class. Must be overwritten by the hardware gateway class.
        :param topic: message topic
        :param payload: message payload
        """
        raise NotImplementedError

    async def digital_write(self, topic, payload):
        """
        This method will pass any messages not handled by this class to the
        specific gateway class. Must be overwritten by the hardware gateway class.
        :param topic: message topic
        :param payload: message payload
        """
        raise NotImplementedError

    async def disable_analog_reporting(self, topic, payload):
        """
        This method will pass any messages not handled by this class to the
        specific gateway class. Must be overwritten by the hardware gateway class.
        :param topic: message topic
        :param payload: message payload
        """
        raise NotImplementedError

    async def disable_digital_reporting(self, topic, payload):
        """
        This method will pass any messages not handled by this class to the
        specific gateway class. Must be overwritten by the hardware gateway class.
        :param topic: message topic
        :param payload: message payload
        """
        raise NotImplementedError

    async def enable_analog_reporting(self, topic, payload):
        """
        This method will pass any messages not handled by this class to the
        specific gateway class. Must be overwritten by the hardware gateway class.
        :param topic: message topic
        :param payload: message payload
        """
        raise NotImplementedError

    async def enable_digital_reporting(self, topic, payload):
        """
        This method will pass any messages not handled by this class to the
        specific gateway class. Must be overwritten by the hardware gateway class.
        :param topic: message topic
        :param payload: message payload
        """
        raise NotImplementedError

    async def i2c_read(self, topic, payload):
        """
        This method will pass any messages not handled by this class to the
        specific gateway class. Must be overwritten by the hardware gateway class.
        :param topic: message topic
        :param payload: message payload
        """
        raise NotImplementedError

    async def i2c_write(self, topic, payload):
        """
        This method will pass any messages not handled by this class to the
        specific gateway class. Must be overwritten by the hardware gateway class.
        :param topic: message topic
        :param payload: message payload
        """
        raise NotImplementedError

    async def play_tone(self, topic, payload):
        """
        This method will pass any messages not handled by this class to the
        specific gateway class. Must be overwritten by the hardware gateway class.
        :param topic: message topic
        :param payload: message payload
        """
        raise NotImplementedError

    async def pwm_write(self, topic, payload):
        """
        This method will pass any messages not handled by this class to the
        specific gateway class. Must be overwritten by the hardware gateway class.
        :param topic: message topic
        :param payload: message payload
        """
        raise NotImplementedError

    async def servo_position(self, topic, payload):
        """
        This method will pass any messages not handled by this class to the
        specific gateway class. Must be overwritten by the hardware gateway class.
        :param topic: message topic
        :param payload: message payload
        """
        raise NotImplementedError

    async def set_mode_analog_input(self, topic, payload):
        """
        This method will pass any messages not handled by this class to the
        specific gateway class. Must be overwritten by the hardware gateway class.
        :param topic: message topic
        :param payload: message payload
        """
        raise NotImplementedError

    async def set_mode_digital_input(self, topic, payload):
        """
        This method will pass any messages not handled by this class to the
        specific gateway class. Must be overwritten by the hardware gateway class.
        :param topic: message topic
        :param payload: message payload
        """
        raise NotImplementedError

    async def set_mode_digital_input_pullup(self, topic, payload):
        """
        This method will pass any messages not handled by this class to the
        specific gateway class. Must be overwritten by the hardware gateway class.
        :param topic: message topic
        :param payload: message payload
        """
        raise NotImplementedError

    async def set_mode_digital_output(self, topic, payload):
        """
        This method will pass any messages not handled by this class to the
        specific gateway class. Must be overwritten by the hardware gateway class.
        :param topic: message topic
        :param payload: message payload
        """
        raise NotImplementedError

    async def set_mode_i2c(self, topic, payload):
        """
        This method will pass any messages not handled by this class to the
        specific gateway class. Must be overwritten by the hardware gateway class.
        :param topic: message topic
        :param payload: message payload
        """
        raise NotImplementedError

    async def set_mode_pwm(self, topic, payload):
        """
        This method will pass any messages not handled by this class to the
        specific gateway class. Must be overwritten by the hardware gateway class.
        :param topic: message topic
        :param payload: message payload
        """
        raise NotImplementedError

    async def set_mode_servo(self, topic, payload):
        """
        This method will pass any messages not handled by this class to the
        specific gateway class. Must be overwritten by the hardware gateway class.
        :param topic: message topic
        :param payload: message payload
        """
        raise NotImplementedError

    async def set_mode_sonar(self, topic, payload):
        """
        This method will pass any messages not handled by this class to the
        specific gateway class. Must be overwritten by the hardware gateway class.
        :param topic: message topic
        :param payload: message payload
        """
        raise NotImplementedError

    async def set_mode_stepper(self, topic, payload):
        """
        Set the mode for the specific board.
        Must be overwritten by the hardware gateway class.
        :param topic: message topic
        :param payload: message payload
        """
        raise NotImplementedError

    async def set_mode_tone(self, topic, payload):
        """
        Must be overwritten by the hardware gateway class.
        Handles a digital write
        :param topic: message topic
        :param payload: message payload
        """
        raise NotImplementedError

    async def digital_read(self, pin):
        raise NotImplementedError

    async def stepper_write(self, topic, payload):
        """
        Must be overwritten by the hardware gateway class.
        Handles a pwm write
        :param topic: message topic
        :param payload: message payload
        """
        raise NotImplementedError
