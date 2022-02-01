"""
agent.py

(c) 2022 OTSUKI Takashi

"""

from __future__ import annotations

import re
from enum import Enum
from typing import Dict, Match, Optional, Pattern


class Agent:

    __agent_map: Dict[int, Agent] = {}

    agent_pattern: Pattern[str] = re.compile(r"(Agent\[(\d+)\]|ANY)")

    @staticmethod
    def compile(input: str) -> Agent:
        """Converts the string representation of Agent into Agent."""
        m: Optional[Match[str]] = Agent.agent_pattern.match(input)
        if m:
            if m.group(1) == "ANY":
                return Agent(0xff)
            else:
                return Agent(int(m.group(2)))
        return Agent(0)

    def __new__(cls: type[Agent], idx: int) -> Agent:
        if idx < 0:
            raise ValueError("agent index must not be negative")
        if idx in cls.__agent_map.keys():
            return cls.__agent_map[idx]
        cls.__agent_map[idx] = super().__new__(cls)
        return cls.__agent_map[idx]

    def __init__(self, idx: int) -> None:
        self.__agent_idx = idx

    @property
    def agent_idx(self) -> int:
        return self.__agent_idx

    def __str__(self) -> str:
        return "Agent[" + "{:02}".format(self.agent_idx) + "]"


class Role(Enum):
    UNC = "UNC"
    BODYGUARD = "BODYGUARD"
    FOX = "FOX"
    FREEMASON = "FREEMASON"
    MEDIUM = "MEDIUM"
    POSSESSED = "POSSESSED"
    SEER = "SEER"
    VILLAGER = "VILLAGER"
    WEREWOLF = "WEREWOLF"
    ANY = "ANY"


class Species(Enum):
    UNC = "UNC"
    HUMAN = "HUMAN"
    WEREWOLF = "WEREWOLF"
    ANY = "ANY"


class Status(Enum):
    UNC = "UNC"
    ALIVE = "ALIVE"
    DEAD = "DEAD"
