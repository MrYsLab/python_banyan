import socket
import subprocess
from subprocess import Popen
import psutil
from python_banyan.banyan_base import BanyanBase


class TestBanyanBase(object):

    # no backplane is running yet
    def test_init_no_backplane(self):
        try:
            BanyanBase()
        except RuntimeError:
            assert True

    def test___init__no_params(self):
        # if  backplane is not running, start one for all the tests
        for pid in psutil.pids():
            p = psutil.Process(pid)
            if p.name() == "backplane":
                break
            else:
                self.proc = Popen(['backplane'],
                                  stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                                  stdout=subprocess.PIPE)
                break

        b = BanyanBase()
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # use the google dns
        try:
            s.connect(('8.8.8.8', 1))
            back_plane_ip_address = s.getsockname()[0]
        except:
            back_plane_ip_address = '127.0.0.1'
        finally:
            s.close()

        b.clean_up()
        assert b.back_plane_ip_address == back_plane_ip_address

    def test___init__specify_backplane_address(self):
        b = BanyanBase('111.222.333.444')
        b.clean_up()
        assert b.back_plane_ip_address == '111.222.333.444'

    def test_set_subscriber_topic_valid(self):
        b = BanyanBase()
        try:
            b.set_subscriber_topic('a_topic')
            b.clean_up()
            assert True
        except TypeError:
            b.clean_up()
            assert False

    def test_set_subscriber_topic_invalid(self):
        b = BanyanBase()
        try:
            b.set_subscriber_topic(8)
            assert False
        except TypeError:
            b.clean_up()
            assert True

    def test_publish_payload_invalid_topic(self):
        b = BanyanBase()
        try:
            b.publish_payload({'payload': 1}, ['b'])
            b.clean_up()
            assert False
        except TypeError:
            b.clean_up()
            assert True

    def test_publish_payload_valid_topic(self):
        b = BanyanBase()
        try:
            b.publish_payload({'payload': 1}, 'b')
            b.clean_up()
            assert True
        except TypeError:
            b.clean_up()
            assert False

    def test_numpy_publish_payload_invalid_topic(self):
        b = BanyanBase(numpy=True)
        try:
            b.publish_payload({'payload': 1}, ['b'])
            b.clean_up()
            assert False
        except TypeError:
            b.clean_up()
            assert True

    def test_numpy_publish_payload_valid_topic(self):
        b = BanyanBase(numpy=True)
        try:
            b.publish_payload({'payload': 1}, 'b')
            b.clean_up()
            assert True
        except TypeError:
            b.clean_up()
            assert False

    def test_incoming_message_processing(self):
        b = BanyanBase()
        b.incoming_message_processing({'payload': 1}, 'the_topic')
        b.clean_up()
        assert True

    def test_clean_up(self):
        b = BanyanBase()
        b.clean_up()
        assert True
