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

import shlex
import subprocess
import sys

verbose_args = []

def call_prog(prog, args_list):
    cmd = [prog] + verbose_args + ["-vconsole:off"] + args_list
    creationFlags = 0
    if sys.platform == 'win32':
        creationFlags = 0x08000000  # CREATE_NO_WINDOW
    output = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                              creationflags=creationFlags).communicate()
    if len(output) == 0 or output[0] is None:
        output = ""
    else:
        output = output[0].decode().strip()
    return output


def ovs_vsctl(args):
    return call_prog("ovs-vsctl", shlex.split(args))


def ovs_ofctl(args):
    return call_prog("ovs-ofctl", shlex.split(args))