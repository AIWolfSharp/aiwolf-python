#
# content.py
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
"""content module."""
from __future__ import annotations

import copy
import re
from enum import Enum
from typing import ClassVar, List, Match, Optional, Pattern

from aiwolf.agent import Agent, Role, Species
from aiwolf.constant import AGENT_ANY, AGENT_NONE, AGENT_UNSPEC
from aiwolf.utterance import Talk, Utterance, UtteranceType, Whisper


class Content:
    """Content class expressing the content of an uteerance."""

    topic: Topic
    """The topic of this Content."""
    subject: Agent
    """The Agent that is the subject of this Content."""
    target: Agent
    """The Agent that is the object of this Content."""
    role: Role
    """The role this Content refers to."""
    result: Species
    """The species this Content refers to."""
    utterance: Utterance
    """The utterance this Content refers to."""
    operator: Operator
    """The operator in this Content."""
    content_list: List[Content]
    """The list of the operands in this Content."""
    day: int
    """The date added to the operand in this Content."""
    text: str
    """The text representing this Content."""

    @staticmethod
    def _get_contents(input: str) -> List[Content]:
        return [Content.compile(s) for s in Content._get_content_strings(input)]

    @staticmethod
    def _get_content_strings(input: str) -> List[str]:
        strings: List[str] = []
        length: int = len(input)
        stack_ptr: int = 0
        start: int = 0
        for i in range(0, length):
            if input[i] == "(":
                if stack_ptr == 0:
                    start = i
                stack_ptr += 1
            elif input[i] == ")":
                stack_ptr -= 1
                if stack_ptr == 0:
                    strings.append(input[start+1:i])
        return strings

    def __init__(self, builder: ContentBuilder) -> None:
        """Initialize a new instance of Content.

        Args:
            builder: A ContentBuilder used for initialization.
        """
        self.topic = builder._topic
        self.subject = builder._subject
        self.target = builder._target
        self.role = builder._role
        self.result = builder._result
        self.utterance = builder._utterance
        self.operator = builder._operator
        self.content_list = builder._content_list
        self.day = builder._day
        self.text = builder._text
        self._complete_inner_subject()
        self._normalize_text()

    def _complete_inner_subject(self) -> None:
        if not self.content_list:
            return
        self.content_list = [self._process_inner_content(c) for c in self.content_list]

    def _process_inner_content(self, inner: Content) -> Content:
        if inner.subject is AGENT_UNSPEC:
            if self.operator is Operator.INQUIRE or self.operator is Operator.REQUEST:
                return inner._copy_and_replace_subject(self.target)
            if self.subject is not AGENT_UNSPEC:
                return inner._copy_and_replace_subject(self.subject)
        inner._complete_inner_subject()
        return inner

    def _copy_and_replace_subject(self, new_subject: Agent) -> Content:
        c: Content = self.clone()
        c.subject = new_subject
        c._complete_inner_subject()
        c._normalize_text()
        return c

    def _normalize_text(self) -> None:
        str_sub: str = "" if self.subject is AGENT_UNSPEC else "ANY " if self.subject is AGENT_ANY else str(self.subject)+" "
        str_tgt: str = "ANY" if self.target is AGENT_ANY or self.target is AGENT_UNSPEC else str(self.target)
        if self.topic is not Topic.OPERATOR:
            if self.topic is Topic.DUMMY:
                self.text = ""
            elif self.topic is Topic.RAW:
                pass
            elif self.topic is Topic.Skip:
                self.text = Utterance.SKIP
            elif self.topic is Topic.Over:
                self.text = Utterance.OVER
            elif self.topic is Topic.AGREE or self.topic is Topic.DISAGREE:
                self.text = str_sub + " ".join([self.topic.value, "TALK" if type(self.utterance) is Talk else "WHISPER", str(self.utterance.day), str(self.utterance.idx)])
            elif self.topic is Topic.ESTIMATE or self.topic is Topic.COMINGOUT:
                self.text = str_sub + " ".join([self.topic.value, str_tgt, self.role.value])
            elif self.topic is Topic.DIVINED or self.topic is Topic.IDENTIFIED:
                self.text = str_sub + " ".join([self.topic.value, str_tgt, self.result.value])
            elif self.topic is Topic.ATTACK or self.topic is Topic.ATTACKED or self.topic is Topic.DIVINATION or self.topic is Topic.GUARD\
                    or self.topic is Topic.GUARDED or self.topic is Topic.VOTE or self.topic is Topic.VOTED:
                self.text = str_sub + " ".join([self.topic.value, str_tgt])
        else:
            if self.operator is Operator.REQUEST or self.operator is Operator.INQUIRE:
                self.text = str_sub + " ".join([self.operator.value, str_tgt, "("+Content._strip_subject(self.content_list[0].text) +
                                                ")" if self.content_list[0].subject is self.target else "("+self.content_list[0].text+")"])
            elif self.operator is Operator.BECAUSE or self.operator is Operator.XOR:
                self.text = str_sub + " ".join([self.operator.value] + ["("+Content._strip_subject(self.content_list[i].text) +
                                                                        ")" if self.content_list[i].subject is self.subject else "("+self.content_list[i].text+")" for i in [0, 1]])
            elif self.operator is Operator.AND or self.operator is Operator.OR:
                self.text = str_sub + " ".join([self.operator.value] + ["("+Content._strip_subject(c.text)+")" if c.subject is self.subject else "("+c.text+")" for c in self.content_list])
            elif self.operator is Operator.NOT:
                self.text = str_sub + " ".join([self.operator.value, "("+Content._strip_subject(self.content_list[0].text) +
                                                ")" if self.content_list[0].subject is self.subject else "("+self.content_list[0].text+")"])
            elif self.operator is Operator.DAY:
                self.text = str_sub + " ".join([self.operator.value, str(self.day), "("+Content._strip_subject(self.content_list[0].text) +
                                                ")" if self.content_list[0].subject is self.subject else "("+self.content_list[0].text+")"])

    _strip_pattern: ClassVar[Pattern[str]] = re.compile(r"^(Agent\[\d+\]|ANY|)\s*([A-Z]+.*)$")

    @staticmethod
    def _strip_subject(input: str) -> str:
        m: Optional[Match[str]] = Content._strip_pattern.match(input)
        if m:
            return m.group(2)
        return input

    def clone(self) -> Content:
        """Clone this Content.

        Returns:
            The cloned Content.
        """
        content: Content = copy.copy(self)
        content.utterance = copy.copy(self.utterance)
        content.content_list = [c.clone() for c in self.content_list]
        return content

    _regex_agent: ClassVar[str] = r"\s+(Agent\[\d+\]|ANY)"
    _regex_subject: ClassVar[str] = r"^(Agent\[\d+\]|ANY|)\s*"
    _regex_talk: ClassVar[str] = r"\s+([A-Z]+)\s+day(\d+)\s+ID:(\d+)"
    _regex_role_species: ClassVar[str] = r"\s+([A-Z]+)"
    _regex_paren: ClassVar[str] = r"(\(.*\))"
    _regex_digit: ClassVar[str] = r"(\d+)"
    _agree_pattern: ClassVar[Pattern[str]] = re.compile(_regex_subject + "(AGREE|DISAGREE)" + _regex_talk + "$")
    _estimate_pattern: ClassVar[Pattern[str]] = re.compile(_regex_subject + "(ESTIMATE|COMINGOUT)" + _regex_agent + _regex_role_species + "$")
    _divined_pattern: ClassVar[Pattern[str]] = re.compile(_regex_subject + "(DIVINED|IDENTIFIED)" + _regex_agent + _regex_role_species + "$")
    _attack_pattern: ClassVar[Pattern[str]] = re.compile(_regex_subject + "(ATTACK|ATTACKED|DIVINATION|GUARD|GUARDED|VOTE|VOTED)" + _regex_agent + "$")
    _request_pattern: ClassVar[Pattern[str]] = re.compile(_regex_subject + "(REQUEST|INQUIRE)" + _regex_agent + r"\s+" + _regex_paren + "$")
    _because_pattern: ClassVar[Pattern[str]] = re.compile(_regex_subject + r"(BECAUSE|AND|OR|XOR|NOT|REQUEST)\s+" + _regex_paren + "$")
    _day_pattern: ClassVar[Pattern[str]] = re.compile(_regex_subject + r"DAY\s+" + _regex_digit + r"\s+" + _regex_paren + "$")
    _skip_pattern: ClassVar[Pattern[str]] = re.compile("^(Skip|Over)$")

    @staticmethod
    def compile(text: str) -> Content:
        """Convert the uttered text into a Content.

        Args:
            text: The uttered text.

        Returns:
            The Content converted from the given text.
        """
        trimmed: str = text.strip()
        m_agree: Optional[Match[str]] = Content._agree_pattern.match(trimmed)
        m_estimate: Optional[Match[str]] = Content._estimate_pattern.match(trimmed)
        m_divined: Optional[Match[str]] = Content._divined_pattern.match(trimmed)
        m_attack: Optional[Match[str]] = Content._attack_pattern.match(trimmed)
        m_request: Optional[Match[str]] = Content._request_pattern.match(trimmed)
        m_because: Optional[Match[str]] = Content._because_pattern.match(trimmed)
        m_day: Optional[Match[str]] = Content._day_pattern.match(trimmed)
        m_skip: Optional[Match[str]] = Content._skip_pattern.match(trimmed)
        content: Content = Content(SkipContentBuilder())
        if m_skip:
            content.topic = Topic[m_skip.group(1)]
        elif m_agree:
            content.subject = Agent.compile(m_agree.group(1))
            content.topic = Topic[m_agree.group(2)]
            if UtteranceType[m_agree.group(3)] is UtteranceType.TALK:
                content.utterance = Talk(int(m_agree.group(5)), AGENT_NONE, int(m_agree.group(4)), "", 0)
            else:
                content.utterance = Whisper(int(m_agree.group(5)), AGENT_NONE, int(m_agree.group(4)), "", 0)
        elif m_estimate:
            content.subject = Agent.compile(m_estimate.group(1))
            content.topic = Topic[m_estimate.group(2)]
            content.target = Agent.compile(m_estimate.group(3))
            content.role = Role[m_estimate.group(4)]
        elif m_divined:
            content.subject = Agent.compile(m_divined.group(1))
            content.topic = Topic[m_divined.group(2)]
            content.target = Agent.compile(m_divined.group(3))
            content.result = Species[m_divined.group(4)]
        elif m_attack:
            content.subject = Agent.compile(m_attack.group(1))
            content.topic = Topic[m_attack.group(2)]
            content.target = Agent.compile(m_attack.group(3))
        elif m_request:
            content.topic = Topic.OPERATOR
            content.subject = Agent.compile(m_request.group(1))
            content.operator = Operator[m_request.group(2)]
            content.target = Agent.compile(m_request.group(3))
            content.content_list = Content._get_contents(m_request.group(4))
        elif m_because:
            content.topic = Topic.OPERATOR
            content.subject = Agent.compile(m_because.group(1))
            content.operator = Operator[m_because.group(2)]
            content.content_list = Content._get_contents(m_because.group(3))
            if content.operator is Operator.REQUEST:
                content.target = AGENT_ANY if content.content_list[0].subject is AGENT_UNSPEC else content.content_list[0].subject
        elif m_day:
            content.topic = Topic.OPERATOR
            content.subject = Agent.compile(m_day.group(1))
            content.operator = Operator.DAY
            content.day = int(m_day.group(2))
            content.content_list = Content._get_contents(m_day.group(3))
        else:
            content.topic = Topic.Skip
        content._complete_inner_subject()
        content._normalize_text()
        return content

    def equals(self, other: Content) -> bool:
        """Show whether or not the given Content is equivalent to this Content.

        Args:
            other: The Content to be compared.

        Returns:
            True if other is equivalent to this, otherwise false.
        """
        return self.text == other.text

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, Content):
            return NotImplemented
        return self is __o or self.text == __o.text


class Topic(Enum):
    """Enumeration type for topic."""

    DUMMY = "DUMMY"
    """Dummy topic."""

    ESTIMATE = "ESTIMATE"
    """Estimation."""

    COMINGOUT = "COMINGOUT"
    """Comingout."""

    DIVINATION = "DIVINATION"
    """Divination."""

    DIVINED = "DIVINED"
    """Report of a divination."""

    IDENTIFIED = "IDENTIFIED"
    """Report of an identification."""

    GUARD = "GUARD"
    """Guard."""

    GUARDED = "GUARDED"
    """Report of a guard."""

    VOTE = "VOTE"
    """Vote."""

    VOTED = "VOTED"
    """Report of a vote."""

    ATTACK = "ATTACK"
    """Attack."""

    ATTACKED = "ATTACKED"
    """Report of an attack."""

    AGREE = "AGREE"
    """Agreement."""

    DISAGREE = "DISAGREE"
    """Disagreement."""

    Over = "Over"
    """There is nothing to talk/whisper."""

    Skip = "Skip"
    """Skip this turn."""

    OPERATOR = "OPERATOR"
    """Operator."""

    RAW = "RAW"
    """Containing raw text."""


class Operator(Enum):
    """Enumeration type for operator."""

    NOP = "NOP"
    """No operation."""

    REQUEST = "REQUEST"
    """Request for the action."""

    INQUIRE = "INQUIRE"
    """Inquiry."""

    BECAUSE = "BECAUSE"
    """Reason for the action."""

    DAY = "DAY"
    """DATE."""

    NOT = "NOT"
    """Negation."""

    AND = "AND"
    """Conjunctive clause."""

    OR = "OR"
    """Disjunctive clause."""

    XOR = "XOR"
    """Exclusive disjunctive clause."""


class ContentBuilder:
    """A class for the builder classes to build Content of all kinds."""

    _subject: Agent
    _target: Agent
    _topic: Topic
    _role: Role
    _result: Species
    _utterance: Utterance
    _operator: Operator
    _content_list: List[Content]
    _day: int
    _text: str

    def __init__(self) -> None:
        """Initialize a new instance of ContentBuilder."""
        self._subject = AGENT_UNSPEC
        self._target = AGENT_ANY
        self._topic = Topic.DUMMY
        self._role = Role.UNC
        self._result = Species.UNC
        self._utterance = Utterance()
        self._operator = Operator.NOP
        self._content_list = []
        self._day = -1
        self._text = ""


class AgreeContentBuilder(ContentBuilder):
    """Builder class for agreeing to the utterance."""

    def __init__(self, utterance_type: UtteranceType, day: int, idx: int, *, subject: Agent = AGENT_UNSPEC) -> None:
        """Initialize a new instance of AgreeContentBuilder.

        Args:
            utterance_type: The type of the utterance.
            day: The date of the utterance.
            idx: The index number of the utterance.
            subject(optional): The agent that agrees. Defaults to AGENT_UNSPEC.
        """
        super().__init__()
        self._topic = Topic.AGREE
        self._subject = subject
        if utterance_type is UtteranceType.TALK:
            self._utterance = Talk(day, AGENT_NONE, idx, "", 0)
        else:
            self._utterance = Whisper(day, AGENT_NONE, idx, "", 0)


class DisagreeContentBuilder(AgreeContentBuilder):
    """Builder class for disagreeing to the utterance."""

    def __init__(self, utterance_type: UtteranceType, day: int, idx: int, *, subject: Agent = AGENT_UNSPEC) -> None:
        """Initialize a new instance of DisagreeContentBuilder.

        Args:
            utterance_type: The type of the utterance.
            day: The date of the utterance.
            idx: The index number of the utterance.
            subject(optional): The agent that disagrees. Defaults to AGENT_UNSPEC.
        """
        super().__init__(utterance_type, day, idx, subject=subject)
        self._topic = Topic.DISAGREE


class AttackContentBuilder(ContentBuilder):
    """Builder class for expressing the will to attack."""

    def __init__(self, target: Agent, *, subject: Agent = AGENT_UNSPEC) -> None:
        """Initialize a new instance of AttackContentBuilder.

        Args:
            target: The agent the utterer wants to attack.
            subject(optional): The agent that expresses the will to attack. Defaults to AGENT_UNSPEC.
        """
        super().__init__()
        self._topic = Topic.ATTACK
        self._subject = subject
        self._target = target


class AttackedContentBuilder(AttackContentBuilder):
    """Builder class for the report of an attack."""

    def __init__(self, target: Agent, *, subject: Agent = AGENT_UNSPEC) -> None:
        """Initialize a new instance of AttackedContentBuilder.

        Args:
            target: The attacked agent.
            subject(optional): The agent that reports the attack. Defaults to AGENT_UNSPEC.
        """
        super().__init__(target, subject=subject)
        self._topic = Topic.ATTACKED


class DivinationContentBuilder(AttackContentBuilder):
    """Builder class for expressing a divination."""

    def __init__(self, target: Agent, *, subject: Agent = AGENT_UNSPEC) -> None:
        """Initialize a new instance of DivinationContentBuilder.

        Args:
            target: The agent that is an object of the divination.
            subject(optional): The agent that does the divination. Defaults to AGENT_UNSPEC.
        """
        super().__init__(target, subject=subject)
        self._topic = Topic.DIVINATION


class DivinedResultContentBuilder(ContentBuilder):
    """Builder class for the report of a divination."""

    def __init__(self, target: Agent, result: Species, *, subject: Agent = AGENT_UNSPEC) -> None:
        """Initialize a new instance of DivinedResultContentBuilder.

        Args:
            target: The agent that was an object of the divination.
            result: The species as the result of the divination.
            subject(optional): The agent that did the divination. Defaults to AGENT_UNSPEC.
        """
        super().__init__()
        self._topic = Topic.DIVINED
        self._subject = subject
        self._target = target
        self._result = result


class GuardContentBuilder(AttackContentBuilder):
    """Builder class for expressing a guard."""

    def __init__(self, target: Agent, *, subject: Agent = AGENT_UNSPEC) -> None:
        """Initialize a new instance of GuardContentBuilder.

        Args:
            target: The agent to be guarded.
            subject(optional): The agent that guards. Defaults to AGENT_UNSPEC.
        """
        super().__init__(target, subject=subject)
        self._topic = Topic.GUARD


class GuardedAgentContentBuilder(AttackContentBuilder):
    """Builder class for the report of a guard."""

    def __init__(self, target: Agent, *, subject: Agent = AGENT_UNSPEC) -> None:
        """Initialize a new instance of GurdedAgentContentBuilder.

        Args:
            target: The agent that was guarded.
            subject(optional): The agent that guarded. Defaults to AGENT_UNSPEC.
        """
        super().__init__(target, subject=subject)
        self._topic = Topic.GUARDED


class VoteContentBuilder(AttackContentBuilder):
    """Builder class for expressing a vote."""

    def __init__(self, target: Agent, *, subject: Agent = AGENT_UNSPEC) -> None:
        """Initialize a new instance of VoteContentBuilder.

        Args:
            target: The agent to be voted on.
            subject(optional): The agent that votes. Defaults to AGENT_UNSPEC.
        """
        super().__init__(target, subject=subject)
        self._topic = Topic.VOTE


class VotedContentBuilder(AttackContentBuilder):
    """Builder class for the report of a vote."""

    def __init__(self, target: Agent, *, subject: Agent = AGENT_UNSPEC) -> None:
        """Initialize a new instance of VotedContentBuilder.

        Args:
            target: The agent that was voted on.
            subject(optional): The agent that voted. Defaults to AGENT_UNSPEC.
        """
        super().__init__(target, subject=subject)
        self._topic = Topic.VOTED


class ComingoutContentBuilder(ContentBuilder):
    """Builder class for expressing a comingout."""

    def __init__(self, target: Agent, role: Role, *, subject: Agent = AGENT_UNSPEC) -> None:
        """Initialize a new instance of ComingoutContentBuilder.

        Args:
            target: The agent that is an object of the comingout.
            role: The role that is an object of the comingout.
            subject(optional): The agent that does the comingout. Defaults to AGENT_UNSPEC.
        """
        super().__init__()
        self._topic = Topic.COMINGOUT
        self._subject = subject
        self._target = target
        self._role = role


class EstimateContentBuilder(ComingoutContentBuilder):
    """Builder class for expressing a estimation."""

    def __init__(self, target: Agent, role: Role, *, subject: Agent = AGENT_UNSPEC) -> None:
        """Initialize a new instance of EstimateContentBuilder.

        Args:
            target: The agent that is an object of the estimation.
            role: The estimated role of the agent.
            subject(optional): The agent that estimates. Defaults to AGENT_UNSPEC.
        """
        super().__init__(target, role, subject=subject)
        self._topic = Topic.ESTIMATE


class IdentContentBuilder(DivinedResultContentBuilder):
    """Builder class for the report of an identification."""

    def __init__(self, target: Agent, result: Species, *, subject: Agent = AGENT_UNSPEC) -> None:
        """Initialize a new instance of IdentContentBuilder.

        Args:
            target: The agent that was an object of the identification.
            result: The species of the agent revealed as a result of the identification.
            subject(optional): The agent that did the identification. Defaults to AGENT_UNSPEC.
        """
        super().__init__(target, result, subject=subject)
        self._topic = Topic.IDENTIFIED


class RequestContentBuilder(ContentBuilder):
    """Builder class for expressing a request."""

    def __init__(self, target: Agent, action: Content, *, subject: Agent = AGENT_UNSPEC) -> None:
        """Initialize a new instance of RequestContentBuilder.

        Args:
            target: The agent that is an object of the request.
            action: The requested action.
            subject(optional): The agent that requests. Defaults to AGENT_UNSPEC.
        """
        super().__init__()
        self._topic = Topic.OPERATOR
        self._operator = Operator.REQUEST
        self._subject = subject
        self._target = target
        self._content_list.append(action.clone())


class InquiryContentBuilder(RequestContentBuilder):
    """Builder class for expressing an inquiry."""

    def __init__(self, target: Agent, action: Content, *, subject: Agent = AGENT_UNSPEC) -> None:
        """Initialize a new instance of InquiryContentBuilder.

        Args:
            target: The agent that reveives the inquiry.
            action: The matter inquired.
            subject(optional): The agent that makes the inquiry. Defaults to AGENT_UNSPEC.
        """
        super().__init__(target, action, subject=subject)
        self._operator = Operator.INQUIRE


class BecauseContentBuilder(ContentBuilder):
    """Builder class for expressing a reason."""

    def __init__(self, reason: Content, action: Content, *, subject: Agent = AGENT_UNSPEC) -> None:
        """Initialize a new instance of BecauseContentBuilder.

        Args:
            reason: The reason for the action.
            action: The action based on the reason.
            subject(optional): The agent that expresses the action and its reason. Defaults to AGENT_UNSPEC.
        """
        super().__init__()
        self._topic = Topic.OPERATOR
        self._operator = Operator.BECAUSE
        self._subject = subject
        self._content_list.append(reason.clone())
        self._content_list.append(action.clone())


class AndContentBuilder(ContentBuilder):
    """Builder class for expressing a conjunctive clause."""

    def __init__(self, contents: List[Content], *, subject: Agent = AGENT_UNSPEC) -> None:
        """Initialize a new instance of AndContentBuilder.

        Args:
            contents: The series of the conjuncts.
            subject(optional): The agent that expresses the conjunctie clause. Defaults to AGENT_UNSPEC.

        Raises:
            ValueError: In case of empty conjuncts, ValueError is raised.
        """
        super().__init__()
        self._topic = Topic.OPERATOR
        self._operator = Operator.AND
        self._subject = subject
        if not contents:
            raise ValueError("Invalid argument: contents is empty")
        self._content_list.extend([c.clone() for c in contents])


class OrContentBuilder(AndContentBuilder):
    """Builder class for expressing a disjunctive clause."""

    def __init__(self, contents: List[Content], *, subject: Agent = AGENT_UNSPEC) -> None:
        """Initialize a new instance of OrContentBuilder.

        Args:
            contents: The series of the disjuncts.
            subject(optional): The agent that expresses the disjunctive clause. Defaults to AGENT_UNSPEC.
        """
        super().__init__(contents, subject=subject)
        self._operator = Operator.OR


class XorContentBuilder(BecauseContentBuilder):
    """Builder class for expressing a exclusive disjunctive clause."""

    def __init__(self, disjunct1: Content, disjunct2: Content, *, subject: Agent = AGENT_UNSPEC) -> None:
        """Initialize a new instance of XorContentBuilder.

        Args:
            disjunct1: The first disjunct.
            disjunct2: The second disjunct.
            subject(optional): The agent that expresses the exclusive disjunctive clause. Defaults to AGENT_UNSPEC.
        """
        super().__init__(disjunct1, disjunct2, subject=subject)
        self._operator = Operator.XOR


class NotContentBuilder(ContentBuilder):
    """Builder class for expressing a negation."""

    def __init__(self, content: Content, *, subject: Agent = AGENT_UNSPEC) -> None:
        """Initialize a new instance of NotContentBuilder.

        Args:
            content: The content to be negated.
            subject(optional): The agent that expresses the negation. Defaults to AGENT_UNSPEC.
        """
        super().__init__()
        self._topic = Topic.OPERATOR
        self._operator = Operator.NOT
        self._subject = subject
        self._content_list.append(content.clone())


class DayContentBuilder(ContentBuilder):
    """Builder class for adding a date to the Content."""

    def __init__(self, day: int, content: Content, *, subject: Agent = AGENT_UNSPEC) -> None:
        """Initialize a new instance of DayContentBuilder.

        Args:
            day: The date of the Content.
            content: The content to which the date is added.
            subject(optional): The agent that adds the date to the Content. Defaults to AGENT_UNSPEC.
        """
        super().__init__()
        self._topic = Topic.OPERATOR
        self._operator = Operator.DAY
        self._subject = subject
        self._day = day
        self._content_list.append(content.clone())


class SkipContentBuilder(ContentBuilder):
    """Builder class for the skip of this turn's utterance."""

    def __init__(self) -> None:
        """Initialize a new instance of SkipContentBuilder."""
        super().__init__()
        self._topic = Topic.Skip


class OverContentBuilder(ContentBuilder):
    """Builder class for expressing that there is nothing to utter."""

    def __init__(self) -> None:
        """Initialize a new instance of OverContentBuilder."""
        super().__init__()
        self._topic = Topic.Over


class RawContentBuilder(ContentBuilder):
    """Builder class for expressing an raw text."""

    def __init__(self, text: str) -> None:
        """Initialize a new instance of RawContentBuilder."""
        super().__init__()
        self._topic = Topic.RAW
        self._text = text

class EmptyContentBuilder(ContentBuilder):
    """Builder class for expressing an empty Content."""

    def __init__(self) -> None:
        """Initialize a new instance of EmptyContentBuilder."""
        super().__init__()
        self._topic = Topic.DUMMY
