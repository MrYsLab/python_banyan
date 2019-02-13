"""
 Copyright (c) 2019 Alan Yorinks All right reserved.

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

from python_banyan.banyan_base import BanyanBase


class Bsub(BanyanBase):
    """
    This class will receive any MQTT messages intercepted by MqttGateway
    """

    def __init__(self):
        """
        This is constructor for the Bpub class

        """

        # initialize the base class
        super(Bsub, self).__init__(process_name='Bsub')

        # subscribe to receive MQTT messages processed
        # by the MqttGateway
        self.set_subscriber_topic('from_mqtt')

        # start the receive_loop
        self.receive_loop()

    def incoming_message_processing(self, topic, payload):
        print(topic, payload)


b = Bsub()
