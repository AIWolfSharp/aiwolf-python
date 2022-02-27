#
# bodyguard.py
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

from typing import List

from aiwolf.agent import Agent, Role, Species
from aiwolf.gameinfo import GameInfo
from aiwolf.gamesetting import GameSetting
from const import Const
from villager import SampleVillager


class SampleBodyguard(SampleVillager):
    """ サンプル狩人エージェント """

    def __init__(self) -> None:
        super().__init__()
        self.to_be_guarded: Agent = Const.AGENT_NONE  # 護衛対象

    def initialize(self, game_info: GameInfo, game_setting: GameSetting) -> None:
        super().initialize(game_info, game_setting)
        self.to_be_guarded = Const.AGENT_NONE

    def guard(self) -> Agent:
        # 非偽生存自称占い師を護衛
        candidates: List[Agent] = self.get_alive([j.agent for j in self.divination_reports if j.result is not Species.WEREWOLF or j.target is not self.me])
        # いなければ生存自称霊媒師を護衛
        if not candidates:
            candidates = [a for a in self.comingout_map if self.is_alive(a) and self.comingout_map[a] is Role.MEDIUM]
        # いなければ生存エージェントを護衛
        if not candidates:
            candidates = self.get_alive_others(self.agent_list)
        # 初回あるいは変更ありの場合，護衛先を更新
        if self.to_be_guarded is Const.AGENT_NONE or self.to_be_guarded not in candidates:
            self.to_be_guarded = self.random_select(list(set(candidates)))
        return self.to_be_guarded if self.to_be_guarded is not Const.AGENT_NONE else self.me
