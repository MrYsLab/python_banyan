import sys
import time
from python_banyan.banyan_base import BanyanBase


class BanyanPub(BanyanBase):
    """
    This class publishes 100000 "test" topic messages as fast as it can.
    It then prints the current time and exits.
    """

    def __init__(self):
        super(BanyanPub, self).__init__(back_plane_ip_address='192.168.2.192', process_name='Banyan publisher')

        print('Publishing 100000 messages.')
        time.sleep(.3)

        for x in range(0, 100000):
            payload = {'msg': x}
            self.publish_payload(payload, 'test')

        localtime = time.asctime(time.localtime(time.time()))

        print('Task completed at: ', localtime)

        super(BanyanPub, self).clean_up()
        sys.exit(0)

# instantiate this class
BanyanPub()



