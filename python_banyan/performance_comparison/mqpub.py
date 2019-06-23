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

import paho.mqtt.client as mqtt
import socket
import sys
import time
import umsgpack


class MQPUB(mqtt.Client):
    """
        This class publishes 100000 "test" topic messages as fast as it can.
        It then prints the current time and exits.
        """

    def __init__(self):
        """
        This method connects, starts the loop and then publishes
        all the messages until complete.

        It then prints the current time before stopping the loop and exiting.
        """
        super(MQPUB, self).__init__()

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
        print("MQPUB Connected - Sending 100000 messages")

        time.sleep(2)

        for x in range(0, 100000):
            payload = {'msg': x}
            packed = umsgpack.packb(payload)
            self.publish("test", packed)

        localtime = time.asctime(time.localtime(time.time()))

        print('Task completed on: ', localtime)
        time.sleep(1)
        self.loop_stop()
        sys.exit(0)


# instantiate the class
MQPUB()
