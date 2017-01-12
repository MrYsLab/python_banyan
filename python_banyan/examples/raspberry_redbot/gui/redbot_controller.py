#!/usr/bin/env python3

"""
Created on January 9 11:39:15 2016

@author: Alan Yorinks
Copyright (c) 2016 Alan Yorinks All right reserved.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public
License as published by the Free Software Foundation; either
version 3 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received python_banyan copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""



import sys
import socket
import signal
import zmq
import umsgpack
import remi.gui as gui
from remi.gui import *
from remi import start, App


class RedBot(App):
    back_plane_ip_address = None
    gui_ip_address = None
    publisher = None
    subscriber = None
    subscriber_port = '43125'
    publisher_port = '43124'
    subscriber_topics = ['left_encoder_tick', 'right_encoder_tick', 'button_state_change', 'right_bumper_state_change',
                         'left_bumper_state_change', 'I2C72', 'I2C83']
    context = None
    default_button_color = '#1d81f1'
    speed = 255
    blink_led = False
    led_state = False
    distance = 0.00
    left_encoder_count = 0
    right_encoder_count = 0
    current_vehicle_direction = 'stop'
    units = 'Centimeters'

    def __init__(self, *args, **kwargs):
        if not 'editing_mode' in kwargs.keys():
            super(RedBot, self).__init__(*args, static_file_path='./res/')

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
        pass

    def main(self):
        print('\n************************************************************')
        print('GUI using Back Plane IP address: ' + self.back_plane_ip_address)
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
        connect_string = "tcp://" + RedBot.back_plane_ip_address + ':' + self.subscriber_port
        self.subscriber.connect(connect_string)
        #
        # noinspection PyUnresolvedReferences
        self.publisher = self.context.socket(zmq.PUB)
        connect_string = "tcp://" + RedBot.back_plane_ip_address + ':' + self.publisher_port
        self.publisher.connect(connect_string)
        the_gui = RedBot.construct_ui(self)
        # alias to help access widgets directly
        self.the_widgets = self.top_frame.children
        self.the_data_panel_widgets = self.top_frame.children['raw_data_panel'].children
        return the_gui

    @staticmethod
    def construct_ui(self):
        top_frame = Widget()
        top_frame.attributes['editor_varname'] = "top_frame"
        top_frame.attributes['editor_constructor'] = "()"
        top_frame.attributes['editor_baseclass'] = "Widget"
        top_frame.attributes['editor_tag_type'] = "widget"
        top_frame.attributes['editor_newclass'] = "False"
        top_frame.attributes['class'] = "Widget"
        top_frame.style['display'] = "block"
        top_frame.style['left'] = "1px"
        top_frame.style['top'] = "1px"
        top_frame.style['background-color'] = "#ffffff"
        top_frame.style['width'] = "800px"
        top_frame.style['position'] = "absolute"
        top_frame.style['margin'] = "0px auto"
        top_frame.style['height'] = "480px"
        top_frame.style['overflow'] = "auto"
        raw_data_panel = Widget()
        raw_data_panel.attributes['editor_varname'] = "raw_data_panel"
        raw_data_panel.attributes['editor_constructor'] = "()"
        raw_data_panel.attributes['editor_baseclass'] = "Widget"
        raw_data_panel.attributes['editor_tag_type'] = "widget"
        raw_data_panel.attributes['editor_newclass'] = "False"
        raw_data_panel.attributes['class'] = "Widget"
        raw_data_panel.style['display'] = "block"
        raw_data_panel.style['left'] = "16px"
        raw_data_panel.style['top'] = "256px"
        raw_data_panel.style['font-weight'] = "bold"
        raw_data_panel.style['width'] = "761px"
        raw_data_panel.style['position'] = "absolute"
        raw_data_panel.style['margin'] = "0px auto"
        raw_data_panel.style['border-style'] = "solid"
        raw_data_panel.style['height'] = "207px"
        raw_data_panel.style['overflow'] = "auto"
        title_encoders = Label('Encoders (L, R): ')
        title_encoders.attributes['editor_varname'] = "title_encoders"
        title_encoders.attributes['editor_constructor'] = "('Encoders (L, R): ')"
        title_encoders.attributes['editor_baseclass'] = "Label"
        title_encoders.attributes['editor_tag_type'] = "widget"
        title_encoders.attributes['editor_newclass'] = "False"
        title_encoders.attributes['class'] = "Label"
        title_encoders.style['display'] = "block"
        title_encoders.style['left'] = "30px"
        title_encoders.style['top'] = "125px"
        title_encoders.style['font-weight'] = "bold"
        title_encoders.style['width'] = "300px"
        title_encoders.style['position'] = "absolute"
        title_encoders.style['margin'] = "0px auto"
        title_encoders.style['height'] = "30px"
        title_encoders.style['overflow'] = "auto"
        raw_data_panel.append(title_encoders, 'title_encoders')
        push_button_data = Label('Off')
        push_button_data.attributes['editor_varname'] = "push_button_data"
        push_button_data.attributes['editor_constructor'] = "('Off')"
        push_button_data.attributes['editor_baseclass'] = "Label"
        push_button_data.attributes['editor_tag_type'] = "widget"
        push_button_data.attributes['editor_newclass'] = "False"
        push_button_data.attributes['class'] = "Label"
        push_button_data.style['display'] = "block"
        push_button_data.style['left'] = "230px"
        push_button_data.style['top'] = "155px"
        push_button_data.style['width'] = "100px"
        push_button_data.style['position'] = "absolute"
        push_button_data.style['margin'] = "0px auto"
        push_button_data.style['height'] = "30px"
        push_button_data.style['overflow'] = "auto"
        raw_data_panel.append(push_button_data, 'push_button_data')
        right_bumper_value = Label('Off')
        right_bumper_value.attributes['editor_varname'] = "right_bumper_value"
        right_bumper_value.attributes['editor_constructor'] = "('Off')"
        right_bumper_value.attributes['editor_baseclass'] = "Label"
        right_bumper_value.attributes['editor_tag_type'] = "widget"
        right_bumper_value.attributes['editor_newclass'] = "False"
        right_bumper_value.attributes['class'] = "Label"
        right_bumper_value.style['display'] = "block"
        right_bumper_value.style['left'] = "350px"
        right_bumper_value.style['top'] = "95px"
        right_bumper_value.style['width'] = "100px"
        right_bumper_value.style['position'] = "absolute"
        right_bumper_value.style['margin'] = "0px auto"
        right_bumper_value.style['height'] = "30px"
        right_bumper_value.style['overflow'] = "auto"
        raw_data_panel.append(right_bumper_value, 'right_bumper_value')
        y_axis_value = Label('1.000')
        y_axis_value.attributes['editor_varname'] = "y_axis_value"
        y_axis_value.attributes['editor_constructor'] = "('1.000')"
        y_axis_value.attributes['editor_baseclass'] = "Label"
        y_axis_value.attributes['editor_tag_type'] = "widget"
        y_axis_value.attributes['editor_newclass'] = "False"
        y_axis_value.attributes['class'] = "Label"
        y_axis_value.style['display'] = "block"
        y_axis_value.style['left'] = "350px"
        y_axis_value.style['top'] = "65px"
        y_axis_value.style['width'] = "100px"
        y_axis_value.style['position'] = "absolute"
        y_axis_value.style['margin'] = "0px auto"
        y_axis_value.style['height'] = "30px"
        y_axis_value.style['overflow'] = "auto"
        raw_data_panel.append(y_axis_value, 'y_axis_value')
        line_follower_center_value = Label('255')
        line_follower_center_value.attributes['editor_varname'] = "line_follower_center_value"
        line_follower_center_value.attributes['editor_constructor'] = "('255')"
        line_follower_center_value.attributes['editor_baseclass'] = "Label"
        line_follower_center_value.attributes['editor_tag_type'] = "widget"
        line_follower_center_value.attributes['editor_newclass'] = "False"
        line_follower_center_value.attributes['class'] = "Label"
        line_follower_center_value.style['display'] = "block"
        line_follower_center_value.style['left'] = "350px"
        line_follower_center_value.style['top'] = "35px"
        line_follower_center_value.style['width'] = "100px"
        line_follower_center_value.style['position'] = "absolute"
        line_follower_center_value.style['margin'] = "0px auto"
        line_follower_center_value.style['height'] = "30px"
        line_follower_center_value.style['overflow'] = "auto"
        raw_data_panel.append(line_follower_center_value, 'line_follower_center_value')
        z_axis_value = Label('1.000')
        z_axis_value.attributes['editor_varname'] = "z_axis_value"
        z_axis_value.attributes['editor_constructor'] = "('1.000')"
        z_axis_value.attributes['editor_baseclass'] = "Label"
        z_axis_value.attributes['editor_tag_type'] = "widget"
        z_axis_value.attributes['editor_newclass'] = "False"
        z_axis_value.attributes['class'] = "Label"
        z_axis_value.style['display'] = "block"
        z_axis_value.style['left'] = "470px"
        z_axis_value.style['top'] = "65px"
        z_axis_value.style['width'] = "100px"
        z_axis_value.style['position'] = "absolute"
        z_axis_value.style['margin'] = "0px auto"
        z_axis_value.style['height'] = "30px"
        z_axis_value.style['overflow'] = "auto"
        raw_data_panel.append(z_axis_value, 'z_axis_value')
        x_axis_value = Label('1.000')
        x_axis_value.attributes['editor_varname'] = "x_axis_value"
        x_axis_value.attributes['editor_constructor'] = "('1.000')"
        x_axis_value.attributes['editor_baseclass'] = "Label"
        x_axis_value.attributes['editor_tag_type'] = "widget"
        x_axis_value.attributes['editor_newclass'] = "False"
        x_axis_value.attributes['class'] = "Label"
        x_axis_value.style['display'] = "block"
        x_axis_value.style['left'] = "230px"
        x_axis_value.style['top'] = "65px"
        x_axis_value.style['width'] = "100px"
        x_axis_value.style['position'] = "absolute"
        x_axis_value.style['margin'] = "0px auto"
        x_axis_value.style['height'] = "30px"
        x_axis_value.style['overflow'] = "auto"
        raw_data_panel.append(x_axis_value, 'x_axis_value')
        left_encoder_value = Label('0')
        left_encoder_value.attributes['editor_varname'] = "left_encoder_value"
        left_encoder_value.attributes['editor_constructor'] = "('40000')"
        left_encoder_value.attributes['editor_baseclass'] = "Label"
        left_encoder_value.attributes['editor_tag_type'] = "widget"
        left_encoder_value.attributes['editor_newclass'] = "False"
        left_encoder_value.attributes['class'] = "Label"
        left_encoder_value.style['display'] = "block"
        left_encoder_value.style['left'] = "230px"
        left_encoder_value.style['top'] = "125px"
        left_encoder_value.style['width'] = "100px"
        left_encoder_value.style['position'] = "absolute"
        left_encoder_value.style['margin'] = "0px auto"
        left_encoder_value.style['height'] = "30px"
        left_encoder_value.style['overflow'] = "auto"
        raw_data_panel.append(left_encoder_value, 'left_encoder_value')
        right_encoder_value = Label('0')
        right_encoder_value.attributes['editor_varname'] = "right_encoder_value"
        right_encoder_value.attributes['editor_constructor'] = "('40000')"
        right_encoder_value.attributes['editor_baseclass'] = "Label"
        right_encoder_value.attributes['editor_tag_type'] = "widget"
        right_encoder_value.attributes['editor_newclass'] = "False"
        right_encoder_value.attributes['class'] = "Label"
        right_encoder_value.style['display'] = "block"
        right_encoder_value.style['left'] = "350px"
        right_encoder_value.style['top'] = "125px"
        right_encoder_value.style['width'] = "100px"
        right_encoder_value.style['position'] = "absolute"
        right_encoder_value.style['margin'] = "0px auto"
        right_encoder_value.style['height'] = "30px"
        right_encoder_value.style['overflow'] = "auto"
        raw_data_panel.append(right_encoder_value, 'right_encoder_value')
        line_follower_right_value = Label('255')
        line_follower_right_value.attributes['editor_varname'] = "line_follower_right_value"
        line_follower_right_value.attributes['editor_constructor'] = "('255')"
        line_follower_right_value.attributes['editor_baseclass'] = "Label"
        line_follower_right_value.attributes['editor_tag_type'] = "widget"
        line_follower_right_value.attributes['editor_newclass'] = "False"
        line_follower_right_value.attributes['class'] = "Label"
        line_follower_right_value.style['display'] = "block"
        line_follower_right_value.style['left'] = "470px"
        line_follower_right_value.style['top'] = "36px"
        line_follower_right_value.style['width'] = "100px"
        line_follower_right_value.style['position'] = "absolute"
        line_follower_right_value.style['margin'] = "0px auto"
        line_follower_right_value.style['height'] = "30px"
        line_follower_right_value.style['overflow'] = "auto"
        raw_data_panel.append(line_follower_right_value, 'line_follower_right_value')
        title_push_button = Label('Push Button: ')
        title_push_button.attributes['editor_varname'] = "title_push_button"
        title_push_button.attributes['editor_constructor'] = "('Push Button: ')"
        title_push_button.attributes['editor_baseclass'] = "Label"
        title_push_button.attributes['editor_tag_type'] = "widget"
        title_push_button.attributes['editor_newclass'] = "False"
        title_push_button.attributes['class'] = "Label"
        title_push_button.style['display'] = "block"
        title_push_button.style['left'] = "30px"
        title_push_button.style['top'] = "155px"
        title_push_button.style['font-weight'] = "bold"
        title_push_button.style['width'] = "100px"
        title_push_button.style['position'] = "absolute"
        title_push_button.style['margin'] = "0px auto"
        title_push_button.style['height'] = "30px"
        title_push_button.style['overflow'] = "auto"
        raw_data_panel.append(title_push_button, 'title_push_button')
        title_accel = Label('Accelerometer (X, Y, Z): ')
        title_accel.attributes['editor_varname'] = "title_accel"
        title_accel.attributes['editor_constructor'] = "('Accelerometer (X, Y, Z): ')"
        title_accel.attributes['editor_baseclass'] = "Label"
        title_accel.attributes['editor_tag_type'] = "widget"
        title_accel.attributes['editor_newclass'] = "False"
        title_accel.attributes['class'] = "Label"
        title_accel.style['display'] = "block"
        title_accel.style['left'] = "30px"
        title_accel.style['top'] = "65px"
        title_accel.style['font-weight'] = "bold"
        title_accel.style['width'] = "192px"
        title_accel.style['position'] = "absolute"
        title_accel.style['margin'] = "0px auto"
        title_accel.style['height'] = "29px"
        title_accel.style['overflow'] = "auto"
        raw_data_panel.append(title_accel, 'title_accel')
        left_bumper_value = Label('Off')
        left_bumper_value.attributes['editor_varname'] = "left_bumper_value"
        left_bumper_value.attributes['editor_constructor'] = "('Off')"
        left_bumper_value.attributes['editor_baseclass'] = "Label"
        left_bumper_value.attributes['editor_tag_type'] = "widget"
        left_bumper_value.attributes['editor_newclass'] = "False"
        left_bumper_value.attributes['class'] = "Label"
        left_bumper_value.style['display'] = "block"
        left_bumper_value.style['left'] = "230px"
        left_bumper_value.style['top'] = "95px"
        left_bumper_value.style['width'] = "100px"
        left_bumper_value.style['position'] = "absolute"
        left_bumper_value.style['margin'] = "0px auto"
        left_bumper_value.style['height'] = "30px"
        left_bumper_value.style['overflow'] = "auto"
        raw_data_panel.append(left_bumper_value, 'left_bumper_value')
        title_line_follower = Label('Line Followers (L, R, C): ')
        title_line_follower.attributes['editor_varname'] = "title_line_follower"
        title_line_follower.attributes['editor_constructor'] = "('Line Followers (L, R, C): ')"
        title_line_follower.attributes['editor_baseclass'] = "Label"
        title_line_follower.attributes['editor_tag_type'] = "widget"
        title_line_follower.attributes['editor_newclass'] = "False"
        title_line_follower.attributes['class'] = "Label"
        title_line_follower.style['display'] = "block"
        title_line_follower.style['left'] = "30px"
        title_line_follower.style['top'] = "35px"
        title_line_follower.style['font-weight'] = "bold"
        title_line_follower.style['width'] = "181px"
        title_line_follower.style['position'] = "absolute"
        title_line_follower.style['margin'] = "0px auto"
        title_line_follower.style['height'] = "33px"
        title_line_follower.style['overflow'] = "auto"
        raw_data_panel.append(title_line_follower, 'title_line_follower')
        title_bumpers = Label('Bumpers (L, R): ')
        title_bumpers.attributes['editor_varname'] = "title_bumpers"
        title_bumpers.attributes['editor_constructor'] = "('Bumpers (L, R): ')"
        title_bumpers.attributes['editor_baseclass'] = "Label"
        title_bumpers.attributes['editor_tag_type'] = "widget"
        title_bumpers.attributes['editor_newclass'] = "False"
        title_bumpers.attributes['class'] = "Label"
        title_bumpers.style['display'] = "block"
        title_bumpers.style['left'] = "30px"
        title_bumpers.style['top'] = "95px"
        title_bumpers.style['font-weight'] = "bold"
        title_bumpers.style['width'] = "300px"
        title_bumpers.style['position'] = "absolute"
        title_bumpers.style['margin'] = "0px auto"
        title_bumpers.style['height'] = "30px"
        title_bumpers.style['overflow'] = "auto"
        raw_data_panel.append(title_bumpers, 'title_bumpers')
        line_follower_left_value = Label('255')
        line_follower_left_value.attributes['editor_varname'] = "line_follower_left_value"
        line_follower_left_value.attributes['editor_constructor'] = "('255')"
        line_follower_left_value.attributes['editor_baseclass'] = "Label"
        line_follower_left_value.attributes['editor_tag_type'] = "widget"
        line_follower_left_value.attributes['editor_newclass'] = "False"
        line_follower_left_value.attributes['class'] = "Label"
        line_follower_left_value.style['display'] = "block"
        line_follower_left_value.style['left'] = "230px"
        line_follower_left_value.style['top'] = "35px"
        line_follower_left_value.style['width'] = "100px"
        line_follower_left_value.style['position'] = "absolute"
        line_follower_left_value.style['margin'] = "0px auto"
        line_follower_left_value.style['height'] = "30px"
        line_follower_left_value.style['overflow'] = "auto"
        raw_data_panel.append(line_follower_left_value, 'line_follower_left_value')
        title_raw_sensor_data = Label('Sensor Data')
        title_raw_sensor_data.attributes['editor_varname'] = "title_raw_sensor_data"
        title_raw_sensor_data.attributes['editor_constructor'] = "('Sensor Data')"
        title_raw_sensor_data.attributes['editor_baseclass'] = "Label"
        title_raw_sensor_data.attributes['editor_tag_type'] = "widget"
        title_raw_sensor_data.attributes['editor_newclass'] = "False"
        title_raw_sensor_data.attributes['class'] = "Label"
        title_raw_sensor_data.style['display'] = "block"
        title_raw_sensor_data.style['left'] = "333px"
        title_raw_sensor_data.style['top'] = "3px"
        title_raw_sensor_data.style['font-weight'] = "bold"
        title_raw_sensor_data.style['width'] = "100px"
        title_raw_sensor_data.style['position'] = "absolute"
        title_raw_sensor_data.style['margin'] = "0px auto"
        title_raw_sensor_data.style['height'] = "30px"
        title_raw_sensor_data.style['overflow'] = "auto"
        raw_data_panel.append(title_raw_sensor_data, 'title_raw_sensor_data')
        top_frame.append(raw_data_panel, 'raw_data_panel')
        blink_checkbox = CheckBoxLabel('Blink LED', False, 'True')
        blink_checkbox.attributes['editor_varname'] = "blink_checkbox"
        blink_checkbox.attributes['editor_constructor'] = "('Blink LED',False,'True')"
        blink_checkbox.attributes['editor_baseclass'] = "CheckBoxLabel"
        blink_checkbox.attributes['editor_tag_type'] = "widget"
        blink_checkbox.attributes['editor_newclass'] = "False"
        blink_checkbox.attributes['class'] = "CheckBoxLabel"
        blink_checkbox.style['display'] = "block"
        blink_checkbox.style['left'] = "46px"
        blink_checkbox.style['top'] = "107px"
        blink_checkbox.style['font-weight'] = "bold"
        blink_checkbox.style['width'] = "100px"
        blink_checkbox.style['position'] = "absolute"
        blink_checkbox.style['margin'] = "0px auto"
        blink_checkbox.style['height'] = "30px"
        blink_checkbox.style['overflow'] = "auto"
        top_frame.append(blink_checkbox, 'blink_checkbox')
        button_reverse = Button('Reverse')
        button_reverse.attributes['editor_varname'] = "button_reverse"
        button_reverse.attributes['editor_constructor'] = "('Reverse')"
        button_reverse.attributes['editor_baseclass'] = "Button"
        button_reverse.attributes['editor_tag_type'] = "widget"
        button_reverse.attributes['editor_newclass'] = "False"
        button_reverse.attributes['class'] = "Button"
        button_reverse.style['display'] = "block"
        button_reverse.style['left'] = "352px"
        button_reverse.style['top'] = "182px"
        button_reverse.style['background-color'] = "#1d81f1"
        button_reverse.style['width'] = "100px"
        button_reverse.style['position'] = "absolute"
        button_reverse.style['margin'] = "0px auto"
        button_reverse.style['height'] = "30px"
        button_reverse.style['overflow'] = "auto"
        top_frame.append(button_reverse, 'button_reverse')
        button_forward = Button('Forward')
        button_forward.attributes['editor_varname'] = "button_forward"
        button_forward.attributes['editor_constructor'] = "('Forward')"
        button_forward.attributes['editor_baseclass'] = "Button"
        button_forward.attributes['editor_tag_type'] = "widget"
        button_forward.attributes['editor_newclass'] = "False"
        button_forward.attributes['class'] = "Button"
        button_forward.style['display'] = "block"
        button_forward.style['left'] = "350px"
        button_forward.style['top'] = "86px"
        button_forward.style['background-color'] = "#1d81f1"
        button_forward.style['width'] = "100px"
        button_forward.style['position'] = "absolute"
        button_forward.style['margin'] = "0px auto"
        button_forward.style['height'] = "30px"
        button_forward.style['overflow'] = "auto"
        top_frame.append(button_forward, 'button_forward')
        label_screen_title = Label('Raspberry RedBot Control and Monitor')
        label_screen_title.attributes['editor_varname'] = "label_screen_title"
        label_screen_title.attributes['editor_constructor'] = "('Raspberry RedBot Control and Monitor')"
        label_screen_title.attributes['editor_baseclass'] = "Label"
        label_screen_title.attributes['editor_tag_type'] = "widget"
        label_screen_title.attributes['editor_newclass'] = "False"
        label_screen_title.attributes['class'] = "Label"
        label_screen_title.style['display'] = "block"
        label_screen_title.style['left'] = "230px"
        label_screen_title.style['top'] = "24px"
        label_screen_title.style['font-weight'] = "bold"
        label_screen_title.style['font-size'] = "20px"
        label_screen_title.style['position'] = "absolute"
        label_screen_title.style['margin'] = "0px auto"
        label_screen_title.style['width'] = "358px"
        label_screen_title.style['height'] = "27px"
        label_screen_title.style['overflow'] = "auto"
        top_frame.append(label_screen_title, 'label_screen_title')
        # label_motor_weight_left = Label('Min')
        # label_motor_weight_left.attributes['editor_varname'] = "label_motor_weight_left"
        # label_motor_weight_left.attributes['editor_constructor'] = "('Min')"
        # label_motor_weight_left.attributes['editor_baseclass'] = "Label"
        # label_motor_weight_left.attributes['editor_tag_type'] = "widget"
        # label_motor_weight_left.attributes['editor_newclass'] = "False"
        # label_motor_weight_left.attributes['class'] = "Label"
        # label_motor_weight_left.style['display'] = "block"
        # label_motor_weight_left.style['left'] = "19px"
        # label_motor_weight_left.style['top'] = "233px"
        # label_motor_weight_left.style['font-weight'] = "bold"
        # label_motor_weight_left.style['width'] = "29px"
        # label_motor_weight_left.style['position'] = "absolute"
        # label_motor_weight_left.style['margin'] = "0px auto"
        # label_motor_weight_left.style['height'] = "30px"
        # label_motor_weight_left.style['overflow'] = "auto"
        # label_motor_weight_r = Label('Max')
        # label_motor_weight_r.attributes['editor_varname'] = "label_motor_weight_r"
        # label_motor_weight_r.attributes['editor_constructor'] = "('Max')"
        # label_motor_weight_r.attributes['editor_baseclass'] = "Label"
        # label_motor_weight_r.attributes['editor_tag_type'] = "widget"
        # label_motor_weight_r.attributes['editor_newclass'] = "False"
        # label_motor_weight_r.attributes['class'] = "Label"
        # label_motor_weight_r.style['display'] = "block"
        # label_motor_weight_r.style['left'] = "156px"
        # label_motor_weight_r.style['top'] = "233px"
        # label_motor_weight_r.style['font-weight'] = "bold"
        # label_motor_weight_r.style['width'] = "27px"
        # label_motor_weight_r.style['position'] = "absolute"
        # label_motor_weight_r.style['margin'] = "0px auto"
        # label_motor_weight_r.style['height'] = "29px"
        # label_motor_weight_r.style['overflow'] = "auto"
        # label_motor_weight_left.append(label_motor_weight_r, 'label_motor_weight_r')
        # top_frame.append(label_motor_weight_left, 'label_motor_weight_left')
        button_stop = Button('Stop')
        button_stop.attributes['editor_varname'] = "button_stop"
        button_stop.attributes['editor_constructor'] = "('Stop')"
        button_stop.attributes['editor_baseclass'] = "Button"
        button_stop.attributes['editor_tag_type'] = "widget"
        button_stop.attributes['editor_newclass'] = "False"
        button_stop.attributes['class'] = "Button"
        button_stop.style['display'] = "block"
        button_stop.style['left'] = "351px"
        button_stop.style['top'] = "134px"
        button_stop.style['background-color'] = "#fc0e24"
        button_stop.style['width'] = "100px"
        button_stop.style['position'] = "absolute"
        button_stop.style['margin'] = "0px auto"
        button_stop.style['height'] = "30px"
        button_stop.style['overflow'] = "auto"
        top_frame.append(button_stop, 'button_stop')
        button_play_tone = Button('Play Tone')
        button_play_tone.attributes['title'] = ""
        button_play_tone.attributes['editor_varname'] = "button_play_tone"
        button_play_tone.attributes['editor_constructor'] = "('Play Tone')"
        button_play_tone.attributes['editor_baseclass'] = "Button"
        button_play_tone.attributes['editor_tag_type'] = "widget"
        button_play_tone.attributes['editor_newclass'] = "False"
        button_play_tone.attributes['class'] = "Button"
        button_play_tone.style['display'] = "block"
        button_play_tone.style['left'] = "620px"
        button_play_tone.style['top'] = "73px"
        button_play_tone.style['background-color'] = "#098539"
        button_play_tone.style['width'] = "141px"
        button_play_tone.style['position'] = "absolute"
        button_play_tone.style['margin'] = "0px auto"
        button_play_tone.style['height'] = "30px"
        button_play_tone.style['overflow'] = "auto"
        top_frame.append(button_play_tone, 'button_play_tone')
        drop_down_distance = DropDown()
        drop_down_distance.attributes['editor_constructor'] = "()"
        drop_down_distance.attributes['editor_varname'] = "drop_down_distance"
        drop_down_distance.attributes['editor_baseclass'] = "DropDown"
        drop_down_distance.attributes['editor_tag_type'] = "widget"
        drop_down_distance.attributes['editor_newclass'] = "False"
        drop_down_distance.attributes['class'] = "DropDown"
        drop_down_distance.style['display'] = "block"
        drop_down_distance.style['left'] = "360px"
        drop_down_distance.style['top'] = "228px"
        drop_down_distance.style['width'] = "100px"
        drop_down_distance.style['position'] = "absolute"
        drop_down_distance.style['margin'] = "0px auto"
        drop_down_distance.style['height'] = "30px"
        drop_down_distance.style['overflow'] = "auto"
        drop_down_item_centimeters = DropDownItem('Centimeters')
        drop_down_item_centimeters.attributes['value'] = "Centimeters"
        drop_down_item_centimeters.attributes['editor_varname'] = "drop_down_item_centimeters"
        drop_down_item_centimeters.attributes['editor_constructor'] = "('Centimeters')"
        drop_down_item_centimeters.attributes['selected'] = "selected"
        drop_down_item_centimeters.attributes['editor_baseclass'] = "DropDownItem"
        drop_down_item_centimeters.attributes['editor_tag_type'] = "widget"
        drop_down_item_centimeters.attributes['editor_newclass'] = "False"
        drop_down_item_centimeters.attributes['class'] = "DropDownItem"
        drop_down_item_centimeters.style['display'] = "block"
        drop_down_item_centimeters.style['left'] = "30px"
        drop_down_item_centimeters.style['top'] = "18px"
        drop_down_item_centimeters.style['width'] = "100px"
        drop_down_item_centimeters.style['position'] = "absolute"
        drop_down_item_centimeters.style['margin'] = "0px auto"
        drop_down_item_centimeters.style['height'] = "30px"
        drop_down_item_centimeters.style['overflow'] = "auto"
        drop_down_distance.append(drop_down_item_centimeters, 'drop_down_item_centimeters')
        drop_down_item_inches = DropDownItem('Inches')
        drop_down_item_inches.attributes['value'] = "Inches"
        drop_down_item_inches.attributes['editor_varname'] = "drop_down_item_inches"
        drop_down_item_inches.attributes['editor_constructor'] = "('Inches')"
        drop_down_item_inches.attributes['editor_baseclass'] = "DropDownItem"
        drop_down_item_inches.attributes['editor_tag_type'] = "widget"
        drop_down_item_inches.attributes['editor_newclass'] = "False"
        drop_down_item_inches.attributes['class'] = "DropDownItem"
        drop_down_item_inches.style['display'] = "block"
        drop_down_item_inches.style['left'] = "31px"
        drop_down_item_inches.style['top'] = "14px"
        drop_down_item_inches.style['width'] = "100px"
        drop_down_item_inches.style['position'] = "absolute"
        drop_down_item_inches.style['margin'] = "0px auto"
        drop_down_item_inches.style['height'] = "30px"
        drop_down_item_inches.style['overflow'] = "auto"
        drop_down_distance.append(drop_down_item_inches, 'drop_down_item_inches')
        top_frame.append(drop_down_distance, 'drop_down_distance')
        label_distance = Label('Distance Traveled In ')
        label_distance.attributes['editor_varname'] = "label_distance"
        label_distance.attributes['editor_constructor'] = "('Distance Traveled In ')"
        label_distance.attributes['editor_baseclass'] = "Label"
        label_distance.attributes['editor_tag_type'] = "widget"
        label_distance.attributes['editor_newclass'] = "False"
        label_distance.attributes['class'] = "Label"
        label_distance.style['display'] = "block"
        label_distance.style['left'] = "232px"
        label_distance.style['top'] = "231px"
        label_distance.style['font-weight'] = "bold"
        label_distance.style['width'] = "140px"
        label_distance.style['position'] = "absolute"
        label_distance.style['margin'] = "0px auto"
        label_distance.style['height'] = "26px"
        label_distance.style['overflow'] = "auto"
        top_frame.append(label_distance, 'label_distance')
        # slider_motor_power_weighting = Slider('50', 0, 100, 1)
        # slider_motor_power_weighting.attributes['value'] = "49"
        # slider_motor_power_weighting.attributes['step'] = "1"
        # slider_motor_power_weighting.attributes['editor_varname'] = "slider_motor_power_weighting"
        # slider_motor_power_weighting.attributes['autocomplete'] = "off"
        # slider_motor_power_weighting.attributes['min'] = "0"
        # slider_motor_power_weighting.attributes['type'] = "range"
        # slider_motor_power_weighting.attributes['max'] = "100"
        # slider_motor_power_weighting.attributes['editor_constructor'] = "('50',0,100,1)"
        # slider_motor_power_weighting.attributes['editor_baseclass'] = "Slider"
        # slider_motor_power_weighting.attributes['editor_tag_type'] = "widget"
        # slider_motor_power_weighting.attributes['editor_newclass'] = "False"
        # slider_motor_power_weighting.attributes['class'] = "range"
        # slider_motor_power_weighting.style['display'] = "block"
        # slider_motor_power_weighting.style['left'] = "48px"
        # slider_motor_power_weighting.style['top'] = "228px"
        # slider_motor_power_weighting.style['width'] = "100px"
        # slider_motor_power_weighting.style['position'] = "absolute"
        # slider_motor_power_weighting.style['margin'] = "0px auto"
        # slider_motor_power_weighting.style['height'] = "30px"
        # slider_motor_power_weighting.style['overflow'] = "auto"
        # top_frame.append(slider_motor_power_weighting, 'slider_motor_power_weighting')
        # label_speed_ratio = Label('Motor Power Weighting')
        # label_speed_ratio.attributes['editor_varname'] = "label_speed_ratio"
        # label_speed_ratio.attributes['editor_constructor'] = "('Motor Power Weighting')"
        # label_speed_ratio.attributes['editor_baseclass'] = "Label"
        # label_speed_ratio.attributes['editor_tag_type'] = "widget"
        # label_speed_ratio.attributes['editor_newclass'] = "False"
        # label_speed_ratio.attributes['class'] = "Label"
        # label_speed_ratio.style['display'] = "block"
        # label_speed_ratio.style['left'] = "28px"
        # label_speed_ratio.style['top'] = "210px"
        # label_speed_ratio.style['font-weight'] = "bold"
        # label_speed_ratio.style['width'] = "181px"
        # label_speed_ratio.style['position'] = "absolute"
        # label_speed_ratio.style['margin'] = "0px auto"
        # label_speed_ratio.style['height'] = "32px"
        # label_speed_ratio.style['overflow'] = "auto"
        # top_frame.append(label_speed_ratio, 'label_speed_ratio')
        button_right = Button('Right')
        button_right.attributes['editor_varname'] = "button_right"
        button_right.attributes['editor_constructor'] = "('Right')"
        button_right.attributes['editor_baseclass'] = "Button"
        button_right.attributes['editor_tag_type'] = "widget"
        button_right.attributes['editor_newclass'] = "False"
        button_right.attributes['class'] = "Button"
        button_right.style['display'] = "block"
        button_right.style['left'] = "478px"
        button_right.style['top'] = "134px"
        button_right.style['background-color'] = "#1d81f1"
        button_right.style['width'] = "100px"
        button_right.style['position'] = "absolute"
        button_right.style['margin'] = "0px auto"
        button_right.style['height'] = "30px"
        button_right.style['overflow'] = "auto"
        top_frame.append(button_right, 'button_right')
        label_reset_distance = Label('(Click on value to reset to zero)')
        label_reset_distance.attributes['editor_varname'] = "label_reset_distance"
        label_reset_distance.attributes['editor_constructor'] = "('(Click on value to reset to zero)')"
        label_reset_distance.attributes['editor_baseclass'] = "Label"
        label_reset_distance.attributes['editor_tag_type'] = "widget"
        label_reset_distance.attributes['editor_newclass'] = "False"
        label_reset_distance.attributes['class'] = "Label"
        label_reset_distance.style['display'] = "block"
        label_reset_distance.style['left'] = "540px"
        label_reset_distance.style['font-weight'] = "bold"
        label_reset_distance.style['width'] = "220px"
        label_reset_distance.style['position'] = "absolute"
        label_reset_distance.style['margin'] = "0px auto"
        label_reset_distance.style['height'] = "27px"
        label_reset_distance.style['overflow'] = "auto"
        label_reset_distance.style['top'] = "230px"
        top_frame.append(label_reset_distance, 'label_reset_distance')
        button_left = Button('Left')
        button_left.attributes['editor_varname'] = "button_left"
        button_left.attributes['editor_constructor'] = "('Left')"
        button_left.attributes['editor_baseclass'] = "Button"
        button_left.attributes['editor_tag_type'] = "widget"
        button_left.attributes['editor_newclass'] = "False"
        button_left.attributes['class'] = "Button"
        button_left.style['display'] = "block"
        button_left.style['left'] = "220px"
        button_left.style['top'] = "136px"
        button_left.style['background-color'] = "#1d81f1"
        button_left.style['width'] = "100px"
        button_left.style['position'] = "absolute"
        button_left.style['margin'] = "0px auto"
        button_left.style['height'] = "30px"
        button_left.style['overflow'] = "auto"
        top_frame.append(button_left, 'button_left')
        label_motor_speed = Label('Motor Speed')
        label_motor_speed.attributes['editor_varname'] = "label_motor_speed"
        label_motor_speed.attributes['editor_constructor'] = "('Motor Speed')"
        label_motor_speed.attributes['editor_baseclass'] = "Label"
        label_motor_speed.attributes['editor_tag_type'] = "widget"
        label_motor_speed.attributes['editor_newclass'] = "False"
        label_motor_speed.attributes['class'] = "Label"
        label_motor_speed.style['display'] = "block"
        label_motor_speed.style['left'] = "48px"
        label_motor_speed.style['top'] = "170px"
        label_motor_speed.style['font-weight'] = "bold"
        label_motor_speed.style['width'] = "100px"
        label_motor_speed.style['position'] = "absolute"
        label_motor_speed.style['margin'] = "0px auto"
        label_motor_speed.style['height'] = "30px"
        label_motor_speed.style['overflow'] = "auto"
        top_frame.append(label_motor_speed, 'label_motor_speed')
        button_led = Button('Toggle LED')
        button_led.attributes['editor_varname'] = "button_led"
        button_led.attributes['editor_constructor'] = "('Toggle LED')"
        button_led.attributes['editor_baseclass'] = "Button"
        button_led.attributes['editor_tag_type'] = "widget"
        button_led.attributes['editor_newclass'] = "False"
        button_led.attributes['class'] = "Button"
        button_led.style['display'] = "block"
        button_led.style['left'] = "21px"
        button_led.style['top'] = "69px"
        button_led.style['background-color'] = "#098539"
        button_led.style['width'] = "141px"
        button_led.style['position'] = "absolute"
        button_led.style['margin'] = "0px auto"
        button_led.style['height'] = "30px"
        button_led.style['overflow'] = "auto"
        top_frame.append(button_led, 'button_led')
        label_actual_distance = Label('0.000')
        label_actual_distance.attributes['editor_varname'] = "label_actual_distance"
        label_actual_distance.attributes['editor_constructor'] = "('0.000')"
        label_actual_distance.attributes['editor_baseclass'] = "Label"
        label_actual_distance.attributes['editor_tag_type'] = "widget"
        label_actual_distance.attributes['editor_newclass'] = "False"
        label_actual_distance.attributes['class'] = "Label"
        label_actual_distance.style['display'] = "block"
        label_actual_distance.style['left'] = "475px"
        label_actual_distance.style['top'] = "232px"
        label_actual_distance.style['font-weight'] = "bold"
        label_actual_distance.style['width'] = "100px"
        label_actual_distance.style['position'] = "absolute"
        label_actual_distance.style['margin'] = "0px auto"
        label_actual_distance.style['height'] = "30px"
        label_actual_distance.style['overflow'] = "auto"
        label_actual_distance.style['color'] = "#0c9572"
        top_frame.append(label_actual_distance, 'label_actual_distance')
        slider_motor_speed = Slider('255', 60, 255, 1)
        slider_motor_speed.attributes['value'] = "255"
        slider_motor_speed.attributes['step'] = "1"
        slider_motor_speed.attributes['editor_varname'] = "slider_motor_speed"
        slider_motor_speed.attributes['autocomplete'] = "off"
        slider_motor_speed.attributes['min'] = "60"
        slider_motor_speed.attributes['type'] = "range"
        slider_motor_speed.attributes['max'] = "255"
        slider_motor_speed.attributes['editor_constructor'] = "('60',60,255,1)"
        slider_motor_speed.attributes['editor_baseclass'] = "Slider"
        slider_motor_speed.attributes['editor_tag_type'] = "widget"
        slider_motor_speed.attributes['editor_newclass'] = "False"
        slider_motor_speed.attributes['class'] = "range"
        slider_motor_speed.style['display'] = "block"
        slider_motor_speed.style['left'] = "36px"
        slider_motor_speed.style['top'] = "190px"
        slider_motor_speed.style['font-weight'] = "bold"
        slider_motor_speed.style['width'] = "100px"
        slider_motor_speed.style['position'] = "absolute"
        slider_motor_speed.style['margin'] = "0px auto"
        slider_motor_speed.style['height'] = "30px"
        slider_motor_speed.style['overflow'] = "auto"
        top_frame.append(slider_motor_speed, 'slider_motor_speed')
        top_frame.children['blink_checkbox'].set_on_change_listener(self.onchange_blink_checkbox)
        top_frame.children['button_reverse'].set_on_click_listener(self.onclick_button_reverse)
        top_frame.children['button_forward'].set_on_click_listener(self.onclick_button_forward)
        top_frame.children['button_stop'].set_on_click_listener(self.onclick_button_stop)
        top_frame.children['button_play_tone'].set_on_click_listener(self.onclick_button_play_tone)
        top_frame.children['drop_down_distance'].set_on_change_listener(self.onchange_drop_down_distance)
        # top_frame.children['slider_motor_power_weighting'].set_on_change_listener(
        #     self.onchange_slider_motor_power_weighting)
        top_frame.children['button_right'].set_on_click_listener(self.onclick_button_right)
        top_frame.children['button_left'].set_on_click_listener(self.onclick_button_left)
        top_frame.children['button_led'].set_on_click_listener(self.onclick_button_led)
        top_frame.children['label_actual_distance'].set_on_click_listener(self.onclick_label_actual_distance)
        top_frame.children['slider_motor_speed'].set_on_change_listener(self.onchange_slider_motor_speed)

        self.top_frame = top_frame
        return self.top_frame

    def clean_up(self):
        """
        Clean up before exiting - override if additional cleanup is necessary

        :return:
        """
        self.publisher.close()
        self.subscriber.close()
        self.context.term()
        # self.stop()
        # sys.exit(0)

    def incoming_message_processing(self, topic, payload):
        """
        :param topic: Message Topic string
        :param payload: Message Data
        :return:
        """
        if topic == 'left_encoder_tick':
            self.distance += 0.125
            distance = self.distance
            if self.units == 'Centimeters':
                distance = distance * 2.54
            self.left_encoder_count += 1
            self.the_data_panel_widgets['left_encoder_value'].set_text(str(self.left_encoder_count))
            distance_traveled_string = '{0: >#0.3f}'.format(float(distance))
            self.the_widgets['label_actual_distance'].set_text(distance_traveled_string)
        elif topic == 'right_encoder_tick':
            self.right_encoder_count += 1
            self.the_data_panel_widgets['right_encoder_value'].set_text(str(self.right_encoder_count))
        elif topic == 'left_bumper_state_change':
            if payload['level'] == 0:
                self.the_data_panel_widgets['left_bumper_value'].set_text('On')
                self.stop()
            else:
                self.the_data_panel_widgets['left_bumper_value'].set_text('Off')
        elif topic == 'right_bumper_state_change':
            if payload['level'] == 0:
                self.the_data_panel_widgets['right_bumper_value'].set_text('On')
                self.stop()
            else:
                self.the_data_panel_widgets['right_bumper_value'].set_text('Off')
        elif topic == 'button_state_change':
            if payload['level'] == 0:
                self.the_data_panel_widgets['push_button_data'].set_text('On')
            else:
                self.the_data_panel_widgets['push_button_data'].set_text('Off')
        elif topic == 'I2C72':
            payload_data = str(payload['data'])
            if payload['tag'] == 0:
                self.the_data_panel_widgets['line_follower_left_value'].set_text(payload_data)
            if payload['tag'] == 1:
                self.the_data_panel_widgets['line_follower_center_value'].set_text(payload_data)
            if payload['tag'] == 2:
                self.the_data_panel_widgets['line_follower_right_value'].set_text(payload_data)
        elif topic == 'I2C83':
            EARTH_GRAVITY_MS2 = 9.80665
            SCALE_MULTIPLIER = 0.004

            raw = payload['data']

            x = raw[0] | (raw[1] << 8)
            if (x & (1 << 16 - 1)):
                x = x - (1 << 16)

            y = raw[2] | (raw[3] << 8)
            if (y & (1 << 16 - 1)):
                y = y - (1 << 16)

            z = raw[4] | (raw[5] << 8)
            if (z & (1 << 16 - 1)):
                z = z - (1 << 16)

            x = x * SCALE_MULTIPLIER
            y = y * SCALE_MULTIPLIER
            z = z * SCALE_MULTIPLIER


            x = (x * EARTH_GRAVITY_MS2) / 10
            y = (y * EARTH_GRAVITY_MS2) / 10
            z = (z * EARTH_GRAVITY_MS2) / 10

            x = round(x, 4)
            y = round(y, 4)
            z = round(z, 4)

            self.the_data_panel_widgets['x_axis_value'].set_text(str(x))
            self.the_data_panel_widgets['y_axis_value'].set_text(str(y))
            self.the_data_panel_widgets['z_axis_value'].set_text(str(z))


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

    def onchange_blink_checkbox(self, emitter, new_value):
        if new_value == 'false':
            self.blink_led = False
        else:
            self.blink_led = True

    def onclick_button_reverse(self, emitter):
        self.current_vehicle_direction = 'reverse'

        self.reset_button_color()
        emitter.style['background-color'] = '#000000'
        self.go_reverse()

    def onclick_button_forward(self, emitter):
        self.current_vehicle_direction = 'forward'
        self.reset_button_color()
        emitter.style['background-color'] = '#000000'
        self.go_forward()

    def onclick_button_stop(self, emitter):
        self.stop()
        self.current_vehicle_direction = 'stop'
        topic = 'user_motor_command'
        payload = {'command': 'left_motor_coast'}
        self.publish_payload(payload, topic)
        payload = {'command': 'right_motor_coast'}
        self.publish_payload(payload, topic)
        self.reset_button_color()

    def onclick_button_play_tone(self, emitter):
        payload = {'command': 'tone', 'frequency': 1000, 'duration': 1000}
        self.publish_payload(payload, 'system_buzzer_command')


    def onchange_drop_down_distance(self, emitter, new_value):
        self.units = new_value

    # def onchange_slider_motor_power_weighting(self, emitter, new_value):
    #     pass

    def onclick_button_right(self, emitter):
        self.current_vehicle_direction = 'right'

        self.reset_button_color()
        emitter.style['background-color'] = '#000000'
        self.go_right()

    def onclick_button_left(self, emitter):
        self.current_vehicle_direction = 'left'

        self.reset_button_color()
        emitter.style['background-color'] = '#000000'

        self.go_left()

    def onclick_button_led(self, emitter):
        if not self.led_state:
            self.led_state = True
            if self.blink_led:
                payload = {'command': 'blink_led',
                           'blink_rate': 1,
                           'number_of_blinks': 5}
                self.publish_payload(payload, 'user_led_command')
                self.led_state = False
            else:
                payload = {'command': 'led_on'}
                self.publish_payload(payload, 'user_led_command')
        else:
            self.led_state = False
            payload = {'command': 'led_off'}
            self.publish_payload(payload, 'user_led_command')


    def onclick_label_actual_distance(self, emitter):
        self.the_data_panel_widgets['left_encoder_value'].set_text('0')
        self.the_data_panel_widgets['right_encoder_value'].set_text('0')
        self.the_widgets['label_actual_distance'].set_text('0.000')
        self.distance = 0
        self.left_encoder_count = 0
        self.right_encoder_count = 0


    def onchange_slider_motor_speed(self, emitter, new_value):
        self.speed = int(new_value)
        if self.current_vehicle_direction == 'forward':
            self.go_forward()
        elif self.current_vehicle_direction == 'reverse':
            self.go_reverse()
        elif self.current_vehicle_direction == 'left':
            self.go_left()
        elif self.current_vehicle_direction == 'right':
            self.go_right()


    def reset_button_color(self):
        self.root.children['button_left'].style['background-color'] = self.default_button_color
        self.root.children['button_right'].style['background-color'] = self.default_button_color
        self.root.children['button_forward'].style['background-color'] = self.default_button_color
        self.root.children['button_reverse'].style['background-color'] = self.default_button_color

    def go_forward(self):
        topic = 'user_motor_command'
        payload = {'command': 'left_motor_forward', 'speed': self.speed}
        self.publish_payload(payload, topic)
        payload = {'command': 'right_motor_forward', 'speed': self.speed}
        self.publish_payload(payload, topic)

    def go_reverse(self):
        topic = 'user_motor_command'
        payload = {'command': 'left_motor_reverse', 'speed': self.speed}
        self.publish_payload(payload, topic)
        payload = {'command': 'right_motor_reverse', 'speed': self.speed}
        self.publish_payload(payload, topic)

    def go_left(self):
        topic = 'user_motor_command'
        payload = {'command': 'right_motor_forward', 'speed': self.speed}
        self.publish_payload(payload, topic)
        #payload = {'command': 'left_motor_coast'}
        payload = {'command': 'left_motor_forward', 'speed': self.speed -50 }

        self.publish_payload(payload, topic)


    def go_right(self):
        topic = 'user_motor_command'
        payload = {'command': 'left_motor_forward', 'speed': self.speed}
        self.publish_payload(payload, topic)
        #payload = {'command': 'right_motor_coast'}
        payload = {'command': 'right_motor_forward', 'speed': self.speed -50 }

        self.publish_payload(payload, topic)

    def stop(self):
        self.current_vehicle_direction = 'stop'
        topic = 'user_motor_command'
        payload = {'command': 'left_motor_coast'}
        self.publish_payload(payload, topic)
        payload = {'command': 'right_motor_coast'}
        self.publish_payload(payload, topic)
        self.reset_button_color()



def redbot_gui():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # use the google dns
    s.connect(('8.8.8.8', 0))
    RedBot.gui_ip_address = s.getsockname()[0]

    if len(sys.argv) > 1:
        RedBot.back_plane_ip_address = sys.argv[1]
    # argument, so just use the local host
    else:
        RedBot.back_plane_ip_address = s.getsockname()[0]

    # signal handler function called when Control-C occurs
    # noinspection PyShadowingNames,PyUnusedLocal,PyUnusedLocal
    def signal_handler(signal, frame):
        print('Control-C detected. See you soon.')

        sys.exit(0)

    # listen for SIGINT
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    start(RedBot, debug=False, address=RedBot.gui_ip_address, update_interval=.00001)


if __name__ == "__main__":
    redbot_gui()
