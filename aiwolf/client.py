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
from typing import List, Optional, TypedDict

from aiwolf.gameinfo import GameInfo, _GameInfo
from aiwolf.gamesetting import GameSetting, _GameSetting
from aiwolf.player import AbstractPlayer
from aiwolf.utterance import Talk, Whisper, _Utterance


class _Packet(TypedDict):
    gameInfo: Optional[_GameInfo]
    gameSetting: Optional[_GameSetting]
    request: str
    talkHistory: Optional[List[_Utterance]]
    whisperHistory: Optional[List[_Utterance]]


class TcpipClient:
    """Client agent that communiates with the server via TCP/IP connection."""

    player: AbstractPlayer
    name: Optional[str]
    host: str
    port: int
    request_role: str
    game_info: Optional[GameInfo]
    last_game_info: Optional[GameInfo]
    sock: Optional[socket.socket]

    def __init__(self, player: AbstractPlayer, name: Optional[str], host: str, port: int, request_role: str, total_games:int = 5) -> None:
        """Initialize a new instance of TcpipClient.

        Args:
            player: An AbstractPlayer to be connect with the server.
            name: The name of the player agent.
            host: The hostname of the server.
            port: The port number the server is waiting on.
            request_role: The name of role that the player agent wants to be.
            total_games: The number of games to be played.
        """
        self.player = player
        self.name = name
        self.host = host
        self.port = port
        self.request_role = request_role
        self.game_info = None
        self.last_game_info = None
        self.sock = None

        self.total_games = total_games
        self.game_start_count = 0
        self.game_end_count = 0
        


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
        talk_history0: Optional[List[_Utterance]] = packet["talkHistory"]
        if talk_history0 is not None:
            for talk0 in talk_history0:
                talk: Talk = Talk.compile(talk0)
                talk_list: List[Talk] = self.game_info.talk_list
                if len(talk_list) == 0:
                    talk_list.append(talk)
                else:
                    last_talk: Talk = talk_list[-1]
                    if talk.day > last_talk.day or (talk.day == last_talk.day and talk.idx > last_talk.idx):
                        talk_list.append(talk)
        whisper_history0: Optional[List[_Utterance]] = packet["whisperHistory"]
        if whisper_history0 is not None:
            for whisper0 in whisper_history0:
                whisper: Whisper = Whisper.compile(whisper0)
                whisper_list: List[Whisper] = self.game_info.whisper_list
                if len(whisper_list) == 0:
                    whisper_list.append(whisper)
                else:
                    last_whisper: Whisper = whisper_list[-1]
                    if whisper.day > last_whisper.day or (whisper.day == last_whisper.day and whisper.idx > last_whisper.idx):
                        whisper_list.append(whisper)
        if request == "INITIALIZE":
            self.game_start_count += 1 #ゲームが始まったらカウントを増やす
            
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
                if self.game_start_count -1 == self.game_end_count:
                    self.game_end_count += 1 #ゲームが終わったらカウントを増やす
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

    def _is_json_complate(self,responses:bytes) -> bool:
        try:
            responses = responses.decode("utf-8")
        except:
            return False
        
        if responses == "":
            return False

        cnt = 0

        for word in responses:
            if word == "{":
                cnt += 1
            elif word == "}":
                cnt -= 1
        
        return cnt == 0
    
    def _get_json(self) -> str:
        responses = b""
        retry_count = 0
        max_retry_count = 1e5
        while not self._is_json_complate(responses=responses):  
            response = self.sock.recv(8192)
            #待機時間が長いときは、一定回数以上のリトライを許容する        
            if response == b"":
                retry_count += 1
                if retry_count > max_retry_count:
                    raise RuntimeError("socket connection broken")
            else:
                retry_count = 0
            
            responses += response

        return responses.decode("utf-8")

    def connect(self) -> None:
        """Connect to the server."""
        # socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(10)
        # connect
        self.sock.connect((self.host, self.port))
        
        while self.game_end_count < self.total_games:
            json_str = self._get_json()
            if json_str == "":
                break
        
            line_list = json_str.split("\n")
            for one_line in line_list:
                if len(one_line) > 0:
                    json_received = json.loads(one_line)
                    self._send_response(self._get_response(json_received))

        self.sock.close()
                
        return None