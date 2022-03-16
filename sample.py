#
# sample.py
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

from aiwolf.agent import Agent, Role
from aiwolf.content import Content
from aiwolf.gameinfo import GameInfo
from aiwolf.gamesetting import GameSetting
from aiwolf.player import AbstractPlayer
from bodyguard import SampleBodyguard
from medium import SampleMedium
from possessed import SamplePossessed
from seer import SampleSeer
from villager import SampleVillager
from werewolf import SampleWerewolf


class SamplePlayer(AbstractPlayer):

    def __init__(self) -> None:
        self.villager: AbstractPlayer = SampleVillager()
        self.bodyguard: AbstractPlayer = SampleBodyguard()
        self.medium: AbstractPlayer = SampleMedium()
        self.seer: AbstractPlayer = SampleSeer()
        self.possessed: AbstractPlayer = SamplePossessed()
        self.werewolf: AbstractPlayer = SampleWerewolf()
        self.player: AbstractPlayer = self.villager

    def attack(self) -> Agent:
        return self.player.attack()

    def day_start(self) -> None:
        self.player.day_start()

    def divine(self) -> Agent:
        return self.player.divine()

    def finish(self) -> None:
        self.player.finish()

    def guard(self) -> Agent:
        return self.player.guard()

    def initialize(self, game_info: GameInfo, game_setting: GameSetting) -> None:
        role = game_info.my_role
        if role is Role.VILLAGER:
            self.player = self.villager
        elif role is Role.BODYGUARD:
            self.player = self.bodyguard
        elif role is Role.MEDIUM:
            self.player = self.medium
        elif role is Role.SEER:
            self.player = self.seer
        elif role is Role.POSSESSED:
            self.player = self.possessed
        elif role is Role.WEREWOLF:
            self.player = self.werewolf
        self.player.initialize(game_info, game_setting)

    def talk(self) -> Content:
        return self.player.talk()

    def update(self, game_info: GameInfo) -> None:
        self.player.update(game_info)

    def vote(self) -> Agent:
        return self.player.vote()

    def whisper(self) -> Content:
        return self.player.whisper()
