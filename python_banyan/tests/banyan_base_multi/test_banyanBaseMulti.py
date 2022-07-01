
from python_banyan.banyan_base_multi import BanyanBaseMulti

import pytest
import subprocess
from subprocess import Popen
import psutil
import zmq
import os


class TestBanyanBaseMulti(object):
    spec_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_specs/')

    def test___init__no_params(self):
        with pytest.raises(ValueError):
            b = BanyanBaseMulti()

    def test___init__duplicate_backplane_name(self):
        with pytest.raises(RuntimeError):
            b = BanyanBaseMulti(self.spec_path + 'sample_duplicate_backplane_name.csv',
                                process_name='test___init__duplicate_backplane_name')

    def test___init__invalid_csv_file_name(self):
        with pytest.raises(ValueError):
            b = BanyanBaseMulti('abc.csv', process_name='test___init__invalid_csv_file_name')

    def test___init__missing_left_bracket_csv_file(self):
        with pytest.raises(RuntimeError):
            b = BanyanBaseMulti(self.spec_path + 'sample_missing_left_bracket.csv')

    def test___init__sample_missing_right_bracket_csv_file(self):
        with pytest.raises(RuntimeError):
            b = BanyanBaseMulti(self.spec_path + 'sample_missing_right_bracket.csv')

    def test___init__csv_with_space(self):
        with pytest.raises(RuntimeError):
            # b = BanyanBaseMulti('sample_with_space.csv')
            b = BanyanBaseMulti(self.spec_path + 'sample_with_space.csv' )

    def test___init__valid_csv_file(self):
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
        b = BanyanBaseMulti(self.spec_path + 'sample.csv')
        assert True

    def test_find_socket_invalid_backplane(self):
        b = BanyanBaseMulti(self.spec_path + 'sample.csv')
        with pytest.raises(StopIteration):
            b.find_socket('invalid_name', b.PUB_SOCK)

    def test_find_socket_invalid_socket_type(self):
        b = BanyanBaseMulti(self.spec_path + 'sample.csv')
        with pytest.raises(ValueError):
            b.find_socket('Motors', 'george')

    def test_find_socket_no_pub_socket(self):
        b = BanyanBaseMulti(self.spec_path + 'sample.csv')
        socket = b.find_socket('Motors', b.PUB_SOCK)
        assert socket == None

    def test_find_socket_no_sub_socket(self):
        b = BanyanBaseMulti(self.spec_path + 'sample.csv')
        socket = b.find_socket('Sensors', b.SUB_SOCK)
        assert socket == None

    def test_find_socket_found_sub_socket(self):
        b = BanyanBaseMulti(self.spec_path + 'sample.csv')
        socket = b.find_socket('Motors', b.SUB_SOCK)
        assert socket != None

    def test_find_socket_found_pub_socket(self):
        b = BanyanBaseMulti(self.spec_path + 'sample.csv')
        # with pytest.raises(ValueError):
        socket = b.find_socket('Sensors', b.PUB_SOCK)
        assert socket != None

    def test_set_subscriber_topic_invalid_topic(self):
        b = BanyanBaseMulti(self.spec_path + 'sample.csv')
        with pytest.raises(TypeError):
            b.set_subscriber_topic(5, 5)

    def test_set_subscriber_topic_invalid_socket(self):
        b = BanyanBaseMulti(self.spec_path + 'sample.csv')
        with pytest.raises(ValueError):
            b.set_subscriber_topic('Hello', None)

    def test_set_subscriber_topic_valid(self):
        context = zmq.Context()
        subscriber = context.socket(zmq.SUB)
        b = BanyanBaseMulti(self.spec_path + 'sample.csv')
        b.set_subscriber_topic('Hello', subscriber)
        assert True

    def test_unsubscribe_topic_invalid_topic(self):
        b = BanyanBaseMulti(self.spec_path + 'sample.csv')
        with pytest.raises(TypeError):
            b.unsubscribe_topic(5, 5)

    def test_unsubscribe_topic_invalid_socket(self):
        b = BanyanBaseMulti(self.spec_path + 'sample.csv')
        with pytest.raises(ValueError):
            b.unsubscribe_topic('Hello', None)

    def test_unsubscribe_topic_valid(self):
        context = zmq.Context()
        subscriber = context.socket(zmq.SUB)
        b = BanyanBaseMulti(self.spec_path + 'sample.csv')
        b.set_subscriber_topic('Hello', subscriber)
        b.unsubscribe_topic('Hello', subscriber)
        assert True

    def test_publish_payload_numpy(self):
        context = zmq.Context()
        subscriber = context.socket(zmq.SUB)
        b = BanyanBaseMulti(back_plane_csv_file=self.spec_path + 'sample.csv', numpy=True)
        b.publish_payload('the_topic_payload', 'BROADCAST', 'the_topic')
        assert True

    def test_publish_payload_invalid_topic(self):
        b = BanyanBaseMulti(self.spec_path + 'sample.csv')
        with pytest.raises(TypeError):
            b.publish_payload(5, 3, 5)

    def test_publish_payload_invalid_socket(self):
        b = BanyanBaseMulti(self.spec_path + 'sample.csv')
        with pytest.raises(ValueError):
            b.publish_payload('the_topic_payload', None, 'the_topic')

    def test_publish_payload_specific_socket(self):
        b = BanyanBaseMulti(self.spec_path + 'sample.csv')
        socket = b.find_socket('LEDS', b.PUB_SOCK)
        b.publish_payload('the_topic_payload', socket, 'the_topic')
        assert True

    def test_incoming_message_processing_test(self):
        context = zmq.Context()
        b = BanyanBaseMulti(back_plane_csv_file=self.spec_path + 'sample.csv')
        b.incoming_message_processing({'payload': 3}, 'the_topic')
        assert True

    def test_clean_up(self):
        context = zmq.Context()
        b = BanyanBaseMulti(back_plane_csv_file=self.spec_path + 'sample.csv')
        b.clean_up()
        assert True


