# Installing Python Banyan

## Checking For An Existing Python Installation

The first step in installing Python Banyan is to make sure you have Python
installed on your computer. Python Banyan is both Python 2 and Python3 compatible.
If either version is installed on your computer, you are ready to start using Python Banyan.

If you need to install Python on your system,
then Python 3 is recommended.

To check to see if you already have Python installed on your computer, open a command window and type:

```
python -V
```

or

```
python3 -V
```

You should see something similar to this screenshot:

![](./images/windows_python.png)


## Installing Python 3
If you need to install Python3 on your computer, use the latest version of Python 3 available.
As of this writing,
that version is 3.7.2.
If you have an earlier version already installed, upgrading to Python 3.7.2 is not necessary.

### Windows Users

To install Python 3.7.2 or later, go to the
<a href="https://www.python.org/" target="_blank">Python home page,</a>
and download the 3.7.2 (or later) distribution for your operating system.

If you have Python 2.7 installed, you do not need to remove it.

If there is a checkbox to add Python 3.7 to your path during the installation
 process, make sure it is checked before proceeding with the installation.

![](./images/pythonInstall.png)

### Debian Based Linux Distribution Users
To build the latest version of Python (version 3.8.1 at the time of this writing) for Debian based Linux releases, such as Ubuntu, Raspbian, etc.,
use the following build instructions:

1. sudo apt-get update
1. sudo apt-get upgrade
1. sudo apt-get dist-upgrade
1. sudo apt-get install build-essential python-dev python-setuptools python-pip python-smbus
1. sudo apt-get install build-essential libncursesw5-dev libgdbm-dev libc6-dev
1. sudo apt-get install zlib1g-dev libsqlite3-dev tk-dev
1. sudo apt-get install libssl-dev openssl
1. sudo apt-get install libffi-dev
1. cd ~
1. mkdir build
1. cd build
1. wget https://www.python.org/ftp/python/3.8.1/Python-3.8.1.tgz
1. tar -zxvf Python-3.7.2.tgz
1. cd Python-3.7.2
1. ./configure
1. make
1. sudo make install

Install pip
For Debian based distributions:
```
  sudo apt-get install pip3-python
```

### Non-Debian Based Linux Distribution Users
Check with your distribution provider for the latest versions of Python.

### Mac Users
1. Install Python 3.7.2 from [https://www.python.org/downloads/](https://www.python.org/downloads/)
 or via [homebrew](http://brew.sh/)
2. Download get-pip.py from [https://bootstrap.pypa.io/get-pip.py](https://bootstrap.pypa.io/get-pip.py) and
install (this should already be installed if Python was installed from python.org or homebrew):

```
curl -O https://bootstrap.pypa.io/get-pip.py
sudo python3 get-pip.py
```


### Verify The Python Installation
Refer to
 ["Checking To See If Python Is Installed,"](#checking-for-an-existing-python-installation)
 above.


# Installing Python Banyan

To install Python Banyan on **Linux and Mac** computers, open a terminal window and type:

```
sudo pip3 install python-banyan
```

**NOTE For Raspberry Pi Users**: When initially installing Python Banyan, it may take
approximately 10 minutes to install. The installation requires some compilation.

For **Windows** users, type:

```
pip install python-banyan
```

The code for Python Banyan can be found on [GitHub](https://github.com/MrYsLab/python_banyan).
<br>
<br>
Copyright (C) 2017-2020 Alan Yorinks All Rights Reserved
