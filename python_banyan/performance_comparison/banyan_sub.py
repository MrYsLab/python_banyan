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

        # time.sleep(.001)
        # if not self.message_count % 100:
        #     print(self.message_count)

        if data == 0:
            self.start = time.time()

        if data == 99999:
            self.end = time.time()
            localtime = time.asctime(time.localtime(time.time()))
            print('Task completed at: ', localtime)
            print('{} Total messages received in {} seconds.'.format(self.message_count, self.end - self.start))
            super(BanyanSub, self).clean_up()
            sys.exit(0)

# instantiate this class
BanyanSub()
