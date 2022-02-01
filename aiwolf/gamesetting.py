"""
gamesetting.py

(c) 2022 OTSUKI Takashi

"""
from typing import Dict, TypedDict

from aiwolf.agent import Role


class GameSetting0(TypedDict):
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
    def __init__(self, game_settin0: GameSetting0) -> None:
        self.enable_no_attack: bool = game_settin0["enableNoAttack"]
        self.enable_no_execution: bool = game_settin0["enableNoExecution"]
        self.enable_role_request: bool = game_settin0["enableRoleRequest"]
        self.max_attack_revote: int = game_settin0["maxAttackRevote"]
        self.max_revote: int = game_settin0["maxRevote"]
        self.max_skip: int = game_settin0["maxSkip"]
        self.max_talk: int = game_settin0["maxTalk"]
        self.max_talk_turn: int = game_settin0["maxTalkTurn"]
        self.max_whisper: int = game_settin0["maxWhisper"]
        self.max_whisper_turn: int = game_settin0["maxWhisperTurn"]
        self.player_num: int = game_settin0["playerNum"]
        self.random_seed: int = game_settin0["randomSeed"]
        self.role_num_map: Dict[Role, int] = {Role[k]: v for k, v in game_settin0["roleNumMap"].items()}
        self.talk_on_first_day: bool = game_settin0["talkOnFirstDay"]
        self.time_limit: int = game_settin0["timeLimit"]
        self.validate_utterance: bool = game_settin0["validateUtterance"]
        self.votable_on_first_day: bool = game_settin0["votableInFirstDay"]
        self.vote_visible: bool = game_settin0["voteVisible"]
        self.whisper_before_revote: bool = game_settin0["whisperBeforeRevote"]
