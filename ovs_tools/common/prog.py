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
