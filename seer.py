#
# seer.py
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

from queue import Queue
from typing import List, Optional

from aiwolf.agent import Agent, Role, Species
from aiwolf.content import (ComingoutContentBuilder, Content,
                            DivinedResultContentBuilder, VoteContentBuilder)
from aiwolf.gameinfo import GameInfo
from aiwolf.gamesetting import GameSetting
from aiwolf.judge import Judge
from const import Const
from villager import SampleVillager


class SampleSeer(SampleVillager):
    """ サンプル占い師エージェント """

    def __init__(self) -> None:
        super().__init__()
        self.co_date: int = 3  # CO予定日
        self.has_co: bool = False  # CO済ならTrue
        self.my_judge_queue: Queue[Judge] = Queue()  # 占い結果の待ち行列
        self.not_divined_agents: List[Agent] = []  # 未占いエージェント
        self.werewolves: List[Agent] = []  # 見つけた人狼

    def initialize(self, game_info: GameInfo, game_setting: GameSetting) -> None:
        super().initialize(game_info, game_setting)
        self.has_co = False
        self.my_judge_queue = Queue()
        self.not_divined_agents = self.get_others(self.agent_list)
        self.werewolves = []

    def day_start(self) -> None:
        super().day_start()
        # 占い結果の処理
        judge: Optional[Judge] = None if self.game_info is None else self.game_info.divine_result
        if judge is not None:
            self.my_judge_queue.put(judge)
            if judge.target in self.not_divined_agents:
                self.not_divined_agents.remove(judge.target)
            if judge.result is Species.WEREWOLF:
                self.werewolves.append(judge.target)

    def talk(self) -> Content:
        if self.game_info is None:
            return Const.CONTENT_SKIP
        # 予定日あるいは人狼を発見したらCO
        if not self.has_co and (self.game_info.day == self.co_date or self.werewolves):
            self.has_co = True
            return Content(ComingoutContentBuilder(self.me, Role.SEER))
        # CO後は占い結果を報告
        if self.has_co and not self.my_judge_queue.empty():
            judge: Judge = self.my_judge_queue.get()
            return Content(DivinedResultContentBuilder(judge.target, judge.result))
        # 生存人狼に投票
        candidates: List[Agent] = self.get_alive(self.werewolves)
        # いなければ生存偽占い師に投票
        if not candidates:
            candidates = self.get_alive([a for a in self.comingout_map.keys() if self.comingout_map[a] is Role.SEER])
        # それでもいなければ生存エージェントに投票
        if not candidates:
            candidates = self.get_alive_others(self.agent_list)
        # 初めての投票先宣言あるいは変更ありの場合，投票先宣言
        if self.vote_candidate is Const.AGENT_NONE or self.vote_candidate not in candidates:
            self.vote_candidate = self.random_select(candidates)
            if self.vote_candidate is not Const.AGENT_NONE:
                return Content(VoteContentBuilder(self.vote_candidate))
        return Const.CONTENT_SKIP

    def divine(self) -> Agent:
        # まだ占っていないエージェントからランダムに占う
        target: Agent = self.random_select(self.not_divined_agents)
        return target if target is not Const.AGENT_NONE else self.me
