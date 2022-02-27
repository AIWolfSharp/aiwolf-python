#
# player.py
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
