#
# villager.py
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
from typing import Dict, List, Optional

from aiwolf.agent import Agent, Role, Species, Status
from aiwolf.content import Content, Topic, VoteContentBuilder
from aiwolf.gameinfo import GameInfo
from aiwolf.gamesetting import GameSetting
from aiwolf.judge import Judge
from aiwolf.player import AbstractPlayer
from aiwolf.utterance import Talk
from const import Const


class SampleVillager(AbstractPlayer):
    """ サンプル村人エージェント """

    def __init__(self) -> None:
        self.me: Agent = Const.AGENT_NONE  # 自分
        self.vote_candidate: Agent = Const.AGENT_NONE  # 投票先
        self.game_info: Optional[GameInfo] = None  # ゲーム情報
        self.comingout_map: Dict[Agent, Role] = {}  # カミングアウト状況
        self.divination_reports: List[Judge] = []  # 占い結果報告時系列
        self.identification_reports: List[Judge] = []  # 霊媒結果報告時系列
        self.talk_list_head: int = 0  # 未解析会話の先頭インデックス
        self.agent_list: List[Agent] = []  # 全エージェントのリスト

    def is_alive(self, agent: Agent) -> bool:
        """ エージェントが生きているかどうか """
        return self.game_info is not None and self.game_info.status_map[agent] is Status.ALIVE

    def get_others(self, agent_list: List[Agent]) -> List[Agent]:
        """ エージェントリストから自分を除いたリストを返す """
        return [a for a in agent_list if a is not self.me]

    def get_alive(self, agent_list: List[Agent]) -> List[Agent]:
        """ エージェントリスト中の生存エージェントのリストを返す """
        return [a for a in agent_list if self.is_alive(a)]

    def get_alive_others(self, agent_list: List[Agent]) -> List[Agent]:
        """ エージェントリスト中の自分以外の生存エージェントのリストを返す """
        return self.get_alive(self.get_others(agent_list))

    def random_select(self, agent_list: List[Agent]) -> Agent:
        """ エージェントのリストからランダムに1エージェントを選んで返す """
        return random.choice(agent_list) if agent_list else Const.AGENT_NONE

    def initialize(self, game_info: GameInfo, game_setting: GameSetting) -> None:
        self.game_info = game_info
        self.me = game_info.me
        self.agent_list = list(game_info.status_map.keys())
        # 前のゲームを引きずらないようにフィールドをクリアしておく
        self.comingout_map = {}
        self.divination_reports = []
        self.identification_reports = []

    def day_start(self) -> None:
        self.talk_list_head = 0
        self.vote_candidate = Const.AGENT_NONE

    def update(self, game_info: GameInfo) -> None:
        self.game_info = game_info  # ゲーム状況更新
        for i in range(self.talk_list_head, len(game_info.talk_list)):  # 未解析発話の解析
            tk: Talk = game_info.talk_list[i]  # 解析対象会話
            talker: Agent = tk.agent
            if talker is self.me:  # 自分の発言は解析しない
                continue
            content: Content = Content.compile(tk.text)
            if content.topic is Topic.COMINGOUT:
                self.comingout_map[talker] = content.role
            elif content.topic is Topic.DIVINED:
                self.divination_reports.append(Judge(talker, game_info.day, content.target, content.result))
            elif content.topic is Topic.IDENTIFIED:
                self.identification_reports.append(Judge(talker, game_info.day, content.target, content.result))
        self.talk_list_head = len(game_info.talk_list)  # すべてを解析済みとする

    def talk(self) -> Content:
        # 会話をしながら投票先を決めていく
        #
        # 村人である自分を人狼と判定した偽占い師のリスト
        fake_seers: List[Agent] = [j.agent for j in self.divination_reports if j.target is self.me and j.result is Species.WEREWOLF]
        # 偽でない自称占い師から人狼と判定された生存エージェントに投票
        reported_wolves: List[Agent] = [j.target for j in self.divination_reports if j.agent not in fake_seers and j.result is Species.WEREWOLF]
        candidates: List[Agent] = self.get_alive_others(reported_wolves)
        # いなければ生存偽占い師に投票
        if not candidates:
            candidates = self.get_alive(fake_seers)
        # それでもいなければ生存エージェントに投票
        if not candidates:
            candidates = self.get_alive_others(self.agent_list)
        # 初めての投票先宣言あるいは変更ありの場合，投票先宣言
        if self.vote_candidate is Const.AGENT_NONE or self.vote_candidate not in candidates:
            self.vote_candidate = self.random_select(list(set(candidates)))
            if self.vote_candidate is not Const.AGENT_NONE:
                return Content(VoteContentBuilder(self.vote_candidate))
        return Const.CONTENT_SKIP

    def vote(self) -> Agent:
        return self.vote_candidate if self.vote_candidate is not Const.AGENT_NONE else self.me

    def attack(self) -> Agent:
        raise Exception("Unexpected function call")  # 誤使用の場合例外送出

    def divine(self) -> Agent:
        raise Exception("Unexpected function call")  # 誤使用の場合例外送出

    def guard(self) -> Agent:
        raise Exception("Unexpected function call")  # 誤使用の場合例外送出

    def whisper(self) -> Content:
        raise Exception("Unexpected function call")  # 誤使用の場合例外送出

    def finish(self) -> None:
        pass
