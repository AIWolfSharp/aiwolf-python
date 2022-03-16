#
# gamesetting.py
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
"""gamesetting module."""
from typing import Dict, TypedDict

from aiwolf.agent import Role


class _GameSetting(TypedDict):
    enableNoAttack: bool
    enableNoExecution: bool
    enableRoleRequest: bool
    maxAttackRevote: int
    maxRevote: int
    maxSkip: int
    maxTalk: int
    maxTalkTurn: int
    maxWhisper: int
    maxWhisperTurn: int
    playerNum: int
    randomSeed: int
    roleNumMap: Dict[str, int]
    talkOnFirstDay: bool
    timeLimit: int
    validateUtterance: bool
    votableInFirstDay: bool
    voteVisible: bool
    whisperBeforeRevote: bool


class GameSetting:
    """Class for game settings."""

    def __init__(self, game_setting: _GameSetting) -> None:
        """Initializes a new instance of GameSetting.

        Args:
            game_setting: The _GameSetting used for initialization.
        """
        self._enable_no_attack: bool = game_setting["enableNoAttack"]
        self._enable_no_execution: bool = game_setting["enableNoExecution"]
        self._enable_role_request: bool = game_setting["enableRoleRequest"]
        self._max_attack_revote: int = game_setting["maxAttackRevote"]
        self._max_revote: int = game_setting["maxRevote"]
        self._max_skip: int = game_setting["maxSkip"]
        self._max_talk: int = game_setting["maxTalk"]
        self._max_talk_turn: int = game_setting["maxTalkTurn"]
        self._max_whisper: int = game_setting["maxWhisper"]
        self._max_whisper_turn: int = game_setting["maxWhisperTurn"]
        self._player_num: int = game_setting["playerNum"]
        self._random_seed: int = game_setting["randomSeed"]
        self._role_num_map: Dict[Role, int] = {Role[k]: v for k, v in game_setting["roleNumMap"].items()}
        self._talk_on_first_day: bool = game_setting["talkOnFirstDay"]
        self._time_limit: int = game_setting["timeLimit"]
        self._validate_utterance: bool = game_setting["validateUtterance"]
        self._votable_on_first_day: bool = game_setting["votableInFirstDay"]
        self._vote_visible: bool = game_setting["voteVisible"]
        self._whisper_before_revote: bool = game_setting["whisperBeforeRevote"]

    @property
    def enable_no_attack(self) -> bool:
        """Whether or not the game permit to attack no one."""
        return self._enable_no_attack

    @property
    def enable_no_execution(self) -> bool:
        """Whether or not executing nobody is allowed."""
        return self._enable_no_execution

    @property
    def enable_role_request(self) -> bool:
        """Whether or not role request is allowed."""
        return self._enable_role_request

    @property
    def max_attack_revote(self) -> int:
        """The maximum number of revotes for attack."""
        return self._max_attack_revote

    @property
    def max_revote(self) -> int:
        """The maximum number of revotes."""
        return self._max_revote

    @property
    def max_skip(self) -> int:
        """The maximum permissible length of the succession of SKIPs."""
        return self._max_skip

    @property
    def max_talk(self) -> int:
        """The maximum number of talks."""
        return self._max_talk

    @property
    def max_talk_turn(self) -> int:
        """The maximum number of turns of talk."""
        return self._max_talk_turn

    @property
    def max_whisper(self) -> int:
        """The maximum number of whispers a day."""
        return self._max_whisper

    @property
    def max_whisper_turn(self) -> int:
        """The maximum number of turns of whisper."""
        return self._max_whisper_turn

    @property
    def player_num(self) -> int:
        """The number of players."""
        return self._player_num

    @property
    def random_seed(self) -> int:
        """The random seed."""
        return self._random_seed

    @property
    def role_num_map(self) -> Dict[Role, int]:
        """The number of each role."""
        return self._role_num_map

    @property
    def talk_on_first_day(self) -> bool:
        """Whether or not there are talks on the first day."""
        return self._talk_on_first_day

    @property
    def time_limit(self) -> int:
        """The upper limit for the response time to the request."""
        return self._time_limit

    @property
    def validate_utterance(self) -> bool:
        """Whether or not the uttered text is validated."""
        return self._validate_utterance

    @property
    def votable_on_first_day(self) -> bool:
        """Whether or not there is vote on the first day."""
        return self._votable_on_first_day

    @property
    def vote_visible(self) -> bool:
        """Whether or not agent can see who vote to who."""
        return self._vote_visible

    @property
    def whisper_before_revote(self) -> bool:
        """Whether or not werewolf can whisper before the revote for attack."""
        return self._whisper_before_revote
