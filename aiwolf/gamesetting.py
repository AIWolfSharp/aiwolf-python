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

    enable_no_attack: bool
    """Whether or not the game permit to attack no one."""
    enable_no_execution: bool
    """Whether or not executing nobody is allowed."""
    enable_role_request: bool
    """Whether or not role request is allowed."""
    max_attack_revote: int
    """The maximum number of revotes for attack."""
    max_revote: int
    """The maximum number of revotes."""
    max_skip: int
    """The maximum permissible length of the succession of SKIPs."""
    max_talk: int
    """The maximum number of talks."""
    max_talk_turn: int
    """The maximum number of turns of talk."""
    max_whisper: int
    """The maximum number of whispers a day."""
    max_whisper_turn: int
    """The maximum number of turns of whisper."""
    player_num: int
    """The number of players."""
    random_seed: int
    """The random seed."""
    role_num_map: Dict[Role, int]
    """The number of each role."""
    talk_on_first_day: bool
    """Whether or not there are talks on the first day."""
    time_limit: int
    """The upper limit for the response time to the request."""
    validate_utterance: bool
    """Whether or not the uttered text is validated."""
    votable_on_first_day: bool
    """Whether or not there is vote on the first day."""
    vote_visible: bool
    """Whether or not agent can see who vote to who."""
    whisper_before_revote: bool
    """Whether or not werewolf can whisper before the revote for attack."""

    def __init__(self, game_setting: _GameSetting) -> None:
        """Initializes a new instance of GameSetting.

        Args:
            game_setting: The _GameSetting used for initialization.
        """
        self.enable_no_attack = game_setting["enableNoAttack"]
        self.enable_no_execution = game_setting["enableNoExecution"]
        #リモートサーバーでenableRoleRequestが送られてこないので、ない場合にエラーにならないように対応
        if "enableRoleRequest" in game_setting:
            self.enable_role_request = game_setting["enableRoleRequest"]
        else:
            self.enable_role_request = False
        self.max_attack_revote = game_setting["maxAttackRevote"]
        self.max_revote = game_setting["maxRevote"]
        self.max_skip = game_setting["maxSkip"]
        self.max_talk = game_setting["maxTalk"]
        self.max_talk_turn = game_setting["maxTalkTurn"]
        self.max_whisper = game_setting["maxWhisper"]
        self.max_whisper_turn = game_setting["maxWhisperTurn"]
        self.player_num = game_setting["playerNum"]
        self.random_seed = game_setting["randomSeed"]
        self.role_num_map = {Role[k]: v for k, v in game_setting["roleNumMap"].items()}
        self.talk_on_first_day = game_setting["talkOnFirstDay"]
        self.time_limit = game_setting["timeLimit"]
        self.validate_utterance = game_setting["validateUtterance"]
        self.votable_on_first_day = game_setting["votableInFirstDay"]
        self.vote_visible = game_setting["voteVisible"]
        self.whisper_before_revote = game_setting["whisperBeforeRevote"]
