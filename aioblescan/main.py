#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# This application is an example on how to use aioblescan
#
# Copyright (c) 2017 François Wautier
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies
# or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
# IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE
import sys
import asyncio
import argparse
import re
import aioblescan as aiobs
from plugins import EddyStone
from plugins import RuuviWeather

async def say(what, when):
    await asyncio.sleep(when)
    print(what)


def my_process(self):
    ev=aiobs.HCI_Event()
    xx=ev.decode(self)
    xx=EddyStone().decode(ev)
    if xx:
        print(xx)
        return (xx.get('rssi'))

try:
    mydev=int(sys.argv[1])
except:
    mydev=0


event_loop = asyncio.get_event_loop()

#First create and configure a raw socket
mysocket = aiobs.create_bt_socket(mydev)

#create a connection with the raw socket
#This used to work but now requires a STREAM socket.
#fac=event_loop.create_connection(aiobs.BLEScanRequester,sock=mysocket)
#Thanks to martensjacobs for this fix
fac=event_loop._create_connection_transport(mysocket,aiobs.BLEScanRequester,None,None)
#Start it
conn,btctrl = event_loop.run_until_complete(fac)
#Attach your processing
btctrl.process=my_process

#Probe
#event_loop.create_task(say('first hello', 0))
btctrl.send_scan_request()
try:
    # event_loop.run_until_complete(coro)
    event_loop.run_forever()
except KeyboardInterrupt:
    print('keyboard interrupt')
finally:
    print('closing event loop')
    btctrl.stop_scan_request()
    command = aiobs.HCI_Cmd_LE_Advertise(enable=False)
    btctrl.send_command(command)
    conn.close()
    event_loop.close()
