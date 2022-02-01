"""
constant.py

(c) 2022 OTSUKI Takashi

"""
from aiwolf.agent import Agent


class Constant:
    AGENT_NONE = Agent(0)
    AGENT_UNSPEC = AGENT_NONE
    AGENT_ANY = Agent(0xff)
