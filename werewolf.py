#
# werewolf.py
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

import random
from typing import List, Optional

from aiwolf.agent import Agent, Role, Species
from aiwolf.content import (AttackContentBuilder, ComingoutContentBuilder,
                            Content)
from aiwolf.gameinfo import GameInfo
from aiwolf.gamesetting import GameSetting
from aiwolf.judge import Judge
from const import Const
from possessed import SamplePossessed


class SampleWerewolf(SamplePossessed):
    """ サンプル人狼エージェント """

    def __init__(self) -> None:
        super().__init__()
        self.allies: List[Agent] = []  # 味方リスト
        self.humans: List[Agent] = []  # 人間リスト
        self.attack_vote_candidate: Agent = Const.AGENT_NONE  # 襲撃投票先

    def initialize(self, game_info: GameInfo, game_setting: GameSetting) -> None:
        super().initialize(game_info, game_setting)
        if self.game_info is not None:
            self.allies = list(self.game_info.role_map.keys())
        self.humans = [a for a in self.get_others(self.agent_list) if a not in self.allies]
        # 1～3日目からランダムにカミングアウトする日付を決める
        self.co_date = random.randint(1, 3)
        # ランダムに騙る役職を決める
        self.fake_role = Role.VILLAGER
        if self.game_info is not None:
            self.fake_role = random.choice([r for r in [Role.VILLAGER, Role.SEER, Role.MEDIUM] if r in self.game_info.existing_role_list])

    def get_fake_judge(self) -> Optional[Judge]:
        ''' 偽判定を生成 '''
        if self.game_info is None:
            return None
        # 判定対象の決定
        target: Agent = Const.AGENT_NONE
        if self.fake_role is Role.SEER:  # 占い師騙りの場合ランダム
            if self.game_info.day != 0:
                target = self.random_select(self.get_alive(self.not_judged_agents))
        elif self.fake_role is Role.MEDIUM:
            target = self.game_info.executed_agent if self.game_info.executed_agent is not None else Const.AGENT_NONE
        if target is Const.AGENT_NONE:
            return None
        # 偽判定結果の決定
        result: Species = Species.HUMAN
        # 人間が偽占い対象の場合偽人狼に余裕があれば30%の確率で人狼と判定
        if target in self.humans:
            if len(self.werewolves) < self.num_wolves and random.random() < 0.3:
                result = Species.WEREWOLF
        return Judge(self.me, self.game_info.day, target, result)

    def day_start(self) -> None:
        super().day_start()
        self.attack_vote_candidate = Const.AGENT_NONE

    def whisper(self) -> Content:
        if self.game_info is None:
            return Const.CONTENT_SKIP
        # 初日は騙る役職を宣言し以降は襲撃投票先を宣言
        if self.game_info.day == 0:
            return Content(ComingoutContentBuilder(self.me, self.fake_role))
        # 襲撃投票先を決定
        # まずカミングアウトした人間から
        candidates = [a for a in self.get_alive(self.humans) if a in self.comingout_map.keys()]
        # いなければ人間から
        if not candidates:
            candidates = self.get_alive(self.humans)
        # 初めての襲撃投票先宣言あるいは変更ありの場合，襲撃投票先宣言
        if self.attack_vote_candidate is Const.AGENT_NONE or self.attack_vote_candidate not in candidates:
            self.attack_vote_candidate = self.random_select(candidates)
            if self.attack_vote_candidate is not Const.AGENT_NONE:
                return Content(AttackContentBuilder(self.attack_vote_candidate))
        return Const.CONTENT_SKIP

    def attack(self) -> Agent:
        return self.attack_vote_candidate if self.attack_vote_candidate is not Const.AGENT_NONE else self.me
