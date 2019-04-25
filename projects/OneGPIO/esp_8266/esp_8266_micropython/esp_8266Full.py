import uerrno
import ujson
import utime
from machine import Pin, PWM, ADC, I2C, time_pulse_us
from utime import sleep_us


class Ultrasonic:
    # this code is based from this URL: https://www.stavros.io/tips/
    def __init__(self, t_pin, e_pin):
        """

        :param t_pin: Trigger Pin
        :param e_pin: Echo Pin
        """
        self.trigger = Pin(t_pin, Pin.OUT)
        self.trigger.value(0)
        self.echo = Pin(e_pin, Pin.IN)

    def distance_in_cm(self):
        self.trigger.value(1)
        sleep_us(10)
        self.trigger.value(0)
        try:
            time = time_pulse_us(self.echo, 1, 29000)
        except OSError:
            return None
        dist_in_cm = (time / 2.0) / 29
        return dist_in_cm


class Esp8266:
    """
    This class receives TCP/IP packets and processes
    commands to control an ESP8266 and sends reports
    over the TCP/IP link.
    """
    def __init__(self, socket, packet_len=96):
        """
        :param socket: connected TCP/IP socket - see main.py
        :param packet_len: A fixed packet length
        """
        # save the socket and packet length parameters
        self.socket = socket
        self.packet_len = packet_len

        # previous adc value
        self.last_adc = 0

        # differential between previous and current adc value
        # to trigger a report
        self.adc_diff_report = 0

        # adc object
        self.adc = None

        # i2c object
        self.i2c = None
        self.i2c_continuous = False

        # sonar object
        self.sonar = None

        # supported GPIO pins
        self.gpio_pins = [4, 5, 12, 13, 14, 15]

        # list of stepper motor pins
        self.stepper_pins = []

        # a list of pin objects to be used when reporting
        # back digital input pin changes
        self.input_pin_objects = [None] * 16

        # incoming command lookup table
        self.command_dictionary = {'analog_write': self.analog_write, 'digital_write': self.digital_write,
                                   'disable_analog_reporting': self.disable_analog_reporting,
                                   'disable_digital_reporting': self.disable_digital_reporting,
                                   'enable_analog_reporting': self.disable_analog_reporting,
                                   'enable_digital_reporting': self.disable_digital_reporting,
                                   'i2c_read': self.i2c_read, 'i2c_write': self.i2c_write, 'play_tone': self.play_tone,
                                   'pwm_write': self.pwm_write, 'servo_position': self.servo_position,
                                   'set_mode_analog_input': self.set_mode_analog_input,
                                   'set_mode_digital_input': self.set_mode_digital_input,
                                   'set_mode_digital_input_pullup': self.set_mode_digital_input_pullup,
                                   'set_mode_digital_output': self.set_mode_digital_output,
                                   'set_mode_i2c': self.set_mode_i2c, 'set_mode_pwm': self.set_mode_pwm,
                                   'set_mode_servo': self.set_mode_servo, 'set_mode_sonar': self.set_mode_sonar,
                                   'set_mode_stepper': self.set_mode_stepper, 'set_mode_tone': self.set_mode_tone,
                                   'stepper_write': self.stepper_write, }

        # digital input change callback message
        self.digital_input_cb_msg = {'report': 'digital_input', 'pin': 0, 'value': 0}

        # set the socket to non-blocking
        self.socket.setblocking(False)

        # output an id string in case we need it
        info = 'esp connected to ' + repr(self.socket)
        self.send_payload_to_gateway({'report': 'connected', 'info': info})

        # start the command processing loop
        self.get_next_command()

    def get_next_command(self):
        """
        Command processing loop
        """
        while True:
            try:
                # wait for all data to arrive for a packet
                # of packet_len
                payload = self.socket.recv(self.packet_len)
                pkt_len_received = len(payload)
                print(pkt_len_received)
                while pkt_len_received < self.packet_len:
                    wait_for = self.packet_len - pkt_len_received
                    short_packet = self.socket.recv(wait_for)
                    payload += short_packet
                    pkt_len_received += len(payload)
            except OSError:
                # this exception is expected because we set the
                # socket to non-blocking.

                # if we have an adc object, get the latest value and send report
                if self.adc:
                    adc_val = self.adc.read()
                    if abs(self.last_adc - adc_val) >= self.adc_diff_report:
                        self.send_payload_to_gateway({'report': 'analog_input', 'pin': 0, 'value': adc_val})
                        self.last_adc = adc_val
                # if sonar is enabled get next sample
                if self.sonar:
                    dist = self.sonar.distance_in_cm()
                    payload = {'report': 'sonar_data', 'value': dist}
                    self.send_payload_to_gateway(payload)
                    utime.sleep(.05)
                continue
            try:
                # decode the payload
                payload = ujson.loads(payload)
            except ValueError:
                self.send_payload_to_gateway(
                    {'error': 'json value error - data: {} length {}'.format(payload, len(payload))})
                self.socket.close()
                break

            # get the payload command and look it up in the
            # command dictionary to execute the command processing
            command = payload['command']
            if command in self.command_dictionary.keys():
                self.command_dictionary[command](payload)
            else:
                self.additional_banyan_messages(payload)

    def additional_banyan_messages(self, payload):
        """
        For future development
        :param payload:
        :return:
        """
        raise NotImplementedError

    def analog_write(self, payload):
        """
        Not implemented - placeholder
        :param payload:
        :return:
        """
        raise NotImplementedError

    def digital_write(self, payload):
        """
        Write to a digital gpio pin
        :param payload:
        :return:
        """
        pin = payload['pin']
        mode = Pin.OUT
        if 'drain' in payload:
            if not payload['drain']:
                mode = Pin.OPEN_DRAIN
        pin_object = Pin(pin, mode)
        pwm = PWM(pin_object)
        pwm.deinit()
        Pin(pin, mode, value=payload['value'])
        self.input_pin_objects[pin] = None

    def disable_analog_reporting(self, payload):
        """
        disable analog reporting
        :param payload:
        :return:
        """
        self.adc = None

    def disable_digital_reporting(self, payload):
        """
        disable digital reporting for the pin
        :param payload:
        :return:
        """
        self.input_pin_objects[payload['pin']] = None

    def enable_analog_reporting(self, payload):
        """
        Will be auto enabled when set_mode_analog_input
        is called.
        :param payload:
        :return:
        """
        raise NotImplementedError

    def enable_digital_reporting(self, payload):
        """
        Will be auto enabled when set_mode_digital_input is called
        :param payload:
        :return:
        """
        raise NotImplementedError

    def i2c_read(self, payload):
        """
        Establish an i2c object if not already establed and
        read from the device.
        :param payload:
        :return:
        """
        if not self.i2c:
            self.i2c = I2C(scl=Pin(5), sda=Pin(4), freq=100000)
        try:
            data = self.i2c.readfrom_mem(payload['addr'], payload['register'], payload['number_of_bytes'])
        except TypeError:
            print('read')
            raise
        try:
            data = list(data)
        except TypeError:
            print(payload, data)
            raise
        payload = {'report': 'i2c_data', 'value': data}
        self.send_payload_to_gateway(payload)

    def i2c_write(self, payload):
        """
        Establish an i2c object if not already establed and
        write to the device.
        :param payload:
        :return:
        """
        if not self.i2c:
            self.i2c = I2C(scl=Pin(5), sda=Pin(4), freq=100000)
        self.i2c.writeto(payload['addr'], bytearray(payload['data']))

    def play_tone(self, payload):
        """
        Play a tone on the specified pin
        :param payload:
        :return:
        """
        beeper = PWM(Pin(payload['pin']), freq=payload['freq'], duty=512)
        utime.sleep_ms(payload['duration'])
        beeper.deinit()

    def pwm_write(self, payload):
        """
        Write a value to a PWM pin
        :param payload:
        :return:
        """
        PWM(Pin(payload['pin']), freq=500, duty=payload['value'])

    def servo_position(self, payload):
        """
        Set the servo position in degrees
        :param payload:
        :return:
        """
        position = 30 + int((payload['position'] * 0.5))
        servo = PWM(Pin(payload['pin']), freq=50, duty=position)
        utime.sleep_ms(300)
        servo.deinit()

    def set_mode_analog_input(self, payload):
        """
        create an adc object
        :param payload:
        :return:
        """

        if 'change_diff' in payload:
            self.adc_diff_report = payload['change_diff']
        self.adc = ADC(0)

    def digital_input_callback(self, p):
        """
        digital input pins use irqs. This is the callback
        method to send the value change to the tcp/ip client.
        :param p: Pin
        :return:
        """
        # find the Pin object to retrieve the data
        for index, item in enumerate(self.input_pin_objects):
            if p == item:
                self.digital_input_cb_msg['pin'] = index
                self.digital_input_cb_msg['value'] = p.value()
                self.send_payload_to_gateway(self.digital_input_cb_msg)

    def set_mode_digital_input(self, payload):
        """
        Set a pin as a digital input with pull_up and
        enable interrupts for a change on either edge.
        :param payload:
        :return:
        """
        pin = payload['pin']
        pin_in = Pin(pin, Pin.IN, Pin.PULL_UP)
        pin_in.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self.digital_input_callback)
        self.input_pin_objects[pin] = pin_in

    def set_mode_digital_input_pullup(self, payload):
        """
        Place holder
        :param payload:
        :return:
        """
        raise NotImplementedError

    def set_mode_digital_output(self, payload):
        """
        Set pin as a digtal output
        :param payload:
        :return:
        """
        pin = payload['pin']
        mode = Pin.OUT
        if 'drain' in payload:
            if not payload['drain']:
                mode = Pin.OPEN_DRAIN
        Pin(pin, mode, value=payload['value'])

    def set_mode_i2c(self, payload):
        """
        Placeholder
        :param payload:
        :return:
        """
        pass

    def set_mode_pwm(self, payload):
        """
        Placeholder
        :param payload:
        :return:
        """
        raise NotImplementedError

    def set_mode_servo(self, payload):
        """
        Placeholder
        :param payload:
        :return:
        """
        pass

    def set_mode_sonar(self, payload):
        """
        Establish a sonar object.
        Readings are performed in get_next_command
        :param payload:
        :return:
        """
        if not self.sonar:
            self.sonar = Ultrasonic(5, 4)

    def set_mode_stepper(self, payload):
        """
        Get the list of stepper pins
        :param payload:
        :return:
        """
        print('set mode stepper')
        self.stepper_pins = payload['pins']

    def set_mode_tone(self, payload):
        """
        Placeholder
        :param payload:
        :return:
        """
        pass

    def digital_read(self, payload):
        """
        Placeholder - irqs automatically report
        :param payload:
        :return:
        """
        raise NotImplementedError

    def stepper_write(self, payload):
        """
        Move stepper specified number of steps
        :param payload:
        :return:
        """
        print('stepper write')
        d1 = Pin(self.stepper_pins[0], Pin.OUT)
        d2 = Pin(self.stepper_pins[1], Pin.OUT)
        d3 = Pin(self.stepper_pins[2], Pin.OUT)
        d4 = Pin(self.stepper_pins[3], Pin.OUT)
        number_of_steps = payload['number_of_steps']
        if number_of_steps > 0:
            for i in range(abs(number_of_steps)):
                d1.value(1)
                utime.sleep_ms(5)
                d1.value(0)
                d2.value(1)
                utime.sleep_ms(5)
                d2.value(0)
                d3.value(1)
                utime.sleep_ms(5)
                d3.value(0)
                d4.value(1)
                i += 1
                utime.sleep_ms(5)
                d4.value(0)
        else:
            for i in range(abs(number_of_steps)):
                d4.value(1)
                utime.sleep_ms(5)
                d4.value(0)
                d3.value(1)
                utime.sleep_ms(5)
                d3.value(0)
                d2.value(1)
                utime.sleep_ms(5)
                d2.value(0)
                d1.value(1)
                i += 1
                utime.sleep_ms(5)
                d1.value(0)

    def send_payload_to_gateway(self, payload):
        """
        send a payload back to the gateway.
        :param payload:
        :return:
        """
        payload = ujson.dumps(payload)
        payload = '{:96}'.format(payload).encode('utf-8')
        try:
            self.socket.sendall(payload)
        except OSError as exc:
            if exc.args[0] == uerrno.EAGAIN:
                pass
