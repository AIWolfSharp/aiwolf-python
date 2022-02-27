#!/usr/bin/env -S python -B
#
# start.py
#
# Copyright 2022 OTSUKI Takashi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from argparse import ArgumentParser
from aiwolf.client import TcpipClient
from aiwolf.player import AbstractPlayer
from sample import SamplePlayer

if __name__ == "__main__":
    agent: AbstractPlayer = SamplePlayer()
    parser: ArgumentParser = ArgumentParser(add_help=False)
    parser.add_argument("-p", type=int, action="store", dest="port", required=True)
    parser.add_argument("-h", type=str, action="store", dest="hostname", required=True)
    parser.add_argument("-r", type=str, action="store", dest="role", default="none")
    parser.add_argument("-n", type=str, action="store", dest="name")
    input_args = parser.parse_args()
    TcpipClient(agent, input_args.name, input_args.hostname, input_args.port, input_args.role).connect()
