import sys
import socket
import signal
import zmq
import umsgpack
import remi.gui as gui
from remi.gui import *
from remi import start, App


class GuiClock(App):

    # ZeroMQ backplane address
    back_plane_ip_address = None

    #ZeroMQ backplane ports
    subscriber_port = '43125'
    publisher_port = '43124'

    # ip address where the remi server is running
    gui_ip_address = None

    # ZeroMQ connections
    publisher = None
    subscriber = None

    # topics that this application wishes to subscribe to
    subscriber_topics = ['update_seconds', 'update_minutes', 'update_hours']

    # The ZeroMQ context
    context = None


    def __init__(self, *args, **kwargs):
        if not 'editing_mode' in kwargs.keys():
            super(GuiClock, self).__init__(*args, static_file_path='./res/')

    def idle(self):
        # idle function called every update cycle
        data = None

        try:
            data = self.subscriber.recv_multipart(zmq.NOBLOCK)
            self.incoming_message_processing(data[0].decode(), umsgpack.unpackb(data[1]))
        except zmq.error.Again:
            pass
        except KeyboardInterrupt:
            self.clean_up()

    def main(self):
        print('\n************************************************************')
        print('Clock GUI using Back Plane IP address: ' + self.back_plane_ip_address)
        print('GUI IP Address = ' + self.gui_ip_address)
        print('Subscriber Port = ' + self.subscriber_port)
        print('Publisher  Port = ' + self.publisher_port)
        print('************************************************************')

        self.context = zmq.Context()
        # noinspection PyUnresolvedReferences
        self.subscriber = self.context.socket(zmq.SUB)
        for topic in self.subscriber_topics:
            self.subscriber.setsockopt(zmq.SUBSCRIBE, topic.encode())
        #
        connect_string = "tcp://" + GuiClock.back_plane_ip_address + ':' + self.subscriber_port
        self.subscriber.connect(connect_string)
        #
        # noinspection PyUnresolvedReferences
        GuiClock.publisher = self.context.socket(zmq.PUB)
        connect_string = "tcp://" + GuiClock.back_plane_ip_address + ':' + self.publisher_port
        self.publisher.connect(connect_string)
        the_gui = GuiClock.construct_ui(self)
        # alias to help access widgets directly
        GuiClock.the_widgets = self.clock_top_panel.children
        return the_gui

    @staticmethod
    def construct_ui(self):
        clock_top_panel = Widget()
        clock_top_panel.attributes['editor_baseclass'] = "Widget"
        clock_top_panel.attributes['editor_constructor'] = "()"
        clock_top_panel.attributes['editor_tag_type'] = "widget"
        clock_top_panel.attributes['editor_newclass'] = "False"
        clock_top_panel.attributes['editor_varname'] = "clock_top_panel"
        clock_top_panel.attributes['class'] = "Widget"
        clock_top_panel.style['height'] = "386px"
        clock_top_panel.style['font-size'] = "90px"
        clock_top_panel.style['width'] = "919px"
        clock_top_panel.style['margin'] = "0px"
        clock_top_panel.style['top'] = "1px"
        clock_top_panel.style['position'] = "absolute"
        clock_top_panel.style['display'] = "block"
        clock_top_panel.style['left'] = "2px"
        clock_top_panel.style['overflow'] = "visible"
        main_label = Label('Python Banyan Clock')
        main_label.attributes['editor_baseclass'] = "Label"
        main_label.attributes['editor_constructor'] = "('Python Banyan Clock')"
        main_label.attributes['editor_tag_type'] = "widget"
        main_label.attributes['editor_newclass'] = "False"
        main_label.attributes['editor_varname'] = "main_label"
        main_label.attributes['class'] = "Label"
        main_label.style['height'] = "82px"
        main_label.style['font-size'] = "50px"
        main_label.style['width'] = "498px"
        main_label.style['margin'] = "0px"
        main_label.style['top'] = "49px"
        main_label.style['position'] = "absolute"
        main_label.style['display'] = "block"
        main_label.style['left'] = "237px"
        main_label.style['overflow'] = "visible"
        clock_top_panel.append(main_label, 'main_label')
        label_colon2 = Label(':')
        label_colon2.attributes['editor_baseclass'] = "Label"
        label_colon2.attributes['editor_constructor'] = "(':')"
        label_colon2.attributes['editor_tag_type'] = "widget"
        label_colon2.attributes['editor_newclass'] = "False"
        label_colon2.attributes['editor_varname'] = "label_colon2"
        label_colon2.attributes['class'] = "Label"
        label_colon2.style['overflow'] = "visible"
        label_colon2.style['height'] = "30px"
        label_colon2.style['font-size'] = "90px"
        label_colon2.style['margin'] = "0px"
        label_colon2.style['top'] = "174px"
        label_colon2.style['width'] = "100px"
        label_colon2.style['left'] = "545px"
        label_colon2.style['position'] = "absolute"
        label_colon2.style['display'] = "block"
        clock_top_panel.append(label_colon2, 'label_colon2')
        label_minutes = Label('00')
        label_minutes.attributes['editor_baseclass'] = "Label"
        label_minutes.attributes['editor_constructor'] = "('00')"
        label_minutes.attributes['editor_tag_type'] = "widget"
        label_minutes.attributes['editor_newclass'] = "False"
        label_minutes.attributes['editor_varname'] = "label_minutes"
        label_minutes.attributes['class'] = "Label"
        label_minutes.style['overflow'] = "visible"
        label_minutes.style['height'] = "72px"
        label_minutes.style['font-size'] = "90px"
        label_minutes.style['margin'] = "0px"
        label_minutes.style['top'] = "181px"
        label_minutes.style['width'] = "132px"
        label_minutes.style['left'] = "423px"
        label_minutes.style['position'] = "absolute"
        label_minutes.style['display'] = "block"
        clock_top_panel.append(label_minutes, 'label_minutes')
        label_seconds = Label('00')
        label_seconds.attributes['editor_baseclass'] = "Label"
        label_seconds.attributes['editor_constructor'] = "('00')"
        label_seconds.attributes['editor_tag_type'] = "widget"
        label_seconds.attributes['editor_newclass'] = "False"
        label_seconds.attributes['editor_varname'] = "label_seconds"
        label_seconds.attributes['class'] = "Label"
        label_seconds.style['overflow'] = "visible"
        label_seconds.style['height'] = "30px"
        label_seconds.style['font-size'] = "90px"
        label_seconds.style['margin'] = "0px"
        label_seconds.style['top'] = "179px"
        label_seconds.style['width'] = "100px"
        label_seconds.style['left'] = "582px"
        label_seconds.style['position'] = "absolute"
        label_seconds.style['display'] = "block"
        clock_top_panel.append(label_seconds, 'label_seconds')
        label_colon1 = Label(':')
        label_colon1.attributes['editor_baseclass'] = "Label"
        label_colon1.attributes['editor_constructor'] = "(':')"
        label_colon1.attributes['editor_tag_type'] = "widget"
        label_colon1.attributes['editor_newclass'] = "False"
        label_colon1.attributes['editor_varname'] = "label_colon1"
        label_colon1.attributes['class'] = "Label"
        label_colon1.style['overflow'] = "visible"
        label_colon1.style['height'] = "39px"
        label_colon1.style['font-size'] = "90px"
        label_colon1.style['margin'] = "0px"
        label_colon1.style['top'] = "173px"
        label_colon1.style['width'] = "49px"
        label_colon1.style['left'] = "390px"
        label_colon1.style['position'] = "absolute"
        label_colon1.style['display'] = "block"
        clock_top_panel.append(label_colon1, 'label_colon1')
        label_hours = Label('00')
        label_hours.attributes['editor_baseclass'] = "Label"
        label_hours.attributes['editor_constructor'] = "('00')"
        label_hours.attributes['editor_tag_type'] = "widget"
        label_hours.attributes['editor_newclass'] = "False"
        label_hours.attributes['editor_varname'] = "label_hours"
        label_hours.attributes['class'] = "Label"
        label_hours.style['overflow'] = "visible"
        label_hours.style['height'] = "61px"
        label_hours.style['font-size'] = "90px"
        label_hours.style['margin'] = "0px"
        label_hours.style['top'] = "179px"
        label_hours.style['width'] = "99px"
        label_hours.style['left'] = "271px"
        label_hours.style['position'] = "absolute"
        label_hours.style['display'] = "block"
        clock_top_panel.append(label_hours, 'label_hours')
        self.clock_top_panel = clock_top_panel
        return self.clock_top_panel

    def clean_up(self):
        """
        Clean up before exiting - override if additional cleanup is necessary

        :return:
        """
        self.publisher.close()
        self.subscriber.close()
        self.context.term()

    def incoming_message_processing(self, topic, payload):
        """
        :param topic: Message Topic string
        :param payload: Message Data
        :return:
        """
        if topic == 'update_seconds':
            self.the_widgets['label_seconds'].set_text(payload['seconds'])
        elif topic == 'update_minutes':
            self.the_widgets['label_minutes'].set_text(payload['minutes'])
        elif topic == 'update_hours':
            self.the_widgets['label_hours'].set_text(payload['hours'])

    def publish_payload(self, payload, topic=''):
        """
        This method will publish python_banyan payload with the specified topic.

        :param payload: A dictionary of items
        :param topic: A string value
        :return:
        """
        if not type(topic) is str:
            raise TypeError('Publish topic must be python_banyan string', 'topic')

        # create python_banyan message pack payload
        message = umsgpack.packb(payload)

        pub_envelope = topic.encode()
        self.publisher.send_multipart([pub_envelope, message])


def clock_gui():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # use the google dns
    s.connect(('8.8.8.8', 0))
    GuiClock.gui_ip_address = s.getsockname()[0]

    # test if user wants to specify the backplane address
    if len(sys.argv) > 1:
        GuiClock.back_plane_ip_address = sys.argv[1]
    # argument, so just use the local host
    else:
        GuiClock.back_plane_ip_address = s.getsockname()[0]

    # signal handler function called when Control-C occurs
    # noinspection PyShadowingNames,PyUnusedLocal,PyUnusedLocal
    def signal_handler(signal, frame):
        print('Control-C detected. See you soon.')

        sys.exit(0)

    # listen for SIGINT
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    start(GuiClock,  debug=False, address=GuiClock.gui_ip_address, update_interval=.00001)


if __name__ == "__main__":
    clock_gui()
