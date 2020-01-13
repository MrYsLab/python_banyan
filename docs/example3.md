# Distributing Banyan Application Components Across Multiple Computers

Distributing the components of a Banyan application across multiple computers
is a simple matter of copying the component's Python
code to the desired computer, and then pointing the component to the IP address and ports
of the running Backplane.



For example let's say we have 2 computers on a network, one with an IP address of
192.168.1.100 and the other with an address of 192.168.2.200.

 <img align="center" src="../images/distributed.png">


  If we wish to
distribute the application so that the ***Backplane*** and the ***echo server*** from
[example 1](../example1/#the-server) runs on computer 1, and the modified
echo client from [example 2](../example2/#example2) runs on computer 2, we would first start the Backplane
and the server on computer 1 as described in [example 1](../example1/#example1),
and then we would start a copy of ***echo_cmdline_client.py***  on computer 2 using
the -b 192.168.1.100 option to point to the Backplane on computer 1:

```
python3 echo_cmdline_client.py -b 192.168.1.100
```

That's it - no configuration files, no recoding, just a simple command line option!

The client will publish 10 messages, but we can easily modify that with the
 -m command line option:

```
python3 echo_cmdline_client.py -b 192.168.1.100 -m 20
```
