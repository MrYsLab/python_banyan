
# GPIO Control

This section will look at a simple example illustrating GPIO control of a Raspberry Pi using Python Banyan.

The problem we will solve is this:

When a user presses a mechanical push button, an LED will light up,
and a Banyan message will be published. The Banyan message
contains the state change details of the push button -
 the GPIO pin number, the current state of the button, and a time
 tick to indicate when the change occurred.

When the user releases the pushbutton, the LED will be extinguished. 
Another message will be published, indicating the new state change.

All examples will use a Raspberry Pi Model 3 connected to a [Pibrella](http://pibrella.com/) hat for ease of use. 
The Pibrella has a push button and
several LEDs. This precludes us from having to wire individual components to the
Raspberry Pi.

For GPIO control, the [pigpio](http://abyz.me.uk/rpi/pigpio/) GPIO library will
be used.

## A Simple Solution To GPIO Control Of A Raspberry Pi

Let's begin by looking at a simple example
named [single.py](https://github.com/MrYsLab/python_banyan/blob/master/examples/single.py).



### The Code Line By Line

     1	"""
     2	 Copyright (c) 2016-2019 Alan Yorinks All right reserved.
     3
     4	 This program is free software; you can redistribute it and/or
     5	 modify it under the terms of the GNU AFFERO GENERAL PUBLIC LICENSE
     6	 Version 3 as published by the Free Software Foundation; either
     7	 or (at your option) any later version.
     8	 This library is distributed in the hope that it will be useful,
     9	 but WITHOUT ANY WARRANTY; without even the implied warranty of
    10	 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    11	 General Public License for more details.
    12
    13	 You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
    14	 along with this library; if not, write to the Free Software
    15	 Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
    16
    17	"""
    18
    19	import sys
    20
    21	import pigpio
    22
    23	from python_banyan.banyan_base import BanyanBase
    24
    25
    26	class Single(BanyanBase):
    27	    """
    28	    This class will monitor a push button connected to a
    29	    Raspberry Pi. When the button is pressed, an LED will light,
    30	    and message will be published with changed state of the input pin.
    31	    """
    32
    33	    def __init__(self, push_button=11, led=4, publish_topic='button'):
    34	        """
    35	        This method initialize the class for operation
    36	        :param push_button: push_button pin
    37	        :param led: led pin
    38	        :param publish_topic: publishing topic
    39	        """
    40
    41	        # initialize the parent
    42	        super(Single, self).__init__(process_name='Single')
    43
    44	        # make the input parameters available to the entire class
    45	        self.push_button = push_button
    46	        self.led = led
    47	        self.publish_topic = publish_topic
    48
    49	        # initialize the GPIO pins using pigpio
    50	        self.pi = pigpio.pi()
    51	        self.pi.set_mode(self.push_button, pigpio.INPUT)
    52	        self.pi.set_pull_up_down(self.push_button, pigpio.PUD_DOWN)
    53	        self.pi.set_mode(led, pigpio.OUTPUT)
    54
    55	        # set a glitch filter to debounce the switch
    56	        self.pi.set_glitch_filter(push_button, 100)
    57
    58	        # set a callback for when the button is pressed
    59	        self.pi.callback(self.push_button, pigpio.EITHER_EDGE,
    60	                         self.button_callback)
    61
    62	        # this will keep the program running forever
    63	        try:
    64	            self.receive_loop()
    65	        except KeyboardInterrupt:
    66	            sys.exit(0)
    67
    68	    def button_callback(self, gpio, level, tick):
    69	        """
    70	        This method receives a change in state of the
    71	        pushbutton.
    72
    73	        It will print the current state to the console
    74	        and reflect that state by turning the LED on
    75	        or OFF based on the state.
    76
    77	        It will also publish a message containing the state
    78	        change.
    79
    80	        :param gpio: pin number
    81	        :param level: pin level
    82	        :param tick: timer tick
    83	        """
    84	        print('The pushbutton state is {} on pin {} '
    85	              'and changed at tick {}'.format(level, gpio, tick))
    86
    87	        self.pi.write(self.led, level)
    88
    89	        # create a publishing payload
    90	        payload = {'pushbutton state': level, 'gpio_pin': gpio,
    91	                   'time_tick':tick}
    92	        self.publish_payload(payload, self.publish_topic)
    93
    94
    95	Single()

Line 21 imports the pigpio library.

Lines 49 through 60 set the pin mode for both the push button
and the LED.

Note: The Pibrella requires that the pull-down resistor be enabled on the
Raspberry Pi. Line 52 enables the pull-down resistor.

A "glitch" filter is set on line 56 to prevent the push button from
generating multiple events from a single press or release of the
button.

Line 59 establishes a callback for when the button is either
pressed or released.

Line 64 calls the base class receive_loop method to
keep the loop running until the user quits the program.

The callback method is contained in lines 68 through 92.

When the user presses or releases the pushbutton, the callback method will be
called by pigpio.

Lines 84 and 85 print a message to the console containing the
parameters passed by pigpio to this method.

On line 87, the LED is set to the reported state. Finally,
lines 89-92 create and publish a Banyan message about the push button
event.



Here is the output on the console after pressing and releasing the
button twice:

```
python3 single.py

************************************************************
Single using Back Plane IP address: 192.168.2.192
Subscriber Port = 43125
Publisher  Port = 43124
Loop Time = 0.1 seconds
************************************************************
The pushbutton state is 1 on pin 11 and changed at tick 3856477239
The pushbutton state is 0 on pin 11 and changed at tick 3857470672
The pushbutton state is 1 on pin 11 and changed at tick 3858747310
The pushbutton state is 0 on pin 11 and changed at tick 3859867653
```

And here is the output from a Monitor session as the button is pressed
and released.

```
$ monitor

************************************************************
Monitor using Back Plane IP address: 192.168.2.192
Subscriber Port = 43125
Publisher  Port = 43124
Loop Time = 0.1 seconds
************************************************************
button {'time_tick': 3856477239, 'pushbutton state': 1, 'gpio_pin': 11}
button {'time_tick': 3857470672, 'pushbutton state': 0, 'gpio_pin': 11}
button {'time_tick': 3858747310, 'pushbutton state': 1, 'gpio_pin': 11}
button {'time_tick': 3859867653, 'pushbutton state': 0, 'gpio_pin': 11}
```

<br>
<br>
Copyright (C) 2017-2020 Alan Yorinks All Rights Reserved