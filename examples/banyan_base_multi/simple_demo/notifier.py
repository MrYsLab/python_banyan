"""
notifier.py

 Copyright (c) 2018 - 2019 Alan Yorinks All right reserved.

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
import sys
import time

from python_banyan.banyan_base import BanyanBase


class Notifier(BanyanBase):
    """
    This class is a simple Banyan echo server

    """

    def __init__(self, ):

        # initialize the parent
        super(Notifier, self).__init__(process_name='Notifier')

        # subscribe to receive 'echo' messages from the client
        self.set_subscriber_topic('notice')

        # wait for messages to arrive
        try:
            self.receive_loop()
        except KeyboardInterrupt:
            self.clean_up()
            sys.exit(0)

    def incoming_message_processing(self, topic, payload):
        """
        Process incoming messages from the client
        :param topic: message topic
        :param payload: message payload
        :return:
        """
        print('Notification Received!')


def notifier():
    Notifier()


if __name__ == '__main__':
    notifier()
