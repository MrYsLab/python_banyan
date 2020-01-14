# Benchmarking Banyan and MQTT

MQTT is an excellent tool if used for what it is designed - that is, publishing messages across the greater Internet.
But when traffic is limited to within a given LAN, MQTT is highly inefficient.

We ran a simple benchmark comparing MQTT to Python Banyan.
For each framework, the benchmark consists of a publisher that publishes 100000 messages and a subscriber that receives those messages.
The total transfer time is calculated for each, and total latency between the publisher and subscriber is explored.

To view the benchmark code, click on these links:

* [MQTT subscriber](https://github.com/MrYsLab/python_banyan/blob/master/python_banyan/performance_comparison/mqsub.py),
* [MQTT publisher](https://github.com/MrYsLab/python_banyan/blob/master/python_banyan/performance_comparison/mqpub.py),
* [Python Banyan subscriber](https://github.com/MrYsLab/python_banyan/blob/master/python_banyan/performance_comparison/banyan_sub.py),
* [Python Banyan publisher](https://github.com/MrYsLab/python_banyan/blob/master/python_banyan/performance_comparison/banyan_pub.py).

## Testing Environment
All tests were run on Ubuntu Linux 18.10 on a computer using
an Intel Core i5-2500K CPU running at 3.30GHz.

Python 3.7.2 compiled with the --enable_optimizations flag set was used for both
tests.

Mosquitto version 1.4.15 and paho version 1.3.1 were used for the MQTT tests.

## Using MQTT


Here are the MQTT test results for the subscriber:
```
$ python3 mqsub.py
MQSUB Connected - Expecting 100000 Messages
Task completed on:  Wed Feb 13 17:27:25 2019
100000 Total messages received in 4.819453239440918 seconds.
```

And here are the results for the MQTT publisher:
```
$ python mqpub.py
MQPUB Connected - Sending 100000 messages
Task completed on:  Wed Feb 13 17:27:24 2019

```

We can see that it took a little over 4.18 seconds to send and receive the 100000 messages.

## Using Python Banyan



Here are the Banyan subscriber results:

```
$ python3 banyan_sub.py

************************************************************
Banyan Subscriber using Back Plane IP address: 192.168.2.189
Subscriber Port = 43125
Publisher  Port = 43124
Loop Time = 0.1 seconds
************************************************************
Expecting 100000 messages.
Task completed at:  Wed Feb 13 17:38:42 2019
100000 Total messages received in 1.695580244064331 seconds.
```

Here are the Banyan publisher results:

```
$ python3 banyan_pub.py

************************************************************
Banyan publisher using Back Plane IP address: 192.168.2.189
Subscriber Port = 43125
Publisher  Port = 43124
Loop Time = 0.1 seconds
************************************************************
Publishing 100000 messages.
Task completed at:  Wed Feb 13 17:38:42 2019

```

Looking at the results, Python Banyan was almost 2.5 times faster than the MQTT.
What is more interesting is the latency between the publishers' and subscribers' completions.
Looking at the time stamps reported, MQTT had a latency of 1 second, while Banyan had a latency of 0 seconds.

## Running the Benchmarks On A Raspberry Pi

The tests were also run on a Raspberry Pi 3 with Raspbian Stretch March 2018 release
updated and upgraded on February 14, 2019.
Python 3.6.4 was used for all tests.

Mosquitto version 1.4.15 and paho version 1.3.1 were used for the MQTT tests.

In this case, MQTT took a little over 36 seconds to complete and Banyan a little over 17.

Latency for MQTT was approximately 7 seconds and for Banyan, approximately 1 second. 

<br>
<br>
Copyright (C) 2017-2020 Alan Yorinks All Rights Reserved