#!/usr/bin/env -S python -B
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
