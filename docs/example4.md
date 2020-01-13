# JavaScript, Ruby, and Java Banyan Frameworks

There are versions of the Banyan Framework available for
[JavaScript](https://github.com/MrYsLab/js-banyan), [Ruby](https://github.com/MrYsLab/rb_banyan),
[Java](https://github.com/MrYsLab/javabanyan).

Banyan components can be written with any of these frameworks, and the components
can be combined into a single Banyan application.

Below is the [simple echo server rewritten using the JavaScript Banyan Framework.](https://github.com/MrYsLab/python_banyan/blob/master/examples/simple_echo_server.js)

```
#!/usr/bin/env node

/**
 Copyright (c) 2017-2019 Alan Yorinks All right reserved.

 Python Banyan is free software; you can redistribute it and/or
 modify it under the terms of the GNU AFFERO GENERAL PUBLIC LICENSE
 Version 3 as published by the Free Software Foundation; either
 or (at your option) any later version.
 This library is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 General Public License for more details.

 You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
 along with this library; if not, write to the Free Software
 Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */

const BanyanBase = require('js-banyan/lib/banyan_base');

class SimpleEchoServer extends BanyanBase {

    constructor() {

        super({ processName: 'SimpleEchoServer'
        });

        this.set_subscriber_topic('echo');
        this.receive_loop();
    }

    incoming_message_processing( topic, payload) {
        console.log('Message number:', payload['message_number']);
        this.publish_payload(payload, 'reply');
    }
}
try {
    new SimpleEchoServer();
}
catch(err){
    process.exit()
}
```

Compare it to the [Python version](../example1/#the-server) and you can easily
see how similar they are.

To run the example, first start the Backplane (it can be any of the Backplanes - Python, JavaScript,
Ruby or Java),
then start the JavaScript server:

```
node simple_echo_server.js
```

and finally start the Python client. The application runs as if it was written for a
single platform.

No changes to the protocol messages or the code are necessary. The components, in conjunction with
any of the Backplanes, create a cohesive, seamless application.
