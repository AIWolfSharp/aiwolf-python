#
# constant.py
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
"""constant module."""
import warnings
from typing import Final

from aiwolf.agent import Agent

AGENT_NONE: Final[Agent] = Agent(0)
AGENT_UNSPEC: Final[Agent] = AGENT_NONE
AGENT_ANY: Final[Agent] = Agent(0xff)


class Constant:
    """Constant class that defines some constants."""

    warnings.warn("Constant class will be deprecated in the next version.", PendingDeprecationWarning)

    AGENT_NONE: Final[Agent] = Agent(0)
    """Agent that does not exisit in this game."""

    AGENT_UNSPEC: Final[Agent] = AGENT_NONE
    """Agent that means no agent specified. (Alias of AGENT_NONE)"""

    AGENT_ANY: Final[Agent] = Agent(0xff)
    """Agent that means any of the agents in this game."""
