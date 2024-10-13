#
# client.py
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
"""client module."""
import json
import socket
from typing import Optional, TypedDict

from aiwolf.gameinfo import GameInfo, _GameInfo
from aiwolf.gamesetting import GameSetting, _GameSetting
from aiwolf.player import AbstractPlayer
from aiwolf.utterance import Talk, Whisper, _Utterance


class _Packet(TypedDict):
    gameInfo: Optional[_GameInfo]
    gameSetting: Optional[_GameSetting]
    request: str
    talkHistory: Optional[list[_Utterance]]
    whisperHistory: Optional[list[_Utterance]]


class TcpipClient:
    """Client agent that communiates with the server via TCP/IP connection."""

    def __init__(self, player: AbstractPlayer, name: Optional[str], host: str, port: int, request_role: str) -> None:
        """Initialize a new instance of TcpipClient.

        Args:
            player: An AbstractPlayer to be connect with the server.
            name: The name of the player agent.
            host: The hostname of the server.
            port: The port number the server is waiting on.
            request_role: The name of role that the player agent wants to be.
        """
        self.player: AbstractPlayer = player
        self.name: Optional[str] = name
        self.host: str = host
        self.port: int = port
        self.request_role: str = request_role
        self.game_info: Optional[GameInfo] = None
        self.last_game_info: Optional[GameInfo] = None
        self.sock: Optional[socket.socket] = None

    def _send_response(self, response: Optional[str]) -> None:
        if isinstance(self.sock, socket.socket) and isinstance(response, str):
            self.sock.send((response + "\n").encode("utf-8"))

    def _get_response(self, packet: _Packet) -> Optional[str]:
        request: str = packet["request"]
        if request == "NAME":
            return self.name if self.name is not None else self.player.get_name()
        elif request == "ROLE":
            return self.request_role
        game_info0: Optional[_GameInfo] = packet["gameInfo"]
        self.game_info = GameInfo(game_info0) if game_info0 is not None else None
        if self.game_info is None:
            self.game_info = self.last_game_info
        else:
            self.last_game_info = self.game_info
        if self.game_info is None:
            return None
        talk_history0: Optional[list[_Utterance]] = packet["talkHistory"]
        if talk_history0 is not None:
            for talk0 in talk_history0:
                talk: Talk = Talk.compile(talk0)
                talk_list: list[Talk] = self.game_info.talk_list
                if len(talk_list) == 0:
                    talk_list.append(talk)
                else:
                    last_talk: Talk = talk_list[-1]
                    if talk.day > last_talk.day or (talk.day == last_talk.day and talk.idx > last_talk.idx):
                        talk_list.append(talk)
        whisper_history0: Optional[list[_Utterance]] = packet["whisperHistory"]
        if whisper_history0 is not None:
            for whisper0 in whisper_history0:
                whisper: Whisper = Whisper.compile(whisper0)
                whisper_list: list[Whisper] = self.game_info.whisper_list
                if len(whisper_list) == 0:
                    whisper_list.append(whisper)
                else:
                    last_whisper: Whisper = whisper_list[-1]
                    if whisper.day > last_whisper.day or (whisper.day == last_whisper.day and whisper.idx > last_whisper.idx):
                        whisper_list.append(whisper)
        if request == "INITIALIZE":
            game_setting0: Optional[_GameSetting] = packet["gameSetting"]
            if game_setting0 is not None:
                self.player.initialize(self.game_info, GameSetting(game_setting0))
            return None
        else:
            self.player.update(self.game_info)
            if request == "DAILY_INITIALIZE":
                self.player.day_start()
                return None
            elif request == "DAILY_FINISH":
                return None
            elif request == "FINISH":
                self.player.finish()
                return None
            elif request == "VOTE":
                return json.dumps({"agentIdx": self.player.vote().agent_idx}, separators=(",", ":"))
            elif request == "ATTACK":
                return json.dumps({"agentIdx": self.player.attack().agent_idx}, separators=(",", ":"))
            elif request == "GUARD":
                return json.dumps({"agentIdx": self.player.guard().agent_idx}, separators=(",", ":"))
            elif request == "DIVINE":
                return json.dumps({"agentIdx": self.player.divine().agent_idx}, separators=(",", ":"))
            elif request == "TALK":
                return self.player.talk().text
            elif request == "WHISPER":
                return self.player.whisper().text
            return None

    def connect(self) -> None:
        """Connect to the server."""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(0.001)
        self.sock.connect((self.host, self.port))
        line: str = ""
        while True:
            try:
                line += self.sock.recv(8192).decode("utf-8")
                if line == "":
                    break
            except socket.timeout:
                pass
            line_list: list[str] = line.split("\n", 1)
            for i in range(len(line_list) - 1):
                if len(line_list[i]) > 0:
                    self._send_response(self._get_response(json.loads(line_list[i])))
                line = line_list[-1]
            try:
                self._send_response(self._get_response(json.loads(line)))
                line = ""
            except ValueError:
                pass
        self.sock.close()
        return None
