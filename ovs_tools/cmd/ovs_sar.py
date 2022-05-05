# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import re
import sys
import time
import threading

from ovs_tools.common.prog import ovs_vsctl
from ovs_tools.common.prog import ovs_ofctl

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--interface", default="", type=str,
                    help="watch on interface.")
parser.add_argument("-n", "--interval", default=2, type=int,
                    help="interval time per second")
args = parser.parse_args()


def find_bridge(port):
    code, output = ovs_vsctl('iface-to-br', port)
    return code, output


def find_statistics(port):
    try:
        code, bridge = find_bridge(port)
        if code != 0:
            raise Exception(bridge)
        code, output = ovs_ofctl('dump-ports', bridge, port)
        if code != 0:
            raise Exception(output)
        rx = re.findall(r"rx pkts=(\d+), bytes=(\d+), drop=(\d+), errs=(\d+)",
                        output, re.S)
        tx = re.findall(r"tx pkts=(\d+), bytes=(\d+), drop=(\d+), errs=(\d+)",
                        output, re.S)
        return [int(i) for i in rx[0]], [int(i) for i in tx[0]]
    except Exception as e:
        sys.stdout.write("%s\n"% e)
        return [0] * 4, [0] * 4


def run():
    inl = args.interval * 1.0
    ports = args.interface.split(',')
    last = time.time()
    sys.stdout.write(('%-6.2f %-13s' + ' %-10s' * 8 + '\n') %
                     (0, 'IFACE', 'rxpck/s', 'txpck/s', 'rxkB/s',
                      'txkB/s', 'rxerr/s', 'txerr/s', 'rxdrop/s', 'txdrop/s'))
    while True:
        rx0 = {}
        tx0 = {}
        rx1 = {}
        tx1 = {}
        record = time.time()
        for i in ports:
            rx0[i], tx0[i] = find_statistics(i)
        time.sleep(inl - (time.time() - record))
        for i in ports:
            rx1[i], tx1[i] = find_statistics(i)
        for i in ports:
            sys.stdout.write(('%-6.2f %-13s' + ' %-10.2f' * 8 + '\n') %
                             (time.time() - last, i,
                              (rx1[i][0] - rx0[i][0]) / inl, (tx1[i][0] - tx0[i][0]) / inl,
                              (rx1[i][1] - rx0[i][1]) / 1024.0 / inl, (tx1[i][1] - tx0[i][1]) / 1024.0 / inl,
                              (rx1[i][2] - rx0[i][2]) / inl, (tx1[i][2] - tx0[i][2]) / inl,
                              (rx1[i][3] - rx0[i][3]) / inl, (tx1[i][3] - tx0[i][3]) / inl))


def setup():
    x = threading.Thread(target=run)
    x.setDaemon(True)
    x.start()


def main():
    setup()
    while True:
        time.sleep(0.5)


if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        raise
