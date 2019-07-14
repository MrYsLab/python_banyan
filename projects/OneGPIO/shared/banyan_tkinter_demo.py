#!/usr/bin/env python3

"""
 This is the Python Banyan GUI that communicates with
 the Raspberry Pi Banyan Gateway

 Copyright (c) 2019 Alan Yorinks All right reserved.

 Python Banyan is free software; you can redistribute it and/or
 modify it under the terms of the GNU AFFERO GENERAL PUBLIC LICENSE
 Version 3 as published by the Free Software Foundation; either
 or (at your option) any later version.
 This library is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 General Public License for more details.

 You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
 along with this library; if not, write to the Free Software
 Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"""
import argparse
import signal
import sys
import tkinter as tk
from functools import partial
from tkinter import ttk, messagebox, IntVar

import msgpack
import zmq

from python_banyan.banyan_base import BanyanBase


class BanyanTkinterDemo(BanyanBase):
    """
    A 'simple' tkinter (tkinter is never simple)
    GUI for the Python Banyan Raspberry Pi Gateway.
    """

    def __init__(self, **kwargs):
        """

        :param kwargs: The arguments that the user can set on the command
        line, or
                       accept the defaults.
        """
        # initialize the parent class
        super(BanyanTkinterDemo, self).__init__(
            back_plane_ip_address=kwargs['back_plane_ip_address'],
            subscriber_port=kwargs['subscriber_port'],
            publisher_port=kwargs['publisher_port'],
            process_name=kwargs['process_name'])

        # create the root. window and set its size
        self.root = tk.Tk()
        self.root.geometry('800x600')

        # the top frame that will contain all the label frames
        frame = ttk.Frame(self.root)

        # We want the label frames to have a blue label, so we use styles
        # to do that.
        style = ttk.Style()
        style.configure("Blue.TLabelframe.Label", foreground="blue")

        # Create a list of pins to be used in the pins comboboxes. The first
        # entry in the
        # combobox is a string asking the user to select a pin.
        self.gpio_pins = []
        self.gpio_pins.insert(0, 'Select Pin')
        self.device_type = kwargs['device_type']

        if self.device_type == 'rpi':
            for pin in range(2, 28):
                self.gpio_pins.append(pin)
            # Give the app a title
            self.root.title(
                "Banyan Demo Station For Raspberry Pi Model 3 - All Pin "
                "Numbers Are BCM")
            # subscribe to receive messages from the raspberry pi gateway
            self.set_subscriber_topic('from_rpi_gateway')

            # topic to use when publishing messages
            self.my_topic = 'to_rpi_gateway'

        elif self.device_type == 'arduino':
            for pin in range(2, 20):
                self.gpio_pins.append(pin)
            # Give the app a title
            self.root.title("Banyan Demo Station For Arduino Uno")
            # subscribe to receive messages from the raspberry pi gateway
            self.set_subscriber_topic('from_arduino_gateway')

            # topic to use when publishing messages
            self.my_topic = 'to_arduino_gateway'

        elif self.device_type == 'esp8266':
            self.gpio_pins = [4, 5, 12, 13, 14, 15]
            self.gpio_pins.insert(0, 'Select Pin')
            # Give the app a title
            self.root.title("Banyan Demo Station For ESP-8266")
            # subscribe to receive messages from the raspberry pi gateway
            self.set_subscriber_topic('from_esp8266_gateway')

            # topic to use when publishing messages
            self.my_topic = 'to_esp8266_gateway'

        else:
            raise RuntimeError('Unknown device type')

        # create a list of valid digital pin states
        self.output_states = [0, 1]

        # put a message at the top of the list for the pin state combo box
        self.output_states.insert(0, 'Select State')

        # What follows is the code for each of the labelframes

        # DIGITAL OUTPUT SECTION
        # create the labelframe for the section
        digital_output_frame = ttk.LabelFrame(frame, text='Digital Output')
        digital_output_frame.grid(row=0, column=0, pady=(30, 20), sticky='W')
        digital_output_frame['style'] = "Blue.TLabelframe"

        # create the pin number label and combo box
        digital_output_label1 = tk.Label(digital_output_frame,
                                         text='Pin Number:')
        digital_output_label1.grid(row=1, column=1, padx=(10, 5), pady=(2, 5))
        self.digital_output_cb1 = ttk.Combobox(digital_output_frame, width=9,
                                               values=self.gpio_pins)
        self.digital_output_cb1.grid(row=1, column=2, pady=(2, 5))
        self.digital_output_cb1.current(0)

        # create the output state label and combobox
        digital_output_label2 = tk.Label(digital_output_frame,
                                         text='GPIO State:')
        digital_output_label2.grid(row=1, column=3, sticky='E', padx=(90, 5),
                                   pady=(2, 5))
        self.digital_output_cb2 = ttk.Combobox(digital_output_frame,
                                               values=self.output_states,
                                               width=10)
        self.digital_output_cb2.grid(row=1, column=4, pady=(2, 5))
        self.digital_output_cb2.current(0)

        # add an execution button to change the pin's state
        self.digital_output_button = ttk.Button(digital_output_frame,
                                                text='Set Output State:',
                                                command=self.set_output_state)
        self.digital_output_button.grid(row=1, column=5, padx=(110, 35),
                                        sticky='W', pady=(2, 5))

        # PWM OUTPUT SECTION
        # create the labelframe for the section
        pwm_output_frame = ttk.LabelFrame(frame, text='PWM Output')
        pwm_output_frame.grid(row=1, column=0, pady=(20, 20))
        pwm_output_frame['style'] = "Blue.TLabelframe"

        # create the pin number label and combo box
        pwm_output_label1 = tk.Label(pwm_output_frame, text='Pin Number:')
        pwm_output_label1.grid(row=1, column=1, padx=(10, 5), pady=(2, 5))
        if self.device_type == 'arduino':
            pwm_pins = [3, 5, 6, 9, 10, 11]
            self.pwm_output_cb1 = ttk.Combobox(pwm_output_frame, width=9,
                                               values=pwm_pins)
        else:
            self.pwm_output_cb1 = ttk.Combobox(pwm_output_frame, width=9,
                                               values=self.gpio_pins)
        self.pwm_output_cb1.grid(row=1, column=2, pady=(2, 5))
        self.pwm_output_cb1.current(0)

        # create the label and scale widget to set the PWM value
        pwm_scale_label = tk.Label(pwm_output_frame, text='PWM Value:')
        pwm_scale_label.grid(row=1, column=3, sticky='W', padx=(90, 5),
                             pady=(2, 5))

        if self.device_type == 'esp8266':
            self.pwm_output_scale = tk.Scale(pwm_output_frame,
                                             orient='horizontal', from_=0,
                                             to=1023,
                                             command=self.pwm_change)
        else:
            self.pwm_output_scale = tk.Scale(pwm_output_frame,
                                             orient='horizontal', from_=0,
                                             to=255,
                                             command=self.pwm_change)
        self.pwm_output_scale.grid(row=1, column=4, padx=(25, 230), pady=(0, 5))

        # THE TONE SECTION
        # create the labelframe
        tone_frame = ttk.LabelFrame(frame, text='Buzzer Tone Output')
        tone_frame.grid(row=2, column=0, pady=(20, 20))
        tone_frame['style'] = "Blue.TLabelframe"

        # create the pin number label and combo box
        tone_label1 = tk.Label(tone_frame, text='Pin Number:')
        tone_label1.grid(row=1, column=1, padx=(10, 5), pady=(2, 5))
        self.tone_cb1 = ttk.Combobox(tone_frame, width=9,
                                     values=self.gpio_pins)
        self.tone_cb1.grid(row=1, column=2, pady=(2, 5))
        self.tone_cb1.current(0)

        # create the label and scale widget to set the frequency value
        tone_scale_label = tk.Label(tone_frame, text='Frequency(hz):')
        tone_scale_label.grid(row=1, column=3, sticky='W', padx=(90, 5),
                              pady=(2, 5))
        self.tone_scale1 = tk.Scale(tone_frame, orient='horizontal', from_=1000,
                                    to=4000)
        self.tone_scale1.grid(row=1, column=4, padx=(5, 5), pady=(0, 5))

        # create the label and scale widget to set the duration value
        tone_scale_label2 = tk.Label(tone_frame, text='Duration(ms):')
        tone_scale_label2.grid(row=2, column=3, sticky='W', padx=(90, 5),
                               pady=(2, 5))
        self.tone_scale2 = tk.Scale(tone_frame, orient='horizontal', from_=500,
                                    to=2000)
        self.tone_scale2.grid(row=2, column=4, padx=(5, 5), pady=(0, 5))

        # add an execution button to play the tone
        self.tone_button = ttk.Button(tone_frame, text='Play Tone',
                                      command=self.play_tone)
        self.tone_button.grid(row=1, column=5, padx=(110, 35), sticky='W',
                              pady=(2, 5))

        # THE DIGITAL INPUT SECTION
        # create the labelframe

        # We need to create an IntVar for each
        # of the radiobuttons for pin selection, so that initially the
        # checkbuttons
        # display properly. Without this, things look strange. The IntVars are
        # assigned as a variable parameter when each radiobutton is created.
        # We will store the IntVars in a dictionary to be able to retrieve the
        # associated IntVar for each pin when a radiobutton is created.

        # We use a dictionary comprehension here to create the dictionary of
        # IntVars.
        self.cb_vars = {key: IntVar() for key in self.gpio_pins[1:]}

        # This is a dictionary of tk labels that will allow the display
        # of the state for each input pin. The key is a valid pin number
        # Note the values for each entry is a dummy value here. The actual
        # value is filled in when the radio button is created.
        self.input_visual_states = {key: key for key in self.gpio_pins[1:]}

        # create an activation dictionary
        self.input_active_states = {key: False for key in self.gpio_pins[1:]}

        digital_input_frame = ttk.LabelFrame(frame, text='Digital Input')
        digital_input_frame.grid(row=3, column=0, pady=(20, 20))
        # # notebook.add(frame1, text='   Digital Input  ')
        digital_input_frame['style'] = "Blue.TLabelframe"

        # Create a label and input widget for each of the 27 pins.

        # first valid pin number
        pin_index = 1
        cb_vars_index = 0

        for x in range(4):
            for y in range(7):
                try:
                    pin = self.gpio_pins[pin_index]
                except IndexError:
                    break
                spacer2 = tk.Label(digital_input_frame, text=' ')
                spacer2.grid(sticky='E', row=x + 1, column=y + 1, pady=(2, 5),
                             padx=(00, 88))
                # create a check button for each pin
                # The partial method is used so that we can identify which
                # radiobutton
                # was changed.
                try:
                    if len(str(self.gpio_pins[pin_index])) == 1:
                        pin_string = '0' + str(self.gpio_pins[pin_index])
                    else:
                        pin_string = str(self.gpio_pins[pin_index])
                    rb = ttk.Checkbutton(digital_input_frame,
                                         text='Pin ' + pin_string + ': ',
                                         variable=self.cb_vars[pin],
                                         command=partial(
                                             self.radio_button_change, pin))
                except (KeyError, IndexError):
                    raise
                # create label that will display the current state of the pin -
                # black is 0 and red is 1
                rb.grid(row=x + 1, column=y, padx=(5, 15), sticky='E',
                        pady=(2, 5))
                if self.device_type == 'esp8266':
                    self.digital_input_value_label = tk.Label(
                        digital_input_frame,
                        text='   ',
                        bg='red', )
                else:
                    self.digital_input_value_label = tk.Label(
                        digital_input_frame,
                        text='   ',
                        bg='black', )
                self.digital_input_value_label.grid(row=x + 1, column=y,
                                                    padx=(0, 0), sticky='E',
                                                    pady=(2, 5))
                self.input_visual_states[pin] = self.digital_input_value_label

                pin_index += 1
                cb_vars_index += 1

        # add a quit button to the frame

        self.quit_button = ttk.Button(frame, text='Quit',
                                      command=self.on_closing)
        self.quit_button.grid(row=5, column=0)

        frame.pack()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # we need to incorporate the banyan event loop into the tkinter
        # event loop. We establish this here using the "after" method.
        self.root.after(5, self.get_message)

        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.on_closing()

    # The following methods are the command handlers for the GUI widgets.
    # The methods create and publish messages that comply with the common
    # unified GPIO message specification.

    def set_output_state(self):
        """
        This method sends a message to set a GPIO pin as an
        output and sets its value.
        """
        pin = None
        value = None

        try:
            pin = int(self.digital_output_cb1.get())
        except ValueError:
            messagebox.showerror("Error", "Please select a pin number.")
        try:
            value = int(self.digital_output_cb2.get())
        except ValueError:
            messagebox.showerror("Error", "Please select an output value.")

        payload = {'command': 'set_mode_digital_output', 'pin': pin}
        self.publish_payload(payload, self.my_topic)

        payload = {'command': 'digital_write', 'pin': pin, 'value': value}
        self.publish_payload(payload, self.my_topic)

    def play_tone(self):
        """
        This method sends a message to activate a piezo buzzer
        on a specific pin, at a specific frequency for
        a specific duration.
        """
        pin = None

        try:
            pin = int(self.tone_cb1.get())
        except ValueError:
            messagebox.showerror("Error", "Please select a pin number.")
        freq = int(self.tone_scale1.get())
        duration = int(self.tone_scale2.get())

        payload = {'command': 'play_tone', 'pin': pin,
                   'freq': freq, 'duration': duration}
        self.publish_payload(payload, self.my_topic)

    def pwm_change(self, value):
        """
        This method sends a message to set a GPIO pin
        for PWM and then sets the pin to the user's
        selected value.
        :param value: The value from the slider control
        """
        pin = None
        try:
            pin = int(self.pwm_output_cb1.get())
        except ValueError:
            messagebox.showerror("Error", "Please select a pin number.")

        value = int(value)

        payload = {'command': 'set_mode_pwm', 'pin': pin}
        self.publish_payload(payload, self.my_topic)

        payload = {'command': 'pwm_write', 'pin': pin, 'value': value}
        self.publish_payload(payload, self.my_topic)

    def radio_button_change(self, pin):
        """
        Toggle the input active state with the user's selections
        :param pin:
        :return:
        """
        if self.input_active_states[pin]:
            self.input_active_states[pin] = False
        else:
            self.input_active_states[pin] = True
            payload = {'command': 'set_mode_digital_input', 'pin': pin}
            self.publish_payload(payload, self.my_topic)

    def get_message(self):
        """
        This method is called from the tkevent loop "after" call.
        It will poll for new zeromq messages within the tkinter event loop.
        """
        try:
            data = self.subscriber.recv_multipart(zmq.NOBLOCK)
            self.incoming_message_processing(data[0].decode(),
                                             msgpack.unpackb(data[1],
                                                             raw=False))
            self.root.after(1, self.get_message)

        except zmq.error.Again:
            try:
                self.root.after(1, self.get_message)
            except KeyboardInterrupt:
                self.root.destroy()
                self.publisher.close()
                self.subscriber.close()
                self.context.term()
                sys.exit(0)
        except KeyboardInterrupt:
            self.root.destroy()
            self.publisher.close()
            self.subscriber.close()
            self.context.term()
            sys.exit(0)

    def incoming_message_processing(self, topic, payload):
        """
        This method processes the incoming pin state change
        messages for GPIO pins set as inputs.

        :param topic:
        :param payload: {'report': 'digital_input', 'pin': pin,
                       'value': level, 'timestamp': time.time()}
        """
        # if the pin currently input active, process the state change

        pin = payload['pin']
        if self.input_active_states[pin]:
            if payload['value'] == 1:
                self.input_visual_states[pin].config(bg="red")
            else:
                self.input_visual_states[pin].config(bg="black")

    def on_closing(self):
        """
        Destroy the window
        """
        self.clean_up()
        self.root.destroy()


def banyan_tkinter_demo():
    parser = argparse.ArgumentParser()

    parser.add_argument("-b", dest="back_plane_ip_address", default="None",
                        help="None or IP address used by Back Plane")
    # allow the user to specify a name for the component and have it shown on
    # the console banner.
    # modify the default process name to one you wish to see on the banner.
    # change the default in the derived class to set the name
    parser.add_argument("-d", dest="device_type", default="rpi",
                        help="Select device type: arduino, esp8266 or rpi")
    parser.add_argument("-n", dest="process_name", default="TKINTER_GUI",
                        help="Set process name in banner")
    parser.add_argument("-p", dest="publisher_port", default='43124',
                        help="Publisher IP port")
    parser.add_argument("-s", dest="subscriber_port", default='43125',
                        help="Subscriber IP port")

    args = parser.parse_args()

    if args.back_plane_ip_address == 'None':
        args.back_plane_ip_address = None
    kw_options = {'back_plane_ip_address': args.back_plane_ip_address,
                  'publisher_port': args.publisher_port,
                  'subscriber_port': args.subscriber_port,
                  'process_name': args.process_name,
                  'device_type': args.device_type}

    # replace with the name of your class
    BanyanTkinterDemo(**kw_options)


def signal_handler(sig, frame):
    print('Exiting Through Signal Handler')
    raise KeyboardInterrupt


# listen for SIGINT
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


if __name__ == '__main__':
    banyan_tkinter_demo()
