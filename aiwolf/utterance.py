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
"""utterance module."""
from __future__ import annotations

from enum import Enum
from typing import Final, TypedDict

from aiwolf.agent import Agent
from aiwolf.constant import AGENT_NONE


class UtteranceType(Enum):
    """Enumeration type for the kind of utterance."""

    TALK = "TALK"
    """Talk."""

    WHISPER = "WHISPER"
    """Whisper."""


class _Utterance(TypedDict):
    day: int
    agent: int
    idx: int
    text: str
    turn: int


class Utterance:
    """Class for utterance."""

    OVER: Final[str] = "Over"
    """The string that nothing to say."""

    SKIP: Final[str] = "Skip"
    """The string that means skip this turn."""

    def __init__(self, day: int = -1, agent: Agent = AGENT_NONE, idx: int = -1, text: str = "", turn: int = -1) -> None:
        """Initialize a new instance of Utterance.

        Args:
            day(opional): The date of the utterance. Defaults to -1.
            agent(optional): The agent that utters. Defaults to C.AGENT_NONE.
            idx(optional): The index number of the utterance. Defaults to -1.
            text(optional): The uttered text. Defaults to "".
            turn(optional): The turn of the utterance. Defaults to -1.
        """
        self.day: int = day
        """The date of this utterance."""

        self.agent: Agent = agent
        """The agent who uttered."""

        self.idx: int = idx
        """The index number of this utterance."""

        self.text: str = text
        """The contents of this utterance."""

        self.turn: int = turn
        """The turn of this utterance."""

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, Utterance):
            return NotImplemented
        return self is __o or (type(self) == type(__o) and self.day == __o.day and self.agent == __o.agent
                               and self.idx == __o.idx and self.text == __o.text and self.turn == __o.turn)


class Talk(Utterance):
    """Talk class."""

    def __init__(self, day: int = -1, agent: Agent = AGENT_NONE, idx: int = -1, text: str = "", turn: int = -1) -> None:
        """Initialize a new instance of Talk.

        Args:
            day(opional): The date of the utterance. Defaults to -1.
            agent(optional): The agent that utters. Defaults to C.AGENT_NONE.
            idx(optional): The index number of the utterance. Defaults to -1.
            text(optional): The uttered text. Defaults to "".
            turn(optional): The turn of the utterance. Defaults to -1.
        """
        super().__init__(day, agent, idx, text, turn)

    @staticmethod
    def compile(utterance: _Utterance) -> Talk:
        """Convert a _Utterance into the corresponding Talk.

        Args:
            utterance: The _Utterance to be converted.

        Returns:
            The Talk converted from the given _Utterance.
        """
        t = Talk()
        t.day = utterance["day"]
        t.agent = Agent(utterance["agent"])
        t.idx = utterance["idx"]
        t.text = utterance["text"]
        t.turn = utterance["turn"]
        return t


class Whisper(Utterance):
    """Whisper class."""

    def __init__(self, day: int = -1, agent: Agent = AGENT_NONE, idx: int = -1, text: str = "", turn: int = -1) -> None:
        """Initialize a new instance of Whisper.

        Args:
            day(opional): The date of the utterance. Defaults to -1.
            agent(optional): The agent that utters. Defaults to C.AGENT_NONE.
            idx(optional): The index number of the utterance. Defaults to -1.
            text(optional): The uttered text. Defaults to "".
            turn(optional): The turn of the utterance. Defaults to -1.
        """
        super().__init__(day, agent, idx, text, turn)

    @staticmethod
    def compile(utterance: _Utterance) -> Whisper:
        """Convert a _Utterance into the corresponding Whisper.

        Args:
            utterance: The _Utterance to be converted.

        Returns:
            The Whisper converted from the given _Utterance.
        """
        w = Whisper()
        w.day = utterance["day"]
        w.agent = Agent(utterance["agent"])
        w.idx = utterance["idx"]
        w.text = utterance["text"]
        w.turn = utterance["turn"]
        return w
