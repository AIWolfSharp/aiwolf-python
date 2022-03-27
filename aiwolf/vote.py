#
# vote.py
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
"""vote module."""
from __future__ import annotations

from typing import TypedDict

from aiwolf.agent import Agent
from aiwolf.constant import Constant as C


class _Vote(TypedDict):
    agent: int
    day: int
    target: int


class Vote:
    """Information of the vote for execution/attack."""

    _agent: Agent
    _day: int
    _target: Agent

    def __init__(self, agent: Agent = C.AGENT_NONE, day: int = -1, target: Agent = C.AGENT_NONE) -> None:
        """Initialize a new instance of Vote.

        Args:
            agent(optional): The agent that votes. Defaults to C.AGENT_NONE.
            day(optional): The date of the vote. Defaults to -1.
            target(optional): The agent to be voted on. Defaults to C.AGENT_NONE.
        """
        self._agent = agent
        self._day = day
        self._target = target

    @staticmethod
    def compile(vote: _Vote) -> Vote:
        """Convert a _Vote into the corresponding Vote.

        Args:
            vote: The _Vote to be converted.

        Returns:
            The Vote converted from the given _Vote.
        """

        v = Vote()
        v._agent = Agent(vote["agent"])
        v._day = vote["day"]
        v._target = Agent(vote["target"])
        return v

    @property
    def agent(self) -> Agent:
        """The agent that votes."""
        return self._agent

    @property
    def day(self) -> int:
        """The date of the vote."""
        return self._day

    @property
    def target(self) -> Agent:
        """The agent to be voted on."""
        return self._target
