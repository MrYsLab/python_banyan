from python_banyan.banyan_base import BanyanBase


class Bsub(BanyanBase):
    """
    This class will receive any MQTT messages intercepted by MqttGateway
    """

    def __init__(self):
        """
        This is constructor for the Bpub class

        """

        # initialize the base class
        super(Bsub, self).__init__(process_name='Bsub')

        # subscribe to receive MQTT messages processed
        # by the MqttGateway
        self.set_subscriber_topic('from_mqtt')

        # start the receive_loop
        self.receive_loop()

    def incoming_message_processing(self, topic, payload):
        print(topic, payload)


b = Bsub()
