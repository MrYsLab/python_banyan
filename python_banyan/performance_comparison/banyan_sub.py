"""
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
from python_banyan.banyan_base import BanyanBase


class BanyanSub(BanyanBase):
    """
    This class subscribes to the "test" topic, and sits in a loop
    receiving messages. When 100000 messages have been received,
    it shuts down the loop and prints both the elapsed time taken
    to receive all messages as well as the current time.
    """
    def __init__(self):
        """
        Subscribe to the "test" topic, initialize the message count
        and enter the receive loop.
        """
        super(BanyanSub, self).__init__(process_name='Banyan Subscriber')
        # allow time for connections to be established
        time.sleep(.3)

        # the start time
        self.start = None

        # the end time
        self.end = None

        print('Expecting 100000 messages.')
        self.set_subscriber_topic('test')
        self.message_count = 0
        self.receive_loop()

    def incoming_message_processing(self, topic, payload):
        """
        When a message is received, extract the message number, bump the
        message count by 1.

        On the first message, start the elapsed time timer.

        On the last message determine the elapsed time, and print it
        and the current time. Finally exit
        :param topic: Message Topic string
        :param payload: Message Data
        :return:
        """
        data = payload['msg']
        self.message_count += 1

        if data == 0:
            self.start = time.time()

        if data == 99999:
            self.end = time.time()
            localtime = time.asctime(time.localtime(time.time()))
            print('Task completed at: ', localtime)
            print('{} Total messages received in {} seconds.'.format(self.message_count, self.end - self.start))
            super(BanyanSub, self).clean_up()
            sys.exit(0)

BanyanSub()
