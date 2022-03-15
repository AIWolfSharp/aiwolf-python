#
# agent.py
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
"""agent module."""
from __future__ import annotations

import re
from enum import Enum
from typing import Dict, Match, Optional, Pattern


class Agent:
    """A player agent in AIWolf game."""

    _agent_map: Dict[int, Agent] = {}

    _agent_pattern: Pattern[str] = re.compile(r"(Agent\[(\d+)\]|ANY)")

    @staticmethod
    def compile(input: str) -> Agent:
        """Convert the string into the corresponding Agent.

        Args:
            input: The string representing an Agent.

        Returns:
            The Agent converted from the given string.
        """
        m: Optional[Match[str]] = Agent._agent_pattern.match(input)
        if m:
            if m.group(1) == "ANY":
                return Agent(0xff)
            else:
                return Agent(int(m.group(2)))
        return Agent(0)

    def __new__(cls: type[Agent], idx: int) -> Agent:
        if idx < 0:
            raise ValueError("agent index must not be negative")
        if idx in cls._agent_map.keys():
            return cls._agent_map[idx]
        cls._agent_map[idx] = super().__new__(cls)
        return cls._agent_map[idx]

    def __init__(self, idx: int) -> None:
        """Initialize a new instance of Agent.

        Args:
            idx: The index number of the Agent.
        """
        self._agent_idx = idx

    @property
    def agent_idx(self) -> int:
        """The index number of this Agent."""
        return self._agent_idx

    def __str__(self) -> str:
        return "Agent[" + "{:02}".format(self.agent_idx) + "]"


class Role(Enum):
    """Enumeration type for role."""

    UNC = "UNC"
    """Uncertain."""

    BODYGUARD = "BODYGUARD"
    """Bodyguard."""

    FOX = "FOX"
    """Fox."""

    FREEMASON = "FREEMASON"
    """Freemason."""

    MEDIUM = "MEDIUM"
    """Medium."""

    POSSESSED = "POSSESSED"
    """Possessed human."""

    SEER = "SEER"
    """Seer."""

    VILLAGER = "VILLAGER"
    """Villager."""

    WEREWOLF = "WEREWOLF"
    """Werewolf."""

    ANY = "ANY"
    """Wildcard."""


class Species(Enum):
    """Enumeration type for species."""

    UNC = "UNC"
    """Uncertain."""

    HUMAN = "HUMAN"
    """Human."""

    WEREWOLF = "WEREWOLF"
    """Werewolf."""

    ANY = "ANY"
    """Wildcard."""


class Status(Enum):
    """Enumeration type for player's status (ie. alive or dead)."""

    UNC = "UNC"
    """Uncertain."""

    ALIVE = "ALIVE"
    """Alive."""

    DEAD = "DEAD"
    """Dead."""
