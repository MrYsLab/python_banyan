# The Python Banyan Framework

![](https://github.com/MrYsLab/python_banyan/blob/master/images/BanyanTree.png)


## Fast Publisher/Subscriber Data Transfers

* Streaming "sensor" data on a single Raspberry Pi 3 by continuously publishing 100000 messages.

* Results:
    * __Python Banyan 14.02 seconds__
    * Mosquitto MQTT 31.3 seconds

* Source code for tests can be found [here](https://github.com/MrYsLab/python_banyan/tree/master/python_banyan/performance_comparison)

## Now Python 2 and 3 compatible

## Transfer Numpy Matrices Quickly In A Single Payload

## Coming Soon - JavaScript, Ruby, Java versions allowing remote procedure calls and data transfers across all platforms



## [View the slides](https://drive.google.com/open?id=0B0adDMMjxksDbkNvTFFZTXYzWWc) from a recent talk describing using the Python Banyan Framework to control a Raspbery Pi robot.
![](https://github.com/MrYsLab/razmq/blob/master/documentation/images/razbot.png)

## Read [Python Banyan User's Guide](https://MrYsLab.github.io/python_banyan/) for details on using the framework:

## INSTALLATION INSTRUCTIONS


You have the option to install the Python Banyan framework alone or the framework plus all the examples.

To install the framework alone:


```

pip install python-banyan

or

sudo pip3 install python-banyan

```

To install the framework plus all the examples


```

pip install python-banyan[examples]

or

sudo pip3 install python-banyan[examples]

```

The example code is located in [its own repository](https://github.com/MrYsLab/python_banyan_examples),
 and may be downloaded there.

## WHAT IS PYTHON BANYAN?
A full User's Guide is available [here](https://MrYsLab.github.io/python_banyan/).

Python Banyan is a lightweight, reactive framework used to create flexible, non-blocking, event 
driven, 
asynchronous applications. It was designed primarily to implement physical computing applications for devices such as
 the Raspberry Pi and Arduino, 
but it is 
not limited to just that domain, and may be used to create application in any domain.

Most traditional physical computing libraries or frameworks use an *object oriented* model that results in a single, 
tightly coupled, monolithic executable image. Python Banyan uses an extension of the object oriented model, called 
the *component based* model. A component based application is comprised of a set of independent, loosely 
coupled 
modules. Functionality is easily added to a Python Banyan application, and in fact it may be added to a fully running
 system without the need to recompile or reboot.
 
 Because each module is a self contained entity, applications can be created with a set of modules that use 
 different 
 versions of Python, and in fact, you can even add modules written in other computer languages.
 
 In addition, the modules may be run on a single computer, or may be distributed across multiple computers running 
 different operating systems, without having to change a single line of code.

## *A Little More Detail*
The Python Banyan Framework consists of a single, simple base class. All Banyan compatible components inherit from 
this class. When a Banyan component is first invoked, it automatically connects to a common shared software backplane. 
All 
of the complexity of managing connections is hidden within and handled by the base class. All Banyan modules
exchange information with each another by sending or publishing user defined protocol messages via the backplane. All
 routing and message buffering is automatically handled by the Framework. Each 
Banyan 
component can
 "publish" messages, "subscribe" to receive specific messages or both publish and subscribe messages. A Banyan 
 component is not limited as to how many types of messages it may subscribe to.

 
 Because Banyan messages are not computer language specific, components written in other computer Languages, such as 
 JavaScript, can be used within a Python Banyan application. A simple JavaScript demo is provided in the 
 examples section below.
 
 Python Banyan takes full advantage of the <a href="http://zeromq.org/" target="_blank">ZeroMQ</a> 
  networking library that not only provides 
 connectivity, but in addition acts as a concurrency framework. All of this is handled transparently by the Python 
 Banyan base class. If your application requires additional concurrency support, you are free to choose whatever 
 works best for your application, such as a multi-threading or a Python asyncio approach. User defined messages are 
 prepared for transport across the network by wrapping them in the 
 <a href="http://msgpack.org/index.html" target="_blank">Message Pack format.</a> 
 
  The complexities of 
 MessagePack are handled transparently by the base class, both for transmitting and receiving messages.
 

### Here is what the [Python Banyan User's Guide](https://MrYsLab.github.io/python_banyan/) guide covers:

Chapter 1 is an introduction to developing with Python Banyan. An application tailored specifically for this purpose 
will be 
presented in detail.

In chapter 2, a demonstration of, and a discussion about creating physical computing components with Python Banyan.

To demonstrate Python Banyan's flexibility, applications will be built from Python 2 components, Python 3 components and even a JavaScript component, all cooperating and communicating with each other within a single Python Banyan application.

Python Banyan applications may be distributed across multiple computers, all without changing a single line of code. Using the components created in this guide, all of the components will first be launched to run on a Raspberry Pi, 
and then then the components will be re-distributed across a Linux Ubuntu PC, a Windows PC and the Raspberry Pi without having to change a single line of code.

In Chapter 3, we will add components to control an 8x8 bicolor LED matrix connected to a Raspberry Pi. A demonstration of using Python Banyan to control an i2c device will be presented.

If you need to control multiple i2c devices sharing the same i2c pins, Python Banyan provides the concurrency support for you to do so.

Chapter 4 discusses how to use Python's setup tools to convert a Banyan component into an executable file and have it 
automatically installed on the execution path.

This project was developed with [Pycharm](https://www.jetbrains.com/pycharm/) ![](https://github.com/MrYsLab/python_banyan/blob/master/images/icon_PyCharm.png)
