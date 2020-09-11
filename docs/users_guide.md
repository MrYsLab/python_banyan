

</p>
<p align="center">
  <span style="color:#990033; font-family:Georgia; font-size:4em;">The Python Banyan</span>
</p>
<p align="center">
<span style="color:#990033; font-family:Georgia; font-size:4em;">User's Guide</span>
</p>



-------------------------------------------------

# What is Python Banyan?
Python Banyan is a lightweight, [reactive](https://gist.github.com/staltz/868e7e9bc2a7b8c1f754) framework used to
create [flexible](http://ptgmedia.pearsoncmg.com/images/9780134602417/samplepages/9780134602417.pdf), [non-blocking, event-driven,
asynchronous](https://www.allthingsdistributed.com/historical/archives/000486.html) applications.
It was designed primarily to aid in implementing real-time physical computing applications
 for devices such as
 the Raspberry Pi, ESP8266,  and Arduino.
Still, it may easily be applied to projects outside of the physical programming domain.

Banyan uses a [publish/subscribe](https://en.wikipedia.org/wiki/Publish%E2%80%93subscribe_pattern)
 model similar to [MQTT](https://en.wikipedia.org/wiki/MQTT) but is much faster than MQTT in
 real-time control and data monitoring applications.
 A [benchmark comparison](benchmark/#benchmark) of Banyan
and MQTT is provided later in this guide to illustrate Banyan's efficiency.
If your application requires connectivity to an MQTT broker, a [Gateway](example10) is provided.

Most traditional physical computing libraries or frameworks use an *object-oriented* model
that yields a single,
tightly coupled, monolithic executable image. Python Banyan uses an extension of the object-oriented model, called
the *[component-based](https://en.wikipedia.org/wiki/Component-based_software_engineering) [service-oriented architectural](https://en.wikipedia.org/wiki/Service-oriented_architecture)*
model. A ***component-based*** application consists of a set of independent, loosely
coupled ***components***. For python-banyan, these components communicate with one another through a set
of platform-independent, user-defined protocol messages transmitted over a TCP network.

A Banyan application is composed of a set of *components* running concurrently as separate processes.
These *components* can be developed using a single language platform such as Python, or developed using any of the other Banyan frameworks.
There are versions of Banyan available for [JavaScript](https://github.com/MrYsLab/js-banyan), [Ruby](https://github.com/MrYsLab/rb_banyan),
 and [Java](https://github.com/MrYsLab/javabanyan). Components developed using dissimilar languages can be combined
 without modification to form a single, cohesive application.

Banyan uses a central message distribution mechanism called the ***Backplane***. When first starting a Banyan application,
the *Backplane* is brought on-line, followed by
the application's components.
At startup, each
 *component* automatically
"plugs" itself into the *Backplane* establishing a TCP/IP communication channel between itself and the Backplane.

After communication is established, components may publish messages *to* the Backplane, receive messages from other components, or both
publish and receive messages. A major feature of Python Banyan
is that it can incorporate [Numpy](http://www.numpy.org/) data into a protocol message
 seamlessly and effortlessly.

Without modification, a Banyan application's components can run on a single computer or distributed across multiple computers.
These configurations will be [demonstrated later](example3/) on in this document.


## *A Little More Detail About Python Banyan*

### Banyan Base Classes
All Banyan components are created by inheriting from one of the supplied Banyan base classes.
 The base class methods are overridden as needed to
 support the component's specific needs.

The base classes act as a wrapper for the [ZeroMQ](http://zeromq.org/) embeddable networking library that has been configured
 to operate in a Publish/Subscribe networking pattern.
Also, the base class encodes and decodes protocol messages for efficient network transmission,
using [MessagePack](https://msgpack.org/index.html).

### Banyan Protocol Messages

Banyan protocol messages consist of 2 parts, a "topic" and a "payload."

#### The Topic String

A message topic consists of a simple string. For a component to receive messages
with a set of given topics, a component
subscribes to receive messages for each topic. A subscribing component receives all messages published
containing the desired topic.

##### Prefix Matching
When a message is received, the topic is compared to the subscribed topic. If it matches,
the message is placed on the component's receive queue. Any topic that begins with the subscribed topic string
is considered a match even if the received message topic contains additional text.
 For example, if you subscribe to the topic **"abcd,"** and a message is received
with a topic of **"abcde,"** the "abcde" message will be placed on the receive queue. Any messages with topics
that begin with the subscribed topic string are considered a match even though the topic may contain additional text.

#### The Message Payload

 Message payloads consist of a Python dictionary type structure, containing one or more name/value items.
 By utilizing a dictionary, message data can be quickly de-referenced and processed.

 Because Banyan messages are not computer language-specific, components written in other computer languages, such as
 JavaScript, can be used within a Python Banyan application. A simple [JavaScript demo](example4/) is provided as one
 of the included examples.

## Where Is Python Banyan Being Used?
Commercially, Python Banyan has been chosen by Palace Games in San Francisco to monitor and control
their [Palace Games Edison Room](https://palace-games.com/edison-escape-room/).
 The Edison room contains several hundred sensors and actuators. Banyan helps tie all the devices
and their associated micro-controllers together, allowing them to
communicate quickly and transparently. Banyan supports data transfers of Numpy data,
which the Edison
room uses to model their data efficiently. You can read about Palace Games on the
[Raspberry Pi Blog](https://www.raspberrypi.org/blog/raspberry-pi-escape-room/).

Banyan is also being used in numerous physical computing projects utilizing the Raspberry Pi, Arduino, and ESP8266.
An earlier version of Python Banyan, called [razmq](https://github.com/MrYsLab/razmq), was used to control a Raspberry Pi robot.

## Banyan Application Design

When designing a Banyan Component, it is good practice to keep it as small as
possible. By limiting a component to a small area of concern, testing is greatly
simplified, and the potential for component reuse increases.

## Some Design Guidelines

* A component should subscribe to the minimal number of message topics as possible.

* Keep messages as short as possible.

* Limit the component to its task at hand. For example, if you wish to log application activity,
create a specific logging component. All other components can take advantage of this logging facility
in a consistent fashion. It also offloads logging I/O from the main component, promoting higher performance
for the system as a whole.

<br>
<br>
Copyright (C) 2017-2020 Alan Yorinks All Rights Reserved



