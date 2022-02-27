#
# possessed.py
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
from queue import Queue
from typing import List, Optional

from aiwolf.agent import Agent, Role, Species
from aiwolf.content import (ComingoutContentBuilder, Content,
                            DivinedResultContentBuilder, IdentContentBuilder,
                            VoteContentBuilder)
from aiwolf.gameinfo import GameInfo
from aiwolf.gamesetting import GameSetting
from aiwolf.judge import Judge
from const import Const
from villager import SampleVillager


class SamplePossessed(SampleVillager):
    """ サンプル裏切り者エージェント """

    def __init__(self) -> None:
        super().__init__()
        self.fake_role: Role = Role.SEER  # 騙る役職
        self.co_date: int = 1  # CO予定日
        self.has_co: bool = False  # CO済ならtrue
        self.my_judgee_queue: Queue[Judge] = Queue()  # 偽判定結果の待ち行列
        self.not_judged_agents: List[Agent] = []  # 未判定エージェント
        self.num_wolves: int = 0  # 人狼の数
        self.werewolves: List[Agent] = []  # 偽人狼

    def initialize(self, game_info: GameInfo, game_setting: GameSetting) -> None:
        super().initialize(game_info, game_setting)
        self.fake_role = Role.SEER
        self.co_date = 1  # いきなりCO
        self.has_co = False
        self.my_judgee_queue = Queue()
        self.not_judged_agents = self.get_others(self.agent_list)
        self.num_wolves = game_setting.role_num_map[Role.WEREWOLF]
        self.werewolves = []

    def get_fake_judge(self) -> Optional[Judge]:
        """ 偽判定を生成 """
        if self.game_info is None:
            return None
        target: Agent = Const.AGENT_NONE
        if self.fake_role is Role.SEER:  # 占い師騙りの場合ランダム
            if self.game_info.day != 0:
                target = self.random_select(self.get_alive(self.not_judged_agents))
        elif self.fake_role is Role.MEDIUM:
            target = self.game_info.executed_agent if self.game_info.executed_agent is not None else Const.AGENT_NONE
        # 偽判定結果の決定
        result: Species = Species.HUMAN
        # 偽人狼に余裕があれば50%の確率で人狼と判定
        if len(self.werewolves) < self.num_wolves and random.random() < 0.5:
            result = Species.WEREWOLF
        return None if target is Const.AGENT_NONE else Judge(self.me, self.game_info.day, target, result)

    def day_start(self) -> None:
        super().day_start()
        # 偽判定結果の処理
        judge: Optional[Judge] = self.get_fake_judge()
        if judge is not None:
            self.my_judgee_queue.put(judge)
            if judge.target in self.not_judged_agents:
                self.not_judged_agents.remove(judge.target)
            if judge.result is Species.WEREWOLF:
                self.werewolves.append(judge.target)

    def talk(self) -> Content:
        if self.game_info is None:
            return Const.CONTENT_SKIP
        # 予定日あるいは人狼を発見したらCO
        if self.fake_role is not Role.VILLAGER and not self.has_co and (self.game_info.day == self.co_date or self.werewolves):
            self.has_co = True
            return Content(ComingoutContentBuilder(self.me, self.fake_role))
        # CO後は判定結果を報告
        if self.has_co and not self.my_judgee_queue.empty():
            judge: Judge = self.my_judgee_queue.get()
            if self.fake_role is Role.SEER:
                return Content(DivinedResultContentBuilder(judge.target, judge.result))
            elif self.fake_role is Role.MEDIUM:
                return Content(IdentContentBuilder(judge.target, judge.result))
        # 生存人狼に投票
        candidates: List[Agent] = self.get_alive(self.werewolves)
        # いなければ生存対抗エージェントに投票
        if not candidates:
            candidates = self.get_alive([a for a in self.comingout_map.keys() if self.comingout_map[a] == self.fake_role])
        # それでもいなければ生存エージェントに投票
        if not candidates:
            candidates = self.get_alive_others(self.agent_list)
        # 初めての投票先宣言あるいは変更ありの場合，投票先宣言
        if self.vote_candidate is Const.AGENT_NONE or self.vote_candidate not in candidates:
            self.vote_candidate = self.random_select(candidates)
            if self.vote_candidate is not Const.AGENT_NONE:
                return Content(VoteContentBuilder(self.vote_candidate))
        return Const.CONTENT_SKIP
