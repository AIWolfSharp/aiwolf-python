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
from typing import Optional, TypedDict

from aiwolf.agent import Agent, Role, Status
from aiwolf.judge import Judge, _Judge
from aiwolf.utterance import Talk, Whisper, _Utterance
from aiwolf.vote import Vote, _Vote


class _GameInfo(TypedDict):
    agent: int
    attackVoteList: list[_Vote]
    attackedAgent: int
    cursedFox: int
    day: int
    divineResult: _Judge
    executedAgent: int
    existingRoleList: list[str]
    guardedAgent: int
    lastDeadAgentList: list[int]
    latestAttackVoteList: list[_Vote]
    latestExecutedAgent: int
    latestVoteList: list[_Vote]
    mediumResult: _Judge
    remainTalkMap: dict[str, int]
    remainWhisperMap: dict[str, int]
    roleMap: dict[str, str]
    statusMap: dict[str, str]
    talkList: list[_Utterance]
    voteList: list[_Vote]
    whisperList: list[_Utterance]


class GameInfo:
    """Class for game information."""

    def __init__(self, game_info: _GameInfo) -> None:
        """Initializes a new instance of GameInfo.

        Args:
            game_info: The _GameInfo used for initialization.
        """
        self.me: Agent = Agent(game_info["agent"])
        """The agent who recieves this GameInfo."""

        self.attack_vote_list: list[Vote] = [Vote.compile(v) for v in game_info["attackVoteList"]]
        """The list of votes for attack."""

        self.attacked_agent: Optional[Agent] = GameInfo._get_agent(game_info["attackedAgent"])
        """The agent decided to be attacked as a result of werewolves' vote."""

        self.cursed_fox: Optional[Agent] = GameInfo._get_agent(game_info["cursedFox"])
        """The fox killed by curse."""

        self.day: int = game_info["day"]
        """Current day."""

        self.divine_result: Optional[Judge] = Judge.compile(game_info["divineResult"]) if game_info["divineResult"] is not None else None
        """The result of the dvination."""

        self.executed_agent: Optional[Agent] = GameInfo._get_agent(game_info["executedAgent"])
        """The agent executed last night."""

        self.existing_role_list: list[Role] = [Role[r] for r in game_info["existingRoleList"]]
        """The list of existing roles in this game."""

        self.guarded_agent: Optional[Agent] = GameInfo._get_agent(game_info["guardedAgent"])
        """The agent guarded last night."""

        self.last_dead_agent_list: list[Agent] = [Agent(a) for a in game_info["lastDeadAgentList"]]
        """The list of agents who died last night."""

        self.latest_attack_vote_list: list[Vote] = [Vote.compile(v) for v in game_info["latestAttackVoteList"]]
        """The latest list of votes for attack."""

        self.latest_executed_agent: Optional[Agent] = GameInfo._get_agent(game_info["latestExecutedAgent"])
        """The latest executed agent."""

        self.latest_vote_list: list[Vote] = [Vote.compile(v) for v in game_info["latestVoteList"]]
        """The latest list of votes for execution."""

        self.medium_result: Optional[Judge] = Judge.compile(game_info["mediumResult"]) if game_info["mediumResult"] is not None else None
        """The result of the inquest."""

        self.remain_talk_map: dict[Agent, int] = {Agent(int(k)): v for k, v in game_info["remainTalkMap"].items()}
        """The number of opportunities to talk remaining."""

        self.remain_whisper_map: dict[Agent, int] = {Agent(int(k)): v for k, v in game_info["remainWhisperMap"].items()}
        """The number of opportunities to whisper remaining."""

        self.role_map: dict[Agent, Role] = {Agent(int(k)): Role[v] for k, v in game_info["roleMap"].items()}
        """The known roles of agents."""

        self.status_map: dict[Agent, Status] = {Agent(int(k)): Status[v] for k, v in game_info["statusMap"].items()}
        """The statuses of all agents."""

        self.talk_list: list[Talk] = [Talk.compile(u) for u in game_info["talkList"]]
        """The list of today's talks."""

        self.vote_list: list[Vote] = [Vote.compile(v) for v in game_info["voteList"]]
        """The list of votes for execution."""

        self.whisper_list: list[Whisper] = [Whisper.compile(u) for u in game_info["whisperList"]]
        """The list of today's whispers."""

    @staticmethod
    def _get_agent(idx: int) -> Optional[Agent]:
        return None if idx < 0 else Agent(idx)

    @property
    def agent_list(self) -> list[Agent]:
        """The list of existing agents."""
        return list(self.status_map.keys())

    @property
    def alive_agent_list(self) -> list[Agent]:
        """The list of alive agents."""
        return [i[0] for i in self.status_map.items() if i[1] == Status.ALIVE]

    @property
    def my_role(self) -> Role:
        """The role of the player who receives this GameInfo."""
        return self.role_map[self.me]
