# Running The Demos

There are two demos available. Currently, data can only be sent in one 
direction at a time since I have not figured out how to perform concurrency in 
MicroPython.  The threading 
library is said to be experimental. However, I did locate [this code](https://github.com/fadushin/esp8266/blob/790958fa332592c80a0f81f25cdaa9513d596f64/micropython/uhttpd/uhttpd/__init__.py#L354) which may solve 
the concurrency issue. I have yet to have a chance to see if the code works.

## Generating Messages To The Local Simulated Server
Here are the steps used:

1. Start the backplane.
2. Start the [messages_from_pico.py](https://github.com/MrYsLab/python_banyan/blob/tcp_gateway/python_banyan/utils/tcp_gateway/pico_micropython_scripts/messages_from_pico.py) MicroPython script.
3. Start [sim_messages_from_pico.py](https://github.com/MrYsLab/python_banyan/blob/tcp_gateway/python_banyan/utils/tcp_gateway/simulated_local_station/sim_messages_from_pico.py)
4. Start the [tcp_gateway.py](https://github.com/MrYsLab/python_banyan/blob/tcp_gateway/python_banyan/utils/tcp_gateway/tcp_gateway.py)

You should see the messages if you look at the console window for sim_messages_from_pico.py.

**Important Note**: There is a 0.5 delay in the MicroPython script. If the delay is 
shortened beyond that, exceptions are thrown. I am unsure of the cause.

## Generating Messages To The Pico
1. Start the backplane.
2. Start the [messages_to_pico.py](https://github.com/MrYsLab/python_banyan/blob/tcp_gateway/python_banyan/utils/tcp_gateway/pico_micropython_scripts/messages_to_pico.py) MicroPython script.
3. Start the [tcp_gateway.py](https://github.com/MrYsLab/python_banyan/blob/tcp_gateway/python_banyan/utils/tcp_gateway/tcp_gateway.py)
4. Start the [sim_messages_to_pico.py](https://github.com/MrYsLab/python_banyan/blob/tcp_gateway/python_banyan/utils/tcp_gateway/simulated_local_station/sim_messages_to_pico.py) script.

Check the Thonny shell for incoming messages.