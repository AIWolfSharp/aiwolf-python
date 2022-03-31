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
"""gameinfo module."""
from typing import Dict, List, Optional, TypedDict

from aiwolf.agent import Agent, Role, Status
from aiwolf.judge import Judge, _Judge
from aiwolf.utterance import Talk, Whisper, _Utterance
from aiwolf.vote import Vote, _Vote


class _GameInfo(TypedDict):
    agent: int
    attackVoteList: List[_Vote]
    attackedAgent: int
    cursedFox: int
    day: int
    divineResult: _Judge
    executedAgent: int
    existingRoleList: List[str]
    guardedAgent: int
    lastDeadAgentList: List[int]
    latestAttackVoteList: List[_Vote]
    latestExecutedAgent: int
    latestVoteList: List[_Vote]
    mediumResult: _Judge
    remainTalkMap: Dict[str, int]
    remainWhisperMap: Dict[str, int]
    roleMap: Dict[str, str]
    statusMap: Dict[str, str]
    talkList: List[_Utterance]
    voteList: List[_Vote]
    whisperList: List[_Utterance]


class GameInfo:
    """Class for game information."""

    me: Agent
    """The agent who recieves this GameInfo."""
    attack_vote_list: List[Vote]
    """The list of votes for attack."""
    attacked_agent: Optional[Agent]
    """The agent decided to be attacked as a result of werewolves' vote."""
    cursed_fox: Optional[Agent]
    """The fox killed by curse."""
    day: int
    """Current day."""
    divine_result: Optional[Judge]
    """The result of the dvination."""
    executed_agent: Optional[Agent]
    """The agent executed last night."""
    existing_role_list: List[Role]
    """The list of existing roles in this game."""
    guarded_agent: Optional[Agent]
    """The agent guarded last night."""
    last_dead_agent_list: List[Agent]
    """The list of agents who died last night."""
    latest_attack_vote_list: List[Vote]
    """The latest list of votes for attack."""
    latest_executed_agent: Optional[Agent]
    """The latest executed agent."""
    latest_vote_list: List[Vote]
    """The latest list of votes for execution."""
    medium_result: Optional[Judge]
    """The result of the inquest."""
    remain_talk_map: Dict[Agent, int]
    """The number of opportunities to talk remaining."""
    remain_whisper_map: Dict[Agent, int]
    """The number of opportunities to whisper remaining."""
    role_map: Dict[Agent, Role]
    """The known roles of agents."""
    status_map: Dict[Agent, Status]
    """The statuses of all agents."""
    talk_list: List[Talk]
    """The list of today's talks."""
    vote_list: List[Vote]
    """The list of votes for execution."""
    whisper_list: List[Whisper]
    """The list of today's whispers."""

    def __init__(self, game_info: _GameInfo) -> None:
        """Initializes a new instance of GameInfo.

        Args:
            game_info: The _GameInfo used for initialization.
        """
        self.me = Agent(game_info["agent"])
        self.attack_vote_list = [Vote.compile(v) for v in game_info["attackVoteList"]]
        self.attacked_agent = GameInfo._get_agent(game_info["attackedAgent"])
        self.cursed_fox = GameInfo._get_agent(game_info["cursedFox"])
        self.day = game_info["day"]
        self.divine_result = Judge.compile(game_info["divineResult"]) if game_info["divineResult"] is not None else None
        self.executed_agent = GameInfo._get_agent(game_info["executedAgent"])
        self.existing_role_list = [Role[r] for r in game_info["existingRoleList"]]
        self.guarded_agent = GameInfo._get_agent(game_info["guardedAgent"])
        self.last_dead_agent_list = [Agent(a) for a in game_info["lastDeadAgentList"]]
        self.latest_attack_vote_list = [Vote.compile(v) for v in game_info["latestAttackVoteList"]]
        self.latest_executed_agent = GameInfo._get_agent(game_info["latestExecutedAgent"])
        self.latest_vote_list = [Vote.compile(v) for v in game_info["latestVoteList"]]
        self.medium_result = Judge.compile(game_info["mediumResult"]) if game_info["mediumResult"] is not None else None
        self.remain_talk_map = {Agent(int(k)): v for k, v in game_info["remainTalkMap"].items()}
        self.remain_whisper_map = {Agent(int(k)): v for k, v in game_info["remainWhisperMap"].items()}
        self.role_map = {Agent(int(k)): Role[v] for k, v in game_info["roleMap"].items()}
        self.status_map = {Agent(int(k)): Status[v] for k, v in game_info["statusMap"].items()}
        self.talk_list = [Talk.compile(u) for u in game_info["talkList"]]
        self.vote_list = [Vote.compile(v) for v in game_info["voteList"]]
        self.whisper_list = [Whisper.compile(u) for u in game_info["whisperList"]]

    @staticmethod
    def _get_agent(idx: int) -> Optional[Agent]:
        return None if idx < 0 else Agent(idx)

    @property
    def agent_list(self) -> List[Agent]:
        """The list of existing agents."""
        return list(self.status_map.keys())

    @property
    def my_role(self) -> Role:
        """The role of the player who receives this GameInfo."""
        return self.role_map[self.me]
