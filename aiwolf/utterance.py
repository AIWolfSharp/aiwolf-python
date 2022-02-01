"""
utterance.py

(c) 2022 OTSUKI Takashi

"""
from __future__ import annotations

from enum import Enum
from typing import TypedDict

from aiwolf.agent import Agent
from aiwolf.constant import Constant as C


class UtteranceType(Enum):
    TALK = "TALK"
    WHISPER = "WHISPER"


class Utterance0(TypedDict):
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
    def compile(utterance0: Utterance0) -> Talk:
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
    def compile(utterance0: Utterance0) -> Whisper:
        w = Whisper()
        w.day = utterance0["day"]
        w.agent = Agent(utterance0["agent"])
        w.idx = utterance0["idx"]
        w.text = utterance0["text"]
        w.turn = utterance0["turn"]
        return w
    