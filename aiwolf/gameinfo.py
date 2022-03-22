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

    def __init__(self, game_info: _GameInfo) -> None:
        """Initializes a new instance of GameInfo.

        Args:
            game_info: The _GameInfo used for initialization.
        """
        self._me: Agent = Agent(game_info["agent"])
        self._attack_vote_list: List[Vote] = [Vote.compile(v) for v in game_info["attackVoteList"]]
        self._attacked_agent: Optional[Agent] = GameInfo._get_agent(game_info["attackedAgent"])
        self._cursed_fox: Optional[Agent] = GameInfo._get_agent(game_info["cursedFox"])
        self._day: int = game_info["day"]
        self._divine_result: Optional[Judge] = Judge.compile(game_info["divineResult"]) if game_info["divineResult"] is not None else None
        self._executed_agent: Optional[Agent] = GameInfo._get_agent(game_info["executedAgent"])
        self._existing_role_list: List[Role] = [Role[r] for r in game_info["existingRoleList"]]
        self._guarded_agent: Optional[Agent] = GameInfo._get_agent(game_info["guardedAgent"])
        self._last_dead_agent_list: List[Agent] = [Agent(a) for a in game_info["lastDeadAgentList"]]
        self._latest_attack_vote_list: List[Vote] = [Vote.compile(v) for v in game_info["latestAttackVoteList"]]
        self._latest_executed_agent: Optional[Agent] = GameInfo._get_agent(game_info["latestExecutedAgent"])
        self._latest_vote_list: List[Vote] = [Vote.compile(v) for v in game_info["latestVoteList"]]
        self._medium_result: Optional[Judge] = Judge.compile(game_info["mediumResult"]) if game_info["mediumResult"] is not None else None
        self._remain_talk_map: Dict[Agent, int] = {Agent(int(k)): v for k, v in game_info["remainTalkMap"].items()}
        self._remain_whisper_map: Dict[Agent, int] = {Agent(int(k)): v for k, v in game_info["remainWhisperMap"].items()}
        self._role_map: Dict[Agent, Role] = {Agent(int(k)): Role[v] for k, v in game_info["roleMap"].items()}
        self._status_map: Dict[Agent, Status] = {Agent(int(k)): Status[v] for k, v in game_info["statusMap"].items()}
        self._talk_list: List[Talk] = [Talk.compile(u) for u in game_info["talkList"]]
        self._vote_list: List[Vote] = [Vote.compile(v) for v in game_info["voteList"]]
        self._whisper_list: List[Whisper] = [Whisper.compile(u) for u in game_info["whisperList"]]

    @staticmethod
    def _get_agent(idx: int) -> Optional[Agent]:
        return None if idx < 0 else Agent(idx)

    @property
    def me(self) -> Agent:
        """The agent who recieves this GameInfo."""
        return self._me

    @property
    def agent_list(self) -> List[Agent]:
        """The list of existing agents."""
        return list(self._status_map.keys())

    @property
    def my_role(self) -> Role:
        """The role of the player who receives this GameInfo."""
        return self._role_map[self._me]

    @property
    def attack_vote_list(self) -> List[Vote]:
        """The list of votes for attack."""
        return self._attack_vote_list

    @property
    def attacked_agent(self) -> Optional[Agent]:
        """The agent decided to be attacked as a result of werewolves' vote."""
        return self._attacked_agent

    @property
    def cursed_fox(self) -> Optional[Agent]:
        """The fox killed by curse."""
        return self._cursed_fox

    @property
    def day(self) -> int:
        """Current day."""
        return self._day

    @property
    def divine_result(self) -> Optional[Judge]:
        """The result of the dvination."""
        return self._divine_result

    @property
    def executed_agent(self) -> Optional[Agent]:
        """The agent executed last night."""
        return self._executed_agent

    @property
    def existing_role_list(self) -> List[Role]:
        """The list of existing roles in this game."""
        return self._existing_role_list

    @property
    def guarded_agent(self) -> Optional[Agent]:
        """The agent guarded last night."""
        return self._guarded_agent

    @property
    def last_dead_agent_list(self) -> List[Agent]:
        """The list of agents who died last night."""
        return self._last_dead_agent_list

    @property
    def latest_attack_vote_list(self) -> List[Vote]:
        """The latest list of votes for attack."""
        return self._latest_attack_vote_list

    @property
    def latest_executed_agent(self) -> Optional[Agent]:
        """The latest executed agent."""
        return self._latest_executed_agent

    @property
    def latest_vote_list(self) -> List[Vote]:
        """The latest list of votes for execution."""
        return self._latest_vote_list

    @property
    def medium_result(self) -> Optional[Judge]:
        """The result of the inquest."""
        return self._medium_result

    @property
    def remain_talk_map(self) -> Dict[Agent, int]:
        """The number of opportunities to talk remaining."""
        return self._remain_talk_map

    @property
    def remain_whisper_map(self) -> Dict[Agent, int]:
        """The number of opportunities to whisper remaining."""
        return self._remain_whisper_map

    @property
    def role_map(self) -> Dict[Agent, Role]:
        """The known roles of agents."""
        return self._role_map

    @property
    def status_map(self) -> Dict[Agent, Status]:
        """The statuses of all agents."""
        return self._status_map

    @property
    def talk_list(self) -> List[Talk]:
        """The list of today's talks."""
        return self._talk_list

    @property
    def vote_list(self) -> List[Vote]:
        """The list of votes for execution."""
        return self._vote_list

    @property
    def whisper_list(self) -> List[Whisper]:
        """The list of today's whispers."""
        return self._whisper_list
