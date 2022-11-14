# Running The Demos

A demo is available to run data end-to-end in both directions.

The TCP Gateway will continually attempt to connect to the Pico.

## Steps
Here are the steps used:

1. Start the backplane.
2. Start the [tcp_gateway.py](https://github.com/MrYsLab/python_banyan/blob/tcp_gateway/python_banyan/utils/tcp_gateway/tcp_gateway.py)
3. Load and start the [select.py](https://github.com/MrYsLab/python_banyan/blob/master/python_banyan/utils/tcp_gateway/pico_micropython_scripts/select.py) MicroPython script on the Raspberry Pi Pico W
4. Start [sim_echo_client.py](https://github.com/MrYsLab/python_banyan/blob/master/python_banyan/utils/tcp_gateway/simulated_local_station/sim_echo_client.py)

The messages appear in the sim_echo_client console and on the MicroPython 
Thonny shell.
