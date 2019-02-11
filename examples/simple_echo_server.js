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
