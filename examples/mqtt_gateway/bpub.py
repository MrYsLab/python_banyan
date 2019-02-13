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


class Bpub(BanyanBase):
    """
    This class will publish a message for the MqttGateway to forward to the MQTT network.
    """

    def __init__(self):
        """
        This is constructor for the Bpub class

        """

        # initialize the base class
        super(Bpub, self).__init__(process_name='Bpub')

        # send a message to the MqttGateway
        self.publish_payload({'from_banyan': 'hello_mqtt_world'}, 'to_mqtt')

        # exit
        self.clean_up()


b = Bpub()
