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
        s.connect(('8.8.8.8', 0))
        self.ip_address = s.getsockname()[0]

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
