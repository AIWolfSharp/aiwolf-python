"""
player.py

(c) 2022 OTSUKI Takashi

"""
from abc import ABC, abstractmethod

from aiwolf.agent import Agent
from aiwolf.content import Content
from aiwolf.gameinfo import GameInfo
from aiwolf.gamesetting import GameSetting


class AbstractPlayer(ABC):

    @abstractmethod
    def attack(self) -> Agent:
        pass

    @abstractmethod
    def day_start(self) -> None:
        pass

    @abstractmethod
    def divine(self) -> Agent:
        pass

    @abstractmethod
    def finish(self) -> None:
        pass

    def get_name(self) -> str:
        return type(self).__name__

    @abstractmethod
    def guard(self) -> Agent:
        pass

    @abstractmethod
    def initialize(self, game_info: GameInfo, game_setting: GameSetting) -> None:
        pass

    @abstractmethod
    def talk(self) -> Content:
        pass

    @abstractmethod
    def update(self, game_info: GameInfo) -> None:
        pass

    @abstractmethod
    def vote(self) -> Agent:
        pass

    @abstractmethod
    def whisper(self) -> Content:
        pass
