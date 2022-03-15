#
# utterance.py
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

from enum import Enum
from typing import TypedDict

from aiwolf.agent import Agent
from aiwolf.constant import Constant as C


class UtteranceType(Enum):
    TALK = "TALK"
    WHISPER = "WHISPER"


class _Utterance(TypedDict):
    day: int
    agent: int
    idx: int
    text: str
    turn: int


class Utterance:

    OVER = "Over"
    SKIP = "Skip"

    def __init__(self, day:int = -1, agent: Agent = C.AGENT_NONE, idx: int = -1, text: str = "", turn: int = -1) -> None:
        self.day: int = day
        self.agent:  Agent = agent
        self.idx: int = idx
        self.text: str = text
        self.turn: int = turn


class Talk(Utterance):
    def __init__(self, day: int = -1, agent: Agent = C.AGENT_NONE, idx: int = -1, text: str = "", turn: int = -1) -> None:
        super().__init__(day, agent, idx, text, turn)

    @staticmethod
    def compile(utterance0: _Utterance) -> Talk:
        t = Talk()
        t.day = utterance0["day"]
        t.agent = Agent(utterance0["agent"])
        t.idx = utterance0["idx"]
        t.text = utterance0["text"]
        t.turn = utterance0["turn"]
        return t


class Whisper(Utterance):
    def __init__(self, day: int = -1, agent: Agent = C.AGENT_NONE, idx: int = -1, text: str = "", turn: int = -1) -> None:
        super().__init__(day, agent, idx, text, turn)

    @staticmethod
    def compile(utterance0: _Utterance) -> Whisper:
        w = Whisper()
        w.day = utterance0["day"]
        w.agent = Agent(utterance0["agent"])
        w.idx = utterance0["idx"]
        w.text = utterance0["text"]
        w.turn = utterance0["turn"]
        return w
    