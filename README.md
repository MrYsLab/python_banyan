# The Python Banyan Framework

![](https://github.com/MrYsLab/python_banyan/blob/master/python_banyan/examples/raspberry_redbot/documentation/images/BanyanTree.png)

## WHAT IS PYTHON BANYAN?
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
 
 In addition, the modules may be run on a single computer, or may be distributed across muiltiple computers running 
 differnent operating systems, without having to change a single line of code.

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

To  understand how to develop with Python Banyan please refer to the user guide. 

THIS SITE IS UNDER CONSTRUCTION