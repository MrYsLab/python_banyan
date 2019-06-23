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
import socket

import paho.mqtt.client as mqtt
import umsgpack


class MQSUB(mqtt.Client):
    """
    This class subscribes to the "test" topic, and sits in a loop
    receiving messages. When 100000 messages have been received,
    it shuts down the loop and prints both the elapsed time taken
    to receive all messages as well as the current time.
    """

    def __init__(self):
        """
        Start the client, subscribe to "test" and start the loop
        """
        super(MQSUB, self).__init__()
        # super().on_connect = self.on_connect
        # super().on_message = self.on_message

        self.start = 0
        self.end = 0
        self.message_count = 0

        # determine current IP address of the local computer
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # use the google dns
        try:
            s.connect(('8.8.8.8', 1))
            self.ip_address = s.getsockname()[0]
        except:
            self.ip_address = '127.0.0.1'
        finally:
            s.close()

        self.connect(self.ip_address, 1883, 60)
        self.subscribe("test", 0)

        self.loop_forever()

    def on_connect(self, mqttc, obj, flags, rc):
        """
        Let the user know we are connected
        :param mqttc: unused
        :param obj: unused
        :param flags: unused
        :param rc: unused
        :return: unused
        """
        print('MQSUB Connected - Expecting 100000 Messages')

    def on_message(self, mqttc, obj, msg):
        """

        :param mqttc: the client
        :param obj: unused
        :param msg: the message containing the payload
        :return:
        """
        # unpack the messagepack message
        if msg.topic == 'test':
            mg = umsgpack.unpackb(msg.payload)
            data = mg['msg']

            # update the count of messages received and start the
            # elapsed time timer
            self.message_count += 1
            if data == 0:
                self.start = time.time()

            # wait for the last message, then print out the current time
            # and an elapsed time message.
            # finally stop the loop and exit.
            if data == 99999:
                self.end = time.time()
                localtime = time.asctime(time.localtime(time.time()))

                print('Task completed on: ', localtime)
                print('{} Total messages received in {} seconds.'.format(self.message_count,
                                                                         self.end - self.start))
                time.sleep(1)
                self.loop_stop()
                sys.exit(0)
        else:
            print('unknown topic' + msg.topic)


MQSUB()
