## Installing Your Components As Executable Modules

There are times when it is more convenient to start a Banyan component
using the command line without having to specifically invoke the Python
interpreter.

For example, instead of starting the server with:
```
python simple_echo_server.py
```

You might wish to start it by simply typing:
```
server
```

Fortunately, the Python [setuptools](https://setuptools.readthedocs.io/en/latest/)
provide a fairly simple way to install a Python script as a command line executable.

The setuptools can perform the installation in a platform independent way, so no matter if you are running
Windows, Mac or Linux, no code changes are necessary and installation is performed
consistently across all platforms.

## Creating A Package Directory Structure

The first thing you need to do is to setup a directory structure for setuptools to use.
Setuptools expects a very specific directory structure.

Here is a directory structure for an example project called *ecs*.
```
ecs
├── ecs
│   ├── echo_cmdline_client.py
│   ├── __init__.py
│   ├── simple_echo_server.py
│   └── tk_echo_client.py
└── setup.py
```

You can find a copy of this directory and all of its files on [GitHub.](https://github.com/MrYsLab/python_banyan/tree/master/examples/ecs)

We start with a top level directory called ecs. The ecs directory contains
the *setup.py* file, and another directory, with the package name *ecs*.
This second directory holds the package's source files, as well as
*\__init__.py*. This file is empty, but identifies this directory as a *python package*
for setuptools.

The *setup.py* file will be configured to install the three Python source files as executables
called
*server*, *client* and *gui*. To perform the installation, we will
use the [*pip*](https://pip.pypa.io/en/stable/) facility.

## setup.py

Let's start by looking at the setup.py file shown below.

```
     1	from setuptools import setup
     2
     3	setup(
     4	    name='ecs',
     5	    version='1.0',
     6	    packages=[
     7	        'ecs',
     8	    ],
     9	    install_requires=[
    10	        'pyzmq',
    11	        'u-msgpack-python',
    12	        'msgpack-python',
    13	        'numpy>=1.9',
    14	        'msgpack-numpy',
    15	        'psutil'
    16	    ],
    17
    18	    entry_points={
    19	        'console_scripts': [
    20	            'client = ecs.echo_cmdline_client:echo_cmdline_client',
    21	            'server = ecs.simple_echo_server:echo_server',
    22	            'gui = ecs.tk_echo_client:gui_client'
    23	        ]
    24	    },
    25	)


```

Line 1 imports setup from setuptools.

Lines 3 through 25 define the *setup* function required by setuptools.

Line 4 is the name parameter which specifies the name we wish to give to our package.

Line 5 is the version number. We can change the version as we make changes.

Line 6 is a list of packages that make up our package. A package can be comprised of set of packages
and therefore it is expressed as a list. For our purposes, we only have one package.

Lines 9 through 16 is a list of packages our package requires to run.

Lines 18 through 24 defines a dictionary called *entry_points* that contains a single
key called *console_scripts*, with a list of 3 strings as its value.

For each of the three entries, the string to the left of the equals sign is the command line
command name for the script. The string between the equals sign and the colon defines
the location of the python script, and the string after the colon defines the name of the function
that will be called within the script to start it.

Let's look at the format for the first executable, *'client'*.

### Executable Name
On the left of the equal sign is the name we wish to give the our executable, and in this
case the name is *client*.

### Location Of The File
On the right of the equal sign, is a dotted notation of where the source file resides,
followed by a function within the file to be called to start the program.

Line 20 specifies the file location as "ecs.echo_cmdline_client". The first
part is the name of the package, "ecs". That is the directory that contains the source
files. The second part is the file name within this directory, "echo_cmdline_client"

### Startup Function
If we look at line 125 of the source code for the
[client](https://github.com/MrYsLab/python_banyan/blob/master/examples/echo_cmdline_client.py), we see the function
called "echo_cmdline_client" and this is the function we specify to start the component
when we invoke "client" as a command line command.



## Installing With *pip*

To install our files as executables we first go to the directory that contains the
*ecs* directory, for example, *python_banyan/python_banyan/examples*.

We then type:
```
pip install ./ecs
```
to install using our local copy of the ecs package. If we did not specify "*./ecs*" and just
used *ecs*, pip would try to access and install the package from [pypi](https://pypi.org/)
 on the internet.

Now, after starting the Backplane, you can start the server by simply typing
"server" in a command window, and either "client" or "gui" in another command window
to start a client.

