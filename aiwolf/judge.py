"""
judge.py

(c) 2022 OTSUKI Takashi

"""
from __future__ import annotations

from typing import TypedDict

from aiwolf.agent import Agent, Species
from aiwolf.constant import Constant as C


class Judge0(TypedDict):
    agent: int
    day: int
    target: int
    result: str


class Judge:
    def __init__(self, agent: Agent = C.AGENT_NONE, day: int = -1, target: Agent = C.AGENT_NONE, result: Species = Species.UNC) -> None:
        self.agent: Agent = agent
        self.day: int = day
        self.target: Agent = target
        self.result: Species = result

    @staticmethod
    def compile(judge0: Judge0) -> Judge:
        j: Judge = Judge()
        j.agent = Agent(judge0['agent'])
        j.day = judge0['day']
        j.target = Agent(judge0['target'])
        j.result = Species[judge0['result']]
        return j
