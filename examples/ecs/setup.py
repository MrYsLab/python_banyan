from setuptools import setup

setup(
    name='ecs',
    version='1.0',
    packages=[
        'ecs',
    ],
    install_requires=[
        'pyzmq',
        'u-msgpack-python',
        'msgpack-python',
        'numpy>=1.9',
        'msgpack-numpy',
        'psutil'
    ],

    entry_points={
        'console_scripts': [
            'client = ecs.echo_cmdline_client:echo_cmdline_client',
            'server = ecs.echo_cmdline_server:echo_cmdline_server',
            'gui = ecs.tk_echo_client:gui_client'
        ]
    },
)
