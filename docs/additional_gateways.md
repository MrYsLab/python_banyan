## MQTT Gateway

If you need to interconnect with MQTT, a Banyan MQTT Gateway has been provided.
This gateway has been documented [here.](../example10/)

## WebSocket Gateway

The OneGPIO Demo Examples include Web pages to control an
Arduino, ESP-8266, and Raspberry Pi. The WebPages publish
commands via a WebSocket connection. This gateway translates
the WebSocket command messages to OneGPIO command messages. It also translates OneGPIO
reporter messages to WebSocket reporter messages to allow reports
to be displayed on the Web page.

The WebSocket IP address that this component uses is *localhost* since it is intended to be
used in conjunction with a Web Browser running on the same computer as the Gateway.
The WebSocket IP port is fixed to a value of 9000. If you need to, you can modify the
supplied code to allow the user to modify these values on the command line.

***IMPORTANT NOTE***

The WebSocket Gateway utilizes a Python asyncio WebSocket library.
It requires that Python 3.7 or higher be used.


## A Quick Overview Of The WsGateway Component

The Banyan WebSocket Gateway is an executable Banyan component. It follows the
command line patterns exposed in the Banyan User's Guide:

```
usage: ws_gateway.py [-h]
                     [-b BACK_PLANE_IP_ADDRESS]
                     [-m SUBSCRIPTION_LIST [SUBSCRIPTION_LIST ...]]
                     [-n PROCESS_NAME] [-p PUBLISHER_PORT]
                     [-s SUBSCRIBER_PORT]

optional arguments:
  -h, --help            show this help message and exit
  -b BACK_PLANE_IP_ADDRESS
                        None or IP address used by Back Plane
  -m SUBSCRIPTION_LIST [SUBSCRIPTION_LIST ...]
                        A space delimited list of topics
  -n PROCESS_NAME       Set process name in banner
  -p PUBLISHER_PORT     Publisher IP port
  -s SUBSCRIBER_PORT    Subscriber IP port
```

### A Quick Look At The WsGateway Internals

Once again, a block of code will be presented, followed by a discussion.

```
    24	import argparse
    25	import asyncio
    26	import datetime
    27	import json
    28	import signal
    29	import sys
    30	
    31	import websockets
    32	
    33	from python_banyan.banyan_base_aio import BanyanBaseAIO
    34	
    35	
    36	class WsGateway(BanyanBaseAIO):
    37	    """
    38	    This class is a gateway between a websocket client and the
    39	    Banyan network.
    40	
    41	    NOTE: This class requires Python 3.7 or above.
    42	
    43	    It implements a websocket server. A websocket client, upon
    44	    connection, must send an id message e.g.: {"id": "to_arduino"}.
    45	
    46	    The id will be used as the topic to publish data to the banyan
    47	    network.
    48	    """
    49	
    50	    def __init__(self, *subscription_list, back_plane_ip_address=None,
    51	                 subscriber_port='43125',
    52	                 publisher_port='43124', process_name='WebSocketGateway',
    53	                 event_loop=None):
    54	        """
    55	        These are all the normal base class parameters
    56	        :param subscription_list:
    57	        :param back_plane_ip_address:
    58	        :param subscriber_port:
    59	        :param publisher_port:
    60	        :param process_name:
    61	        :param event_loop:
    62	        """
    63	
    64	        # initialize the base class
    65	        super(WsGateway, self).__init__(subscriber_list=subscription_list,
    66	                                        back_plane_ip_address=back_plane_ip_address,
    67	                                        subscriber_port=subscriber_port,
    68	                                        publisher_port=publisher_port,
    69	                                        process_name=process_name,
    70	                                        event_loop=event_loop)
    71	        # save the event loop
    72	        self.event_loop = event_loop
    73	
    74	        # array of active sockets
    75	        self.active_sockets = []
    76	
    77	        try:
    78	            # start the websocket server and call the main task, wsg
    79	            self.start_server = websockets.serve(self.wsg, '127.0.0.1', 9000)
    80	            self.event_loop.run_until_complete(self.start_server)
    81	            self.event_loop.run_forever()
    82	        except (websockets.exceptions.ConnectionClosed,
    83	                RuntimeError,
    84	                KeyboardInterrupt):
    85	            sys.exit()
```

In this section of code, the necessary packages are imported and we
define the WsGateway class, which is derived from BanyanBaseAIO.

Being an asyncio based class, one of the parameters 
that may be passed to this class is an asyncio event loop. Usually,
the default event loop is used, but you can supply your own event loop
if you need to.

This component implements a WebSocket server that permits connections to multiple
WebSocket clients. An empty array, *self.active_sockets* is created
on line 75 to store a record for each connected socket.

Lines 79-85 start the WebSocket server. When a client connects
to the WebSocket server, the *wsg* method is called
on line 79.

For information about the WebSocket server, please go to this
[link](https://github.com/aaugustin/websockets).

```
	87    async def wsg(self, websocket, path):
    88	        """
    89	        This method handles connections and will be used to send
    90	        messages to the client
    91	        :param websocket: websocket for connected client
    92	        :param path: required, but unused
    93	        :return:
    94	        """
    95	        # start up banyan
    96	        await self.begin()
    97	
    98	        # wait for a connection
    99	        data = await websocket.recv()
   100	
   101	        # expecting an id string from client
   102	        data = json.loads(data)
   103	
   104	        # if id field not present then raise an exception
   105	        try:
   106	            id_string = data['id']
   107	        except KeyError:
   108	            print('Client did not provide an ID string')
   109	            raise
   110	
   111	        # create a subscriber string from the id
   112	        subscriber_string = id_string.replace('to', 'from')
   113	
   114	        # subscribe to that topic
   115	        await self.set_subscriber_topic(subscriber_string)
   116	
   117	        # add an entry into the active_sockets table
   118	        entry = {websocket: 'to_banyan_topic', subscriber_string: websocket}
   119	        self.active_sockets.append(entry)
   120	
   121	        # create a task to receive messages from the client
   122	        await asyncio.create_task(self.receive_data(websocket, data['id']))
```

The *wsg* method is called when a WebSocket client connects to the WebSocket Gateway.
Line 96 establishes the zeromq subscriber and publisher sockets for this component
 as well as providing a connection to the Banyan Backplane.
 
Line 99 waits to receive initial identification data from a WebSocket client. This data 
is used to create a subscription topic for the WebSocket Gateway. 

Using the [Arduino Demo Station Page](https://github.com/MrYsLab/python_banyan/blob/master/projects/OneGPIO/arduino_uno/arduino.html) 
as an example, the ID string sent as a WebSocket message from the Web page is "to_arduino_gateway." This
ID string is used to create subscription topic strings that the WebSocket Gateway
 uses for its operation. This is accomplished on lines 112-115.

An entry for the socket connection is created and added to the active_websockets array.
The entry is used to dispatch messages to the correct WebSocket during data transfer. This is
accomplished on lines 118-119.

Line 122 creates an asyncio task to continuously receive WebSocket messages from any connected WebSocket client.
 This task passes these messages to the *receive_data* method
for further processing.

```
   124	    async def receive_data(self, websocket, publisher_topic):
   125	        """
   126	        This method processes a received WebSocket command message
   127	        and translates it to a Banyan command message.
   128	        :param websocket: The currently active websocket
   129	        :param publisher_topic: The publishing topic
   130	        """
   131	        while True:
   132	            try:
   133	                data = await websocket.recv()
   134	                data = json.loads(data)
   135	            except (websockets.exceptions.ConnectionClosed, TypeError):
   136	                # remove the entry from active_sockets
   137	                # using a list comprehension
   138	                self.active_sockets = [entry for entry in self.active_sockets if websocket not in entry]
   139	                break
   140	
   141	            await self.publish_payload(data, publisher_topic)
```

The *receive_data* method processes WebSocket messages sent from the WebSocket client.
The message is in the form of a JSON message and it is decoded on line 134. The message
is then published as a Banyan OneGPIO message on line 141. 

```
   143	    async def incoming_message_processing(self, topic, payload):
   144	        """
   145	        This method converts the incoming messages to ws messages
   146	        and sends them to the ws client
   147	
   148	        :param topic: Message Topic string.
   149	
   150	        :param payload: Message Data.
   151	        """
   152	        if 'timestamp' in payload:
   153	            timestamp = datetime.datetime.fromtimestamp(payload['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
   154	            payload['timestamp'] = timestamp
   155	
   156	        ws_data = json.dumps(payload)
   157	
   158	        # find the websocket of interest by looking for the topic in
   159	        # active_sockets
   160	        for socket in self.active_sockets:
   161	            if topic in socket.keys():
   162	                pub_socket = socket[topic]
   163	                await pub_socket.send(ws_data)
   164	                # print(ws_data)
```

The *incoming_message_processing* method is the standard Banyan message
processing method, overwritten to process OneGPIO messages received from
the target hardware in the form of a report message. Using the topic
of the message as a key, it looks up the associated WebSocket in the 
*active_sockets* array and publishes the message to the correct WebSocket.

On lines 152-154, if the gateway provided a timestamp, the timestamp
 is formatted and appended to the report message.
Line 156 encodes the message as a JSON message and sends the message
to the WebSocket client on line 163.

```
   167	def ws_gateway():
   168	    # allow user to bypass the IP address auto-discovery. This is necessary if the component resides on a computer
   169	    # other than the computing running the backplane.
   170	
   171	    parser = argparse.ArgumentParser()
   172	    parser.add_argument("-b", dest="back_plane_ip_address", default="None",
   173	                        help="None or IP address used by Back Plane")
   174	    # allow the user to specify a name for the component and have it shown on the console banner.
   175	    # modify the default process name to one you wish to see on the banner.
   176	    # change the default in the derived class to set the name
   177	    parser.add_argument("-m", dest="subscription_list", default="from_arduino_gateway, "
   178	                                                                "from_ESP8266_gateway, "
   179	                                                                "from_rpi_gateway, "
   180	                                                                "from_microbit_gateway", nargs='+',
   181	                        help="A space-delimited list of topics")
   182	    parser.add_argument("-n", dest="process_name", default="WebSocket Gateway",
   183	                        help="Set process name in banner")
   184	    parser.add_argument("-p", dest="publisher_port", default='43124',
   185	                        help="Publisher IP port")
   186	    parser.add_argument("-s", dest="subscriber_port", default='43125',
   187	                        help="Subscriber IP port")
   188	
   189	    args = parser.parse_args()
   190	
   191	    subscription_list = args.subscription_list.split(',')
   192	
   193	    kw_options = {
   194	        'publisher_port': args.publisher_port,
   195	        'subscriber_port': args.subscriber_port,
   196	        'process_name': args.process_name,
   197	    }
   198	
   199	    if args.back_plane_ip_address != 'None':
   200	        kw_options['back_plane_ip_address'] = args.back_plane_ip_address
   201	
   202	    # get the event loop
   203	    loop = asyncio.get_event_loop()
   204	
   205	    WsGateway(*subscription_list, **kw_options, event_loop=loop)
   206	
   207	
   208	def signal_handler(sig, frame):
   209	    print('Exiting Through Signal Handler')
   210	    raise KeyboardInterrupt
   211	
   212	
   213	# listen for SIGINT
   214	signal.signal(signal.SIGINT, signal_handler)
   215	signal.signal(signal.SIGTERM, signal_handler)
   216	
   217	if __name__ == '__main__':
   218	    ws_gateway()
```

Lines 167-219 implement the standard way of instantiating a 
Banyan component.

<br>
<br>
Copyright (C) 2017-2020 Alan Yorinks All Rights Reserved
