# Introduction To OneGPIO Gateways

A *OneGPIO Gateway* is a specialized Banyan component that is target-hardware specific. 
 It subscribes to and translates OneGPIO command messages to and from native target hardware 
 GPIO API calls. OneGPIO Gateways for the [Arduino](https://github.com/MrYsLab/python_banyan/blob/master/projects/OneGPIO/arduino_uno/arduino_gateway.py), 
[ESP-8266,](https://github.com/MrYsLab/python_banyan/blob/master/projects/OneGPIO/esp_8266/esp8266_gateway.py)
 and [Raspberry Pi](https://github.com/MrYsLab/python_banyan/blob/master/projects/OneGPIO/raspberry_pi/rpi_gateway.py) are included with this distribution.
 
A base class, called
[***GatewayBase,***](https://github.com/MrYsLab/python_banyan/blob/master/python_banyan/gateway_base/gateway_base.py)
is made available to simplify the task of creating a OneGPIO Gateway. This class encapsulates both BanyanBase functionality as well as
OneGPIO Gateway functionality. When implementing a OneGPIO Gateway, you may choose
any target GPIO API. For example, in creating the Raspberry Pi Gateway, the *pigpio* library
was chosen. If you prefer to use some other API, there are no restrictions to do so.

There is also a Python asyncio version of the base class, called
 [***GatewayBaseAIO***.](https://github.com/MrYsLab/python_banyan/blob/master/python_banyan/gateway_base_aio/gateway_base_aio.py)
 This additional base class,
was necessary to support the pymata-express asyncio GPIO library for the Arduino. It is very
similar to the GatewayBase class, and so it will not be discussed here.
 
# Understanding The GatewayBase Class
 
Let's look at the [code.](https://github.com/MrYsLab/python_banyan/blob/master/python_banyan/gateway_base/gateway_base.py) 
Below are code sections that are followed by a discussion. 


```
    23	from python_banyan.banyan_base import BanyanBase
    24	
    25	
    26	class GatewayBase(BanyanBase):
    27	    """
    28	    This class provides a common front end abstraction for all asyncio hardware gateways.
    29	    """
    30	
    31	    # pin modes
    32	    DIGITAL_INPUT_MODE = 0
    33	    DIGITAL_OUTPUT_MODE = 1
    34	    PWM_OUTPUT_MODE = 2
    35	    ANALOG_INPUT_MODE = 3
    36	    ANALOG_OUTPUT_MODE = 4
    37	    DIGITAL_INPUT_PULLUP_MODE = 5
    38	    I2C_MODE = 6
    39	    TONE_MODE = 7
    40	    SERVO_MODE = 8
    41	    STEPPER_MODE = 9
    42	    SONAR_MODE = 10
    43	    WILD_CARD_MODE = 11
    44	
    45	    # board types
    46	    ARDUINO = 0
    47	    RPi = 1
    48	    ESP8266 = 2
```

Since GatewayBase is derived by the BanyanBase class, we import BanyanBase on line
23. 

Lines 31-43 define a set of pin mode "constants" as class variables.

Lines 46-48 define some common board type identifiers.

```
    51	    def __init__(self, back_plane_ip_address=None, subscriber_port='43125',
    52	                 publisher_port='43124', process_name='',
    53	                 subscriber_list=None, board_type=None, ):
    54	        """
    55	
    56	        :param back_plane_ip_address: banyan_base back_planeIP Address -
    57	               if not specified, it will be set to the local computer
    58	        :param subscriber_port: banyan_base back plane subscriber port.
    59	               This must match that of the banyan_base backplane
    60	        :param publisher_port: banyan_base back plane publisher port.
    61	                               This must match that of the banyan_base
    62	                               backplane
    63	        :param process_name: Component identifier
    64	        :param subscriber_list: a tuple or list of topics to be subscribed to
    65	        :param board_type: micro-controller type ID
    66	
    67	        """
```
The \__init__ method accepts the standard BanyanBase input parameters, as well
as 2 additional  parameters. The *subscriber_list* parameter allows the user
to supply a list of subscription topics for the gateway, and *board_type* is an optional
parameter that will allow the user to supply a board type id.

```
    68	        if board_type:
    69	            self.board_type = board_type
    70	
    71	        if subscriber_list:
    72	            self.subscriber_list = subscriber_list
    73	        else:
    74	            self.subscriber_list = ('all')
    75	
    76	        # dictionaries for pin modes set by user
    77	        # an entry is board type specific
    78	
    79	        # this dictionary initially contains an entry for each default
    80	        # digital input pin
    81	
    82	        self.pins_dictionary = {}
    83	
    84	        # a pin can optionally be given a tag, it is used as a key to find
    85	        # pin number
    86	        # tag(string): pin(integer)
    87	        self.tags_dictionary = {}
    88	
    89	        self.init_pins_dictionary()
    90	
```

In this section, we save the input parameters and establish some data structures.

On line 74, if a subscriber_list was not provided, a default subscription  topic of *all*
is used as the lone entry into the subscriber_list. Of course, subscription
topics may be added at any time during run-time.

Line 82 creates an empty *pins_dictionary*. This dictionary is used by each
hardware-specific gateway to store pin information, such as the pin's mode and current state.

Line 87 creates an empty *tags_dictionary*. When setting a pin mode, if a tag is provided,
an entry is made into this dictionary. The tag is used as a key, and the pin number is the entry's value.

Line 89 calls the *init_pins_dictionary* method. See the discussion below for line 126 for
more information about this method.

```
    91	        # initialize the parent
    92	        super(GatewayBase, self).__init__(back_plane_ip_address=back_plane_ip_address,
    93	                                          subscriber_port=subscriber_port,
    94	                                          publisher_port=publisher_port,
    95	                                          process_name=process_name,
    96	                                          )
```

Line 91 initializes the BanyanBase class

```
    98	        self.command_dictionary = {'analog_write': self.analog_write,
    99	                                   'digital_write': self.digital_write,
   100	                                   'disable_analog_reporting': self.disable_analog_reporting,
   101	                                   'disable_digital_reporting': self.disable_digital_reporting,
   102	                                   'enable_analog_reporting': self.disable_analog_reporting,
   103	                                   'enable_digital_reporting': self.disable_digital_reporting,
   104	                                   'i2c_read': self.i2c_read,
   105	                                   'i2c_write': self.i2c_write,
   106	                                   'play_tone': self.play_tone,
   107	                                   'pwm_write': self.pwm_write,
   108	                                   'servo_position': self.servo_position,
   109	                                   'set_mode_analog_input': self.set_mode_analog_input,
   110	                                   'set_mode_digital_input': self.set_mode_digital_input,
   111	                                   'set_mode_digital_input_pullup': self.set_mode_digital_input_pullup,
   112	                                   'set_mode_digital_output': self.set_mode_digital_output,
   113	                                   'set_mode_i2c': self.set_mode_i2c,
   114	                                   'set_mode_pwm': self.set_mode_pwm,
   115	                                   'set_mode_servo': self.set_mode_servo,
   116	                                   'set_mode_sonar': self.set_mode_sonar,
   117	                                   'set_mode_stepper': self.set_mode_stepper,
   118	                                   'set_mode_tone': self.set_mode_tone,
   119	                                   'stepper_write': self.stepper_write,
   120	                                   }
```

Lines 98-120 create a *command_dictionary*. Every OneGPIO Gateway contains a 
*command_dictionary*.
 
The *command_dictionary* maps
 OneGPIO *commands* to
methods that ultimately process the command.
A OneGPIO *command string* is used as a key, and the value for each
key is a method *reference* that will be called on line 161 below.

```
   121	
   122	        if subscriber_list is not None:
   123	            for topic in subscriber_list:
   124	                self.set_subscriber_topic(topic)
```
The \__init__ method concludes by subscribing to all the topics within the subscriber_list.


```
   126	    def init_pins_dictionary(self):
   127	        """
   128	        This method will initialize the pins dictionary
   129	        This is handled within the class for each hardware type
   130	        """
   131	        raise NotImplementedError
```

This method ***must be***  overwritten by each hardware-specific OneGPiO Gateway, even if not needed.
This is to ensure that you have not forgotten to implement this method.

```
   133	    def incoming_message_processing(self, topic, payload):
   134	        """
   135	        Messages are sent here from the receive_loop
   136	        :param topic: Message Topic string
   137	        :param payload: Message Data
   138	        :return:
   139	        """
   140	        # process payload command
   141	        try:
   142	            command = payload['command']
   143	        except KeyError:
   144	            print(payload)
   145	            raise
   146	
   147	        # if a tag is provided and the tag is in the dictionary, fetch
   148	        # the associated pin number
   149	        if 'tag' in payload:
   150	            tag = payload['tag']
   151	            if tag:
   152	                if tag in self.tags_dictionary:
   153	                    pin = self.tags_dictionary[tag]
   154	                    # the pin is optional if using tag, so add it to the payload
   155	                    payload['pin'] = pin
   156	                else:
   157	                    self.tags_dictionary[payload['tag']] = payload['pin']
   158	
   159	        # if command is in the command dictionary, execute the command
   160	        if command in self.command_dictionary.keys():
   161	            self.command_dictionary[command](topic, payload)
   162	
   163	        # for unknown requests, pass them along to the hardware gateway to handle
   164	        else:
   165	            self.additional_banyan_messages(topic, payload)
   166	
 
```

Lines 133-168 implement the Banyan *incoming_message_processing* method. Received OneGPIO
commands are processed by this method.

Line 141-145 retrieves the *command* key string of the OneGPIO
incoming message. 

Line 149 checks to see if an optional *tag* key is in the message.

If it is, lines 149-158 process the tag. If the tag is not in the *tags_dictionary*,
the tag and its associated pin number are added to the dictionary.



Lines 160-165 checks to see if the value of the *command* key is within the command_dictionary.
If it is, the command method is called.

If it is not found, the *additional_banyan_messages* method is called.
 This allows you to add hardware-specific commands not found in the command dictionary easily.


```
   179	    def analog_write(self, topic, payload):
   180	        """
   181	        This method will pass any messages not handled by this class to the
   182	        specific gateway class. Must be overwritten by the hardware gateway class.
   183	        :param topic: message topic
   184	        :param payload: message payload
   185	        """
   186	        raise NotImplementedError
```

The remainder of the class is the set of command methods that need to be overwritten
in the derived class. Lines 179-186 are an illustration of the analog_write method. All the
other command methods follow a similar pattern (lines 170-378).
   
# Some Specific Command Examples

To illustrate the flexibility of using the OneGPIO specification, let's look 
at some sample OneGPIO command implementations. Both examples
presented below are from the Raspberry Pi Gateway.

## Adding A *Custom Spin* To The Command

When implementing a OneGPIO command,
you can go beyond a simple one to one mapping between the OneGPIO command and
the underlying GPIO API.

Let's look at *set_mode_digital_input* for the Raspberry Pi. The Raspberry Pi
Gateway uses the pigpio GPIO library. Of course, you can use
any GPIO library you wish to choose.

```
   def set_mode_digital_input(self, topic, payload):
        """
        This method sets a pin as digital input.
        :param topic: message topic
        :param payload: {"command": "set_mode_digital_input", "pin": “PIN”, "tag":”TAG” }
        """
        pin = payload['pin']
        entry = self.pins_dictionary[pin]
        entry['mode'] = self.DIGITAL_INPUT_MODE

        self.pi.set_glitch_filter(pin, 20000)
        self.pi.set_mode(pin, pigpio.INPUT)
        self.pi.set_pull_up_down(pin, pigpio.PUD_DOWN)

        self.pi.callback(pin, pigpio.EITHER_EDGE, self.input_callback)
```


The pin number is extracted from the OneGPIO payload. The pin mode is set within
 the *pins_dictionary* for the pin.

Next, it performs 4 *pigpio* functions.

* A glitch filter to debounce the pin.
* The pin mode is set to ***input***.
* The internal pull-up/pull-down resistor for the pin is set to ***pull-down***.
* A callback method is set. This method is called whenever there is a state change for the pin.

The OneGPIO Application Component has no knowledge of all of this underlying logic.
It merely sends the command to set the pin mode to digital input, and the OneGPIO Gateway
interprets the behavior for the specific target hardware.


## Adding Some More *Spin*

The Raspberry Pi GPIO does not directly support analog input. But
since you control the definition of a command, the gateway
can implement anything you choose, including using an external device to perform analog input.

Here we implement analog input for the Raspberry Pi by using a PFC8591
A/D converter.

```
    def set_mode_analog_input(self, topic, payload):
        """
        This method programs a PCF8591 AD/DA for analog input.
        :param topic: message topic
        :param payload: {"command": "set_mode_analog_input",
                         "pin": “PIN”, "tag":”TAG” }
        """

        # pin is used as channel number

        value = None
        i2c_handle = self.pi.i2c_open(1, 72, 0)
        pin = payload['pin']

        self.pi.i2c_write_byte_data(i2c_handle, 64 | (pin & 0x03), 0)
        time.sleep(0.1)
        for i in range(3):
            value = self.pi.i2c_read_byte(i2c_handle)

        self.pi.i2c_close(i2c_handle)

        # publish an analog input report
        payload = {'report': 'analog_input', 'pin': pin,
                   'value': value}
        self.publish_payload(payload, 'from_rpi_gateway')
``` 
The A/D device is i2c based and so this method implements the i2c communication.
The method retrieves the current value for one of the 4 channels supported by the
PCF8591 A/D converter and then publishes that value using a OneGPIO report message.

<br>
<br>
Copyright (C) 2017-2020 Alan Yorinks All Rights Reserved
