from setuptools import setup

setup(
    name='python-banyan',
    version='1.0',
    packages=[
        'python_banyan.banyan_base',
        'python_banyan.utils',
        'python_banyan.backplane',
    ],
    install_requires=[
        'pyzmq',
        'u-msgpack-python',
    ],

    entry_points={
        'console_scripts': [
            'backplane = python_banyan.backplane.backplane:bp',
            'monitor = python_banyan.utils.monitor:monitor',

        ]
    },

    extras_require = {
        'examples':  ['python-banyan-examples'],
    },

    url='https://github.com/MrYsLab/python_banyan',
    license='GNU General Public License v3 (GPLv3)',
    author='Alan Yorinks',
    author_email='MisterYsLab@gmail.com',
    description='A Non-Blocking Event Driven Robotics Framework',
    keywords=['python banyan', 'Raspberry Pi', 'ZeroMQ', 'MessagePack', 'RedBot', ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Other Environment',
        'Intended Audience :: Education',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Education',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: System :: Hardware'
    ],
)
