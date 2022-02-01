"""
vote.py

(c) 2022 OTSUKI Takashi

"""
from __future__ import annotations

from typing import TypedDict

from aiwolf.agent import Agent
from aiwolf.constant import Constant as C


class Vote0(TypedDict):
    agent: int
    day: int
    target: int


class Vote:
    def __init__(self, agent: Agent = C.AGENT_NONE, day: int = -1, target: Agent = C.AGENT_NONE) -> None:
        self.agent: Agent = agent
        self.day: int = day
        self.target: Agent = target

    @staticmethod
    def compile(vote0: Vote0) -> Vote:
        v = Vote()
        v.agent = Agent(vote0["agent"])
        v.day = vote0["day"]
        v.target = Agent(vote0["target"])
        return v
