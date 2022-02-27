#
# medium.py
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
                            IdentContentBuilder, VoteContentBuilder)
from aiwolf.gameinfo import GameInfo
from aiwolf.gamesetting import GameSetting
from aiwolf.judge import Judge
from const import Const
from villager import SampleVillager


class SampleMedium(SampleVillager):
    """ サンプル霊媒師エージェント """

    def __init__(self) -> None:
        super().__init__()
        self.co_date: int = 3  # CO予定日
        self.found_wolf: bool = False  # 人狼を発見したか
        self.has_co: bool = False  # CO済ならTrue
        self.my_judge_queue: Queue[Judge] = Queue()  # 霊媒結果の待ち行列

    def initialize(self, game_info: GameInfo, game_setting: GameSetting) -> None:
        super().initialize(game_info, game_setting)
        self.found_wolf = False
        self.has_co = False
        self.my_judge_queue = Queue()

    def day_start(self) -> None:
        super().day_start()
        # 霊媒結果を待ち行列に入れる
        judge: Optional[Judge] = None if self.game_info is None else self.game_info.medium_result
        if judge is not None:
            self.my_judge_queue.put(judge)
            if judge.result is Species.WEREWOLF:
                self.found_wolf = True

    def talk(self) -> Content:
        if self.game_info is None:
            return Const.CONTENT_SKIP
        # 予定日あるいは人狼を発見したらCO
        if not self.has_co and (self.game_info.day == self.co_date or self.found_wolf):
            self.has_co = True
            return Content(ComingoutContentBuilder(self.me, Role.MEDIUM))
        # CO後は霊能行使結果を報告
        if self.has_co and not self.my_judge_queue.empty():
            judge: Judge = self.my_judge_queue.get()
            return Content(IdentContentBuilder(judge.target, judge.result))
        # 偽占い師
        fake_seers: List[Agent] = [j.agent for j in self.divination_reports if j.target is self.me and j.result is Species.WEREWOLF]
        # 生存偽霊媒師に投票
        candidates: List[Agent] = [a for a in self.comingout_map.keys() if self.is_alive(a) and self.comingout_map[a] is Role.MEDIUM]
        # いなければ非偽自称占い師から人狼と判定された生存エージェントに投票
        reported_wolves: List[Agent] = [j.target for j in self.divination_reports if j.agent not in fake_seers and j.result is Species.WEREWOLF]
        candidates = self.get_alive_others(reported_wolves)
        # いなければ生存偽占い師に投票
        if not candidates:
            candidates = self.get_alive(fake_seers)
        # それでもいなければ生存エージェントに投票
        if not candidates:
            candidates = self.get_alive_others(self.agent_list)
        # 初めての投票先宣言あるいは変更ありの場合，投票先宣言
        if self.vote_candidate is Const.AGENT_NONE or self.vote_candidate not in candidates:
            self.vote_candidate = self.random_select(candidates)
            if self.vote_candidate is not Const.AGENT_NONE:
                return Content(VoteContentBuilder(self.vote_candidate))
        return Const.CONTENT_SKIP
