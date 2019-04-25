import uerrno
import ujson
import utime
from machine import Pin,PWM,ADC,I2C,time_pulse_us
from utime import sleep_us
class Ultrasonic:
 def __init__(self,t_pin,e_pin):
  self.trigger=Pin(t_pin,Pin.OUT)
  self.trigger.value(0)
  self.echo=Pin(e_pin,Pin.IN)
 def distance_in_cm(self):
  self.trigger.value(1)
  sleep_us(10)
  self.trigger.value(0)
  try:
   time=time_pulse_us(self.echo,1,29000)
  except OSError:
   return None
  dist_in_cm=(time/2.0)/29
  return dist_in_cm
class Esp8266:
 def __init__(self,socket,packet_len=96):
  self.socket=socket
  self.packet_len=packet_len
  self.last_adc=0
  self.adc_diff_report=0
  self.adc=None
  self.i2c=None
  self.i2c_continuous=False
  self.sonar=None
  self.gpio_pins=[4,5,12,13,14,15]
  self.stepper_pins=[]
  self.input_pin_objects=[None]*16
  self.command_dictionary={'analog_write':self.analog_write,'digital_write':self.digital_write,'disable_analog_reporting':self.disable_analog_reporting,'disable_digital_reporting':self.disable_digital_reporting,'enable_analog_reporting':self.disable_analog_reporting,'enable_digital_reporting':self.disable_digital_reporting,'i2c_read':self.i2c_read,'i2c_write':self.i2c_write,'play_tone':self.play_tone,'pwm_write':self.pwm_write,'servo_position':self.servo_position,'set_mode_analog_input':self.set_mode_analog_input,'set_mode_digital_input':self.set_mode_digital_input,'set_mode_digital_input_pullup':self.set_mode_digital_input_pullup,'set_mode_digital_output':self.set_mode_digital_output,'set_mode_i2c':self.set_mode_i2c,'set_mode_pwm':self.set_mode_pwm,'set_mode_servo':self.set_mode_servo,'set_mode_sonar':self.set_mode_sonar,'set_mode_stepper':self.set_mode_stepper,'set_mode_tone':self.set_mode_tone,'stepper_write':self.stepper_write,}
  self.digital_input_cb_msg={'report':'digital_input','pin':0,'value':0}
  self.socket.setblocking(False)
  info='esp connected to '+repr(self.socket)
  self.send_payload_to_gateway({'report':'connected','info':info})
  self.get_next_command()
 def get_next_command(self):
  while True:
   try:
    payload=self.socket.recv(self.packet_len)
    pkt_len_received=len(payload)
    print(pkt_len_received)
    while pkt_len_received<self.packet_len:
     wait_for=self.packet_len-pkt_len_received
     short_packet=self.socket.recv(wait_for)
     payload+=short_packet
     pkt_len_received+=len(payload)
   except OSError:
    if self.adc:
     adc_val=self.adc.read()
     if abs(self.last_adc-adc_val)>=self.adc_diff_report:
      self.send_payload_to_gateway({'report':'analog_input','pin':0,'value':adc_val})
      self.last_adc=adc_val
    if self.sonar:
     dist=self.sonar.distance_in_cm()
     payload={'report':'sonar_data','value':dist}
     self.send_payload_to_gateway(payload)
     utime.sleep(.05)
    continue
   try:
    payload=ujson.loads(payload)
   except ValueError:
    self.send_payload_to_gateway({'error':'json value error - data: {} length {}'.format(payload,len(payload))})
    self.socket.close()
    break
   command=payload['command']
   if command in self.command_dictionary.keys():
    self.command_dictionary[command](payload)
   else:
    self.additional_banyan_messages(payload)
 def additional_banyan_messages(self,payload):
  raise NotImplementedError
 def analog_write(self,payload):
  raise NotImplementedError
 def digital_write(self,payload):
  pin=payload['pin']
  mode=Pin.OUT
  if 'drain' in payload:
   if not payload['drain']:
    mode=Pin.OPEN_DRAIN
  pin_object=Pin(pin,mode)
  pwm=PWM(pin_object)
  pwm.deinit()
  Pin(pin,mode,value=payload['value'])
  self.input_pin_objects[pin]=None
 def disable_analog_reporting(self,payload):
  self.adc=None
 def disable_digital_reporting(self,payload):
  self.input_pin_objects[payload['pin']]=None
 def enable_analog_reporting(self,payload):
  raise NotImplementedError
 def enable_digital_reporting(self,payload):
  raise NotImplementedError
 def i2c_read(self,payload):
  if not self.i2c:
   self.i2c=I2C(scl=Pin(5),sda=Pin(4),freq=100000)
  try:
   data=self.i2c.readfrom_mem(payload['addr'],payload['register'],payload['number_of_bytes'])
  except TypeError:
   print('read')
   raise
  try:
   data=list(data)
  except TypeError:
   print(payload,data)
   raise
  payload={'report':'i2c_data','value':data}
  self.send_payload_to_gateway(payload)
 def i2c_write(self,payload):
  if not self.i2c:
   self.i2c=I2C(scl=Pin(5),sda=Pin(4),freq=100000)
  self.i2c.writeto(payload['addr'],bytearray(payload['data']))
 def play_tone(self,payload):
  beeper=PWM(Pin(payload['pin']),freq=payload['freq'],duty=512)
  utime.sleep_ms(payload['duration'])
  beeper.deinit()
 def pwm_write(self,payload):
  PWM(Pin(payload['pin']),freq=500,duty=payload['value'])
 def servo_position(self,payload):
  position=30+int((payload['position']*0.5))
  servo=PWM(Pin(payload['pin']),freq=50,duty=position)
  utime.sleep_ms(300)
  servo.deinit()
 def set_mode_analog_input(self,payload):
  if 'change_diff' in payload:
   self.adc_diff_report=payload['change_diff']
  self.adc=ADC(0)
 def digital_input_callback(self,p):
  print(p)
  for index,item in enumerate(self.input_pin_objects):
   if p==item:
    self.digital_input_cb_msg['pin']=index
    self.digital_input_cb_msg['value']=p.value()
    self.send_payload_to_gateway(self.digital_input_cb_msg)
 def set_mode_digital_input(self,payload):
  pin=payload['pin']
  pin_in=Pin(pin,Pin.IN,Pin.PULL_UP)
  pin_in.irq(trigger=Pin.IRQ_RISING|Pin.IRQ_FALLING,handler=self.digital_input_callback)
  self.input_pin_objects[pin]=pin_in
 def set_mode_digital_input_pullup(self,payload):
  raise NotImplementedError
 def set_mode_digital_output(self,payload):
  pin=payload['pin']
  mode=Pin.OUT
  if 'drain' in payload:
   if not payload['drain']:
    mode=Pin.OPEN_DRAIN
  Pin(pin,mode,value=payload['value'])
 def set_mode_i2c(self,payload):
  pass
 def set_mode_pwm(self,payload):
  raise NotImplementedError
 def set_mode_servo(self,payload):
  pass
 def set_mode_sonar(self,payload):
  if not self.sonar:
   self.sonar=Ultrasonic(payload['trigger'],payload['echo'])
 def set_mode_stepper(self,payload):
  self.stepper_pins=payload['pins']
 def set_mode_tone(self,payload):
  pass
 def digital_read(self,payload):
  raise NotImplementedError
 def stepper_write(self,payload):
  d1=Pin(self.stepper_pins[0],Pin.OUT)
  d2=Pin(self.stepper_pins[1],Pin.OUT)
  d3=Pin(self.stepper_pins[2],Pin.OUT)
  d4=Pin(self.stepper_pins[3],Pin.OUT)
  number_of_steps=payload['number_of_steps']
  if number_of_steps>0:
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
    i+=1
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
    i+=1
    utime.sleep_ms(5)
    d1.value(0)
 def send_payload_to_gateway(self,payload):
  payload=ujson.dumps(payload)
  payload='{:96}'.format(payload).encode('utf-8')
  try:
   self.socket.sendall(payload)
  except OSError as exc:
   if exc.args[0]==uerrno.EAGAIN:
    pass
# Created by pyminifier (https://github.com/liftoff/pyminifier)
