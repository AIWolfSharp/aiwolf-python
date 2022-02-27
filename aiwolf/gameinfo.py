#
# gameinfo.py
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

from typing import Dict, List, Optional, TypedDict

from aiwolf.agent import Agent, Role, Status
from aiwolf.judge import Judge, Judge0
from aiwolf.utterance import Talk, Utterance0, Whisper
from aiwolf.vote import Vote, Vote0


class GameInfo0(TypedDict):
    agent: int
    attackVoteList: List[Vote0]
    attackedAgent: int
    cursedFox: int
    day: int
    divineResult: Judge0
    executedAgent: int
    existingRoleList: List[str]
    guardedAgent: int
    lastDeadAgentList: List[int]
    latestAttackVoteList: List[Vote0]
    latestExecutedAgent: int
    latestVoteList: List[Vote0]
    mediumResult: Judge0
    remainTalkMap: Dict[str, int]
    remainWhisperMap: Dict[str, int]
    roleMap: Dict[str, str]
    statusMap: Dict[str, str]
    talkList: List[Utterance0]
    voteList: List[Vote0]
    whisperList: List[Utterance0]


class GameInfo:
    def __init__(self, game_info0: GameInfo0) -> None:
        self.agent: Agent = Agent(game_info0["agent"])
        self.attack_vote_list: List[Vote] = [Vote.compile(v) for v in game_info0["attackVoteList"]]
        self.attacked_agent: Optional[Agent] = GameInfo.get_agent(game_info0["attackedAgent"])
        self.cursed_fox: Optional[Agent] = GameInfo.get_agent(game_info0["cursedFox"])
        self.day: int = game_info0["day"]
        self.divine_result: Optional[Judge] = Judge.compile(game_info0["divineResult"]) if game_info0["divineResult"] is not None else None
        self.executed_agent: Optional[Agent] = GameInfo.get_agent(game_info0["executedAgent"])
        self.existing_role_list: List[Role] = [Role[r] for r in game_info0["existingRoleList"]]
        self.guarded_agent: Optional[Agent] = GameInfo.get_agent(game_info0["guardedAgent"])
        self.last_dead_agent_list: List[Agent] = [Agent(a) for a in game_info0["lastDeadAgentList"]]
        self.latest_attack_vote_list: List[Vote] = [Vote.compile(v) for v in game_info0["latestAttackVoteList"]]
        self.latest_executed_agent: Optional[Agent] = GameInfo.get_agent(game_info0["latestExecutedAgent"])
        self.latest_vote_list: List[Vote] = [Vote.compile(v) for v in game_info0["latestVoteList"]]
        self.medium_result: Optional[Judge] = Judge.compile(game_info0["mediumResult"]) if game_info0["mediumResult"] is not None else None
        self.remain_talk_map: Dict[Agent, int] = {Agent(int(k)): v for k, v in game_info0["remainTalkMap"].items()}
        self.remain_whisper_map: Dict[Agent, int] = {Agent(int(k)): v for k, v in game_info0["remainWhisperMap"].items()}
        self.role_map: Dict[Agent, Role] = {Agent(int(k)): Role[v] for k, v in game_info0["roleMap"].items()}
        self.status_map: Dict[Agent, Status] = {Agent(int(k)): Status[v] for k, v in game_info0["statusMap"].items()}
        self.talk_list: List[Talk] = [Talk.compile(u) for u in game_info0["talkList"]]
        self.vote_list: List[Vote] = [Vote.compile(v) for v in game_info0["voteList"]]
        self.whisper_list: List[Whisper] = [Whisper.compile(u) for u in game_info0["whisperList"]]

    @staticmethod
    def get_agent(idx: int) -> Optional[Agent]:
        return None if idx < 0 else Agent(idx)
