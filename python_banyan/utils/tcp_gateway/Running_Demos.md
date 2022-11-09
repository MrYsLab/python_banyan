# Running The Demos

There are two demos available. Currently, data can only be sent in one direction at time,
since I have not figured out how to perform concurrency in MicroPython. The threading 
library is said to be experimental. I did manage to locate [this code](https://github.com/fadushin/esp8266/blob/790958fa332592c80a0f81f25cdaa9513d596f64/micropython/uhttpd/uhttpd/__init__.py#L354) which may solve 
the concurrency issue. I have not had a chance to see if the code actually works.

## Generating Messages To The Local Simulated Server
Here are the steps used:

1. Start the backplane.
2. Start the tcp_gateway
3. Start messages_to_pico.py

Look at the 

## Generating Messages From The Pico