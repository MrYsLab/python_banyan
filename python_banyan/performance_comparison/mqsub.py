import sys
import time

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

        self.connect('192.168.2.192', 1883, 60)
        self.subscribe("test", 0)
        self.subscribe("m2", 0)


        self.loop_forever()

    def on_connect(self, mqttc, obj, flags, rc):
        """
        Let the use know we are connected
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
        elif msg.topic == 'm2':
            mg = umsgpack.unpackb(msg.payload)
            if mg['modulo'] == 45000:
                print(msg.payload)
        else:
            print('unkown topic' + msg.topic)


MQSUB()
