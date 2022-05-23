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

from subprocess import PIPE
from subprocess import Popen


def call_prog(prog, args_list):
    cmd = [prog] + ["-vconsole:off"] + list(args_list)
    pipe = Popen(cmd, stdout=PIPE, stderr=PIPE)
    output, error = pipe.communicate()
    if pipe.returncode == 0:
        return 0, output.decode().strip()
    return pipe.returncode, error.decode().strip()


def ovs_vsctl(*args):
    return call_prog("ovs-vsctl", args)


def ovs_ofctl(*args):
    return call_prog("ovs-ofctl", args)


def find_bridge(port):
    code, output = ovs_vsctl('iface-to-br', port)
    return code, output


def is_bridge(port):
    code, _ = ovs_vsctl('br-exists', port)
    return code == 0


def find_statistics(port):
    try:
        code, bridge = find_bridge(port)
        if code != 0:
            if is_bridge(port):
                bridge = port
            else:
                raise Exception(bridge)
        code, output = ovs_ofctl('dump-ports', bridge, port)
        if code != 0:
            raise Exception(output)
        rx = re.findall(r"rx pkts=(\?|\d+), bytes=(\?|\d+), drop=(\?|\d+), errs=(\?|\d+)",
                        output, re.S)
        tx = re.findall(r"tx pkts=(\?|\d+), bytes=(\?|\d+), drop=(\?|\d+), errs=(\?|\d+)",
                        output, re.S)

        def format_stat(data):
            return [0 if i == '?' else int(i) for i in data]

        return format_stat(rx[0]), format_stat(tx[0])
    except Exception as e:
        sys.stdout.write("%s\n" % e)
        return [0] * 4, [0] * 4


parser = argparse.ArgumentParser()
parser.add_argument("-i", "--interface", default="", type=str,
                    help="watch on interface.")
parser.add_argument("-n", "--interval", default=2, type=int,
                    help="interval time per second")
args = parser.parse_args()


def run():
    interval = args.interval * 1.0
    ports = args.interface.split(',')
    start_time = time.time()
    sys.stdout.write(('%-6.2f %-13s' + ' %-10s' * 8 + '\n') %
                     (0, 'IFACE',
                      'rxpck/s', 'txpck/s',
                      'rxkB/s', 'txkB/s',
                      'rxdrop/s', 'txdrop/s',
                      'rxerr/s', 'txerr/s'))
    rx0 = {}
    tx0 = {}
    for i in ports:
        rx0[i], tx0[i] = find_statistics(i)
    record = time.time()
    while True:
        rx1 = {}
        tx1 = {}
        time.sleep(interval)
        for i in ports:
            rx1[i], tx1[i] = find_statistics(i)
        dt = time.time() - record
        for i in ports:
            sys.stdout.write(('%-6.2f %-13s' + ' %-10.2f' * 8 + '\n') %
                             (time.time() - start_time, i,
                              (rx1[i][0] - rx0[i][0]) / dt,
                              (tx1[i][0] - tx0[i][0]) / dt,
                              (rx1[i][1] - rx0[i][1]) / 1024.0 / dt,
                              (tx1[i][1] - tx0[i][1]) / 1024.0 / dt,
                              (rx1[i][2] - rx0[i][2]) / dt,
                              (tx1[i][2] - tx0[i][2]) / dt,
                              (rx1[i][3] - rx0[i][3]) / dt,
                              (tx1[i][3] - tx0[i][3]) / dt))
        rx0 = rx1
        tx0 = tx1
        record = time.time()


def setup():
    x = threading.Thread(target=run)
    x.setDaemon(True)
    x.start()


def wait():
    while True:
        try:
            time.sleep(0.5)
        except KeyboardInterrupt:
            return


def main():
    setup()
    wait()


if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        raise
