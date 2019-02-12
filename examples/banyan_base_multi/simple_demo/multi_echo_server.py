"""
multi_echo_server.py

 Copyright (c) 2016-2019 Alan Yorinks All right reserved.

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

from python_banyan.banyan_base_multi import BanyanBaseMulti


class MultiEchoServer(BanyanBaseMulti):
    """
    This class is a simple Banyan echo server

    """

    def __init__(self, ):

        # initialize the parent
        super(MultiEchoServer, self).__init__(back_plane_csv_file='spec.csv', process_name='MultiDriver')

        # find the sockets in the table for the 2 backplanes
        # socket a is to reply to messages from the client
        self.socket_a = self.find_socket("BP1", self.PUB_SOCK)

        # socket b is to send the notification messages
        self.socket_b = self.find_socket("BP2", self.PUB_SOCK)

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
        if topic == 'echo':
            self.publish_payload(payload, self.socket_a, 'reply')
            print('Message number:', payload['message_number'])
            if payload['message_number'] == 0:
                self.publish_payload({'message': 'got it', 'id': 'b'},
                                    self.socket_b, 'notice')


def multi_echo_server():
    MultiEchoServer()


if __name__ == '__main__':
    multi_echo_server()
