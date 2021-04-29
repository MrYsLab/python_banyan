# The Python Banyan Framework
![](https://github.com/MrYsLab/python_banyan/blob/master/images/BanyanTree.png)


The Python Banyan Framework is a lightweight, reactive framework used to
create flexible, non-blocking, event driven, asynchronous applications.

Python Banyan comes with [full documentation](https://mryslab.github.io/python_banyan/#)
 that includes a [User's Guide](https://mryslab.github.io/python_banyan/#users_guide/) 
 with hands-on examples, as well documentation for the
 [OneGPIO Project](https://mryslab.github.io/python_banyan/#gpio_intro/) 
 that allows you to quickly and easily build reusable GPIO projects for the
 Arduino, ESP-8266, and Raspberry Pi.

Base class API's may be viewed [here.](https://htmlpreview.github.io/?https://github.com/MrYsLab/python_banyan/blob/master/html/python_banyan/index.html)


It is being used by [Palace Games](https://www.raspberrypi.org/blog/raspberry-pi-escape-room/)
to concurrently monitor hundreds of real-time sensors and actuators.

* Based on a network connected Publish/Subscribe model,  Banyan components publish 
user defined protocol messages in the form of Python dictionaries.
* A Banyan protocol message may contain Numpy data.
* Applications may reside on a single computer or be distributed across 
multiple computers without having to change source code.
* Compatible Banyan Frameworks are available for [JavaScript](https://github.com/MrYsLab/js-banyan), [Ruby](https://github.com/MrYsLab/rb_banyan), and
[Java](https://github.com/MrYsLab/javabanyan). Components written in any of these languages can interact with components of a differing language without modification.
* Runs on Python 2 or Python 3 (recommended).


To install,  view the full [installation instructions.](https://mryslab.github.io/python_banyan/install/#installing-python-banyan_1)

A Simple Banyan Echo Server:

```
import sys
from python_banyan.banyan_base import BanyanBase


class EchoServer(BanyanBase):
    """
    This class is a simple Banyan echo server
    """
    def __init__(self, ):

        # initialize the parent
        super(EchoServer, self).__init__(process_name='EchoServer')

        # subscribe to receive 'echo' messages from the client
        self.set_subscriber_topic('echo')

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
        """
        # republish the message with a topic of reply
        self.publish_payload(payload, 'reply')
        
        # extract the message number from the payload
        print('Message number:', payload['message_number'])

```

A Simple Banyan Echo Client:

```
import sys
from python_banyan.banyan_base import BanyanBase


class EchoClient(BanyanBase):
    """
    This is a simple echo client derived from the BanyanBase class. 
    It sends out a series of messages and expects an
    echo reply from the server.
    """

    def __init__(self):

        # initialize the parent
        super(EchoClient, self).__init__(process_name='EchoClient')

        # accept banyan messages with the topic of reply
        self.set_subscriber_topic('reply')

        # sequence number of messages and total number of messages to send
        self.message_number = self.number_of_messages = 10

        # send the first message - make sure that the server is already started
        self.publish_payload({'message_number': self.message_number}, 'echo')

        # get the reply messages
        try:
            self.receive_loop()
        except KeyboardInterrupt:
            self.clean_up()
            sys.exit(0)

    def incoming_message_processing(self, topic, payload):
        """
        Process incoming messages received from the echo client
        :param topic: Message Topic string
        :param payload: Message Data
        """

        # When a message is received and its number is zero, finish up.
        if payload['message_number'] == 0:
            print(str(self.number_of_messages) + ' messages sent and received. ')
            input('Press enter to exit.')
            self.clean_up()
            sys.exit(0)
        # bump the message number and send the message out
        else:
            self.message_number -= 1
            if self.message_number >= 0:
                self.publish_payload({'message_number': self.message_number}, 'echo')


```

This project was developed with [Pycharm](https://www.jetbrains.com/pycharm/) ![logo](https://github.com/MrYsLab/python_banyan/blob/master/images/icon_PyCharm.png)
