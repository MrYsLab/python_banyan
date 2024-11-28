from setuptools import setup

with open('../pypi_desc.md') as f:
    long_description = f.read()

setup(
    name='python-banyan',
    version='3.15',
    packages=[
        'python_banyan',
        'python_banyan.banyan_base',
        'python_banyan.banyan_base_aio',
        'python_banyan.banyan_base_multi',
        'python_banyan.gateway_base',
        'python_banyan.gateway_base_aio',
        'python_banyan.utils',
        'python_banyan.utils.monitor',
        'python_banyan.utils.banyan_launcher',
        'python_banyan.utils.mqtt_gateway',
        'python_banyan.utils.tcp_gateway',
        'python_banyan.backplane',
    ],
    install_requires=[
        'pyzmq',
        'msgpack-python',
        'numpy>=1.9',
        'msgpack-numpy',
        'psutil',
        'apscheduler',
        'websockets==13.1'
    ],

    entry_points={
        'console_scripts': [
            'backplane = python_banyan.backplane.backplane:bp',
            'monitor = python_banyan.utils.monitor.monitor:monitor',
            'bls = python_banyan.utils.banyan_launcher.bls:bls',
            'blc = python_banyan.utils.banyan_launcher.blc:blc',
            'blk = python_banyan.utils.banyan_launcher.blk:blk',
            'mgw = python_banyan.utils.mqtt_gateway.mqtt_gateway:mqtt_gateway',
            'tgw = python_banyan.utils.tcp_gateway.tcp_gateway:tcp_gateway',
        ]
    },

    url='https://github.com/MrYsLab/python_banyan',
    license='GNU Affero General Public License v3 or later (AGPLv3+)',
    author='Alan Yorinks',
    author_email='MisterYsLab@gmail.com',
    description='A Non-Blocking Event Driven Applications Framework',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords=['python banyan',  'RPC', 'Remote Procedure Call', 'Event Driven',
              'Asynchronous', 'Non-Blocking',
              'Raspberry Pi', 'ZeroMQ', 'MessagePack', 'RedBot'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Other Environment',
        'Intended Audience :: Education',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Education',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: System :: Hardware'
    ],
)
