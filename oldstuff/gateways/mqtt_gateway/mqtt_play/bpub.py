from python_banyan.banyan_base import BanyanBase


class Bpub(BanyanBase):
    """
    This class will publish a message for the MqttGateway to forward to the MQTT network.
    """

    def __init__(self):
        """
        This is constructor for the Bpub class

        """

        # initialize the base class
        super(Bpub, self).__init__(process_name='Bpub')

        # send a message to the MqttGateway
        self.publish_payload({'from_banyan': 'hello_mqtt_world'}, 'to_mqtt')

        # exit
        self.clean_up()


b = Bpub()
