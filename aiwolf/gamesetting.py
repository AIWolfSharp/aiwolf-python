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
        self.enable_no_attack: bool = game_setting["enableNoAttack"]
        """Whether or not the game permit to attack no one."""

        self.enable_no_execution: bool = game_setting["enableNoExecution"]
        """Whether or not executing nobody is allowed."""

        self.enable_role_request: bool = game_setting["enableRoleRequest"]
        """Whether or not role request is allowed."""

        self.max_attack_revote: int = game_setting["maxAttackRevote"]
        """The maximum number of revotes for attack."""

        self.max_revote: int = game_setting["maxRevote"]
        """The maximum number of revotes."""

        self.max_skip: int = game_setting["maxSkip"]
        """The maximum permissible length of the succession of SKIPs."""

        self.max_talk: int = game_setting["maxTalk"]
        """The maximum number of talks."""

        self.max_talk_turn: int = game_setting["maxTalkTurn"]
        """The maximum number of turns of talk."""

        self.max_whisper: int = game_setting["maxWhisper"]
        """The maximum number of whispers a day."""

        self.max_whisper_turn: int = game_setting["maxWhisperTurn"]
        """The maximum number of turns of whisper."""

        self.player_num: int = game_setting["playerNum"]
        """The number of players."""

        self.random_seed: int = game_setting["randomSeed"]
        """The random seed."""

        self.role_num_map: Dict[Role, int] = {Role[k]: v for k, v in game_setting["roleNumMap"].items()}
        """The number of each role."""

        self.talk_on_first_day: bool = game_setting["talkOnFirstDay"]
        """Whether or not there are talks on the first day."""

        self.time_limit: int = game_setting["timeLimit"]
        """The upper limit for the response time to the request."""

        self.validate_utterance: bool = game_setting["validateUtterance"]
        """Whether or not the uttered text is validated."""

        self.votable_on_first_day: bool = game_setting["votableInFirstDay"]
        """Whether or not there is vote on the first day."""

        self.vote_visible: bool = game_setting["voteVisible"]
        """Whether or not agent can see who vote to who."""

        self.whisper_before_revote: bool = game_setting["whisperBeforeRevote"]
        """Whether or not werewolf can whisper before the revote for attack."""
