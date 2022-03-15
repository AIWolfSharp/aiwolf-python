#
# judge.py
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

from aiwolf.agent import Agent, Species
from aiwolf.constant import Constant as C


class _Judge(TypedDict):
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
    def compile(judge0: _Judge) -> Judge:
        j: Judge = Judge()
        j.agent = Agent(judge0['agent'])
        j.day = judge0['day']
        j.target = Agent(judge0['target'])
        j.result = Species[judge0['result']]
        return j
