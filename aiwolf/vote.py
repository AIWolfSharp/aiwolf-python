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
