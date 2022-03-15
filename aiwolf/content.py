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

import re
from enum import Enum
from typing import List, Match, Optional, Pattern

from aiwolf.agent import Agent, Role, Species
from aiwolf.constant import Constant as C
from aiwolf.utterance import Talk, Utterance, UtteranceType, Whisper


class Content:
    """Content class expressing the content of an uteerance."""

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
        self._topic: Topic = builder._topic
        self._subject: Agent = builder._subject
        self._target: Agent = builder._target
        self._role: Role = builder._role
        self._result: Species = builder._result
        self._utterance: Utterance = builder._utterance
        self._operator: Operator = builder._operator
        self._content_list: List[Content] = builder._content_list
        self._day: int = builder._day
        self._text: str = ""
        self._complete_inner_subject()
        self._normalize_text()

    @property
    def topic(self) -> Topic:
        """The topic of this Content."""
        return self._topic

    @property
    def subject(self) -> Agent:
        """The Agent that is the subject of this Content."""
        return self._subject

    @property
    def target(self) -> Agent:
        """The Agent that is the object of this Content."""
        return self._target

    @property
    def role(self) -> Role:
        """The role this Content refers to."""
        return self._role

    @property
    def result(self) -> Species:
        """The species this Content refers to."""
        return self._result

    @property
    def utterance(self) -> Utterance:
        """The utterance this Content refers to."""
        return self._utterance

    @property
    def operator(self) -> Operator:
        """The operator in this Content."""
        return self._operator

    @property
    def content_list(self) -> List[Content]:
        """The list of the operands in this Content."""
        return self._content_list

    @property
    def day(self) -> int:
        """The date added to the operand in this Content."""
        return self._day

    @property
    def text(self) -> str:
        """The text representing this Content."""
        return self._text

    def _complete_inner_subject(self) -> None:
        if not self._content_list:
            return
        self._content_list = [self._process_inner_content(c) for c in self._content_list]

    def _process_inner_content(self, inner: Content) -> Content:
        if inner._subject is C.AGENT_UNSPEC:
            if self._operator is Operator.INQUIRE or self._operator is Operator.REQUEST:
                return inner._copy_and_replace_subject(self._target)
            if self._subject is not C.AGENT_UNSPEC:
                return inner._copy_and_replace_subject(self._subject)
        inner._complete_inner_subject()
        return inner

    def _copy_and_replace_subject(self, new_subject: Agent) -> Content:
        c: Content = self.clone()
        c._subject = new_subject
        c._complete_inner_subject()
        c._normalize_text()
        return c

    def _normalize_text(self) -> None:
        str_sub: str = "" if self._subject is C.AGENT_UNSPEC else "ANY " if self._subject is C.AGENT_ANY else str(self._subject)+" "
        str_tgt: str = "ANY" if self._target is C.AGENT_ANY or self._target is C.AGENT_UNSPEC else str(self._target)
        if self._topic is not Topic.OPERATOR:
            if self._topic is Topic.DUMMY:
                self._text = ""
            elif self._topic is Topic.Skip:
                self._text = Utterance.SKIP
            elif self._topic is Topic.Over:
                self._text = Utterance.OVER
            elif self._topic is Topic.AGREE or self._topic is Topic.DISAGREE:
                self._text = str_sub + " ".join([self._topic.value, "TALK" if type(self._utterance) is Talk else "WHISPER", str(self._utterance.day), str(self._utterance.idx)])
            elif self._topic is Topic.ESTIMATE or self._topic is Topic.COMINGOUT:
                self._text = str_sub + " ".join([self._topic.value, str_tgt, self._role.value])
            elif self._topic is Topic.DIVINED or self._topic is Topic.IDENTIFIED:
                self._text = str_sub + " ".join([self._topic.value, str_tgt, self._result.value])
            elif self._topic is Topic.ATTACK or self._topic is Topic.ATTACKED or self._topic is Topic.DIVINATION or self._topic is Topic.GUARD\
                    or self._topic is Topic.GUARDED or self._topic is Topic.VOTE or self._topic is Topic.VOTED:
                self._text = str_sub + " ".join([self._topic.value, str_tgt])
        else:
            if self._operator is Operator.REQUEST or self._operator is Operator.INQUIRE:
                self._text = str_sub + " ".join([self._operator.value, str_tgt, "("+Content._strip_subject(self._content_list[0]._text) +
                                                ")" if self._content_list[0]._subject is self._target else "("+self._content_list[0]._text+")"])
            elif self._operator is Operator.BECAUSE or self._operator is Operator.XOR:
                self._text = str_sub + " ".join([self._operator.value] + ["("+Content._strip_subject(self._content_list[i]._text) +
                                                                          ")" if self._content_list[i]._subject is self._subject else "("+self._content_list[i]._text+")" for i in [0, 1]])
            elif self._operator is Operator.AND or self._operator is Operator.OR:
                self._text = str_sub + " ".join([self._operator.value] + ["("+Content._strip_subject(c._text)+")" if c._subject is self._subject else "("+c._text+")" for c in self._content_list])
            elif self._operator is Operator.NOT:
                self._text = str_sub + " ".join([self._operator.value, "("+Content._strip_subject(self._content_list[0]._text) +
                                                ")" if self._content_list[0]._subject is self._subject else "("+self._content_list[0]._text+")"])
            elif self._operator is Operator.DAY:
                self._text = str_sub + " ".join([self._operator.value, str(self._day), "("+Content._strip_subject(self._content_list[0]._text) +
                                                ")" if self._content_list[0]._subject is self._subject else "("+self._content_list[0]._text+")"])

    _strip_pattern: Pattern[str] = re.compile(r"^(Agent\[\d+\]|ANY|)\s*([A-Z]+.*)$")

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
        content: Content = Content(ContentBuilder())
        content._topic = self._topic
        content._subject = self._subject
        content._target = self._target
        content._role = self._role
        content._result = self._result
        content._utterance = self._utterance
        content._operator = self._operator
        content._content_list = self._content_list
        content._day = self._day
        content._text = self._text
        return content

    _regex_agent: str = r"\s+(Agent\[\d+\]|ANY)"
    _regex_subject: str = r"^(Agent\[\d+\]|ANY|)\s*"
    _regex_talk: str = r"\s+([A-Z]+)\s+day(\d+)\s+ID:(\d+)"
    _regex_role_species: str = r"\s+([A-Z]+)"
    _regex_paren: str = r"(\(.*\))"
    _regex_digit: str = r"(\d+)"
    _agree_pattern: Pattern[str] = re.compile(_regex_subject + "(AGREE|DISAGREE)" + _regex_talk + "$")
    _estimate_pattern: Pattern[str] = re.compile(_regex_subject + "(ESTIMATE|COMINGOUT)" + _regex_agent + _regex_role_species + "$")
    _divined_pattern: Pattern[str] = re.compile(_regex_subject + "(DIVINED|IDENTIFIED)" + _regex_agent + _regex_role_species + "$")
    _attack_pattern: Pattern[str] = re.compile(_regex_subject + "(ATTACK|ATTACKED|DIVINATION|GUARD|GUARDED|VOTE|VOTED)" + _regex_agent + "$")
    _request_pattern: Pattern[str] = re.compile(_regex_subject + "(REQUEST|INQUIRE)" + _regex_agent + r"\s+" + _regex_paren + "$")
    _because_pattern: Pattern[str] = re.compile(_regex_subject + r"(BECAUSE|AND|OR|XOR|NOT|REQUEST)\s+" + _regex_paren + "$")
    _day_pattern: Pattern[str] = re.compile(_regex_subject + r"DAY\s+" + _regex_digit + r"\s+" + _regex_paren + "$")
    _skip_pattern: Pattern[str] = re.compile("^(Skip|Over)$")

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
            content._topic = Topic[m_skip.group(1)]
        elif m_agree:
            content._subject = Agent.compile(m_agree.group(1))
            content._topic = Topic[m_agree.group(2)]
            if UtteranceType[m_agree.group(3)] is UtteranceType.TALK:
                content._utterance = Talk(int(m_agree.group(5)), C.AGENT_NONE, int(m_agree.group(4)), "", 0)
            else:
                content._utterance = Whisper(int(m_agree.group(5)), C.AGENT_NONE, int(m_agree.group(4)), "", 0)
        elif m_estimate:
            content._subject = Agent.compile(m_estimate.group(1))
            content._topic = Topic[m_estimate.group(2)]
            content._target = Agent.compile(m_estimate.group(3))
            content._role = Role[m_estimate.group(4)]
        elif m_divined:
            content._subject = Agent.compile(m_divined.group(1))
            content._topic = Topic[m_divined.group(2)]
            content._target = Agent.compile(m_divined.group(3))
            content._result = Species[m_divined.group(4)]
        elif m_attack:
            content._subject = Agent.compile(m_attack.group(1))
            content._topic = Topic[m_attack.group(2)]
            content._target = Agent.compile(m_attack.group(3))
        elif m_request:
            content._topic = Topic.OPERATOR
            content._subject = Agent.compile(m_request.group(1))
            content._operator = Operator[m_request.group(2)]
            content._target = Agent.compile(m_request.group(3))
            content._content_list = Content._get_contents(m_request.group(4))
        elif m_because:
            content._topic = Topic.OPERATOR
            content._subject = Agent.compile(m_because.group(1))
            content._operator = Operator[m_because.group(2)]
            content._content_list = Content._get_contents(m_because.group(3))
            if content._operator is Operator.REQUEST:
                content._target = C.AGENT_ANY if content._content_list[0]._subject is C.AGENT_UNSPEC else content._content_list[0]._subject
        elif m_day:
            content._topic = Topic.OPERATOR
            content._subject = Agent.compile(m_day.group(1))
            content._operator = Operator.DAY
            content._day = int(m_day.group(2))
            content._content_list = Content._get_contents(m_day.group(3))
        else:
            content._topic = Topic.Skip
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
        return self._text == other._text


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

    def __init__(self) -> None:
        """Initialize a new instance of ContentBuilder."""
        self._subject: Agent = C.AGENT_UNSPEC
        self._target: Agent = C.AGENT_ANY
        self._topic: Topic = Topic.DUMMY
        self._role: Role = Role.UNC
        self._result: Species = Species.UNC
        self._utterance: Utterance = Utterance()
        self._operator: Operator = Operator.NOP
        self._content_list: List[Content] = []
        self._day: int = -1


class AgreeContentBuilder(ContentBuilder):
    """Builder class for agreeing to the utterance."""

    def __init__(self, utterance_type: UtteranceType, day: int, idx: int, *, subject: Agent = C.AGENT_UNSPEC) -> None:
        """Initialize a new instance of AgreeContentBuilder.

        Args:
            utterance_type: The type of the utterance.
            day: The date of the utterance.
            idx: The index number of the utterance.
            subject(optional): The agent that agrees. Defaults to C.AGENT_UNSPEC.
        """
        super().__init__()
        self._topic = Topic.AGREE
        self._subject = subject
        if utterance_type is UtteranceType.TALK:
            self._utterance = Talk(day, C.AGENT_NONE, idx, "", 0)
        else:
            self._utterance = Whisper(day, C.AGENT_NONE, idx, "", 0)


class DisagreeContentBuilder(AgreeContentBuilder):
    """Builder class for disagreeing to the utterance."""

    def __init__(self, utterance_type: UtteranceType, day: int, idx: int, *, subject: Agent = C.AGENT_UNSPEC) -> None:
        """Initialize a new instance of DisagreeContentBuilder.

        Args:
            utterance_type: The type of the utterance.
            day: The date of the utterance.
            idx: The index number of the utterance.
            subject(optional): The agent that disagrees. Defaults to C.AGENT_UNSPEC.
        """
        super().__init__(utterance_type, day, idx, subject=subject)
        self._topic = Topic.DISAGREE


class AttackContentBuilder(ContentBuilder):
    """Builder class for expressing the will to attack."""

    def __init__(self, target: Agent, *, subject: Agent = C.AGENT_UNSPEC) -> None:
        """Initialize a new instance of AttackContentBuilder.

        Args:
            target: The agent the utterer wants to attack.
            subject(optional): The agent that expresses the will to attack. Defaults to C.AGENT_UNSPEC.
        """
        super().__init__()
        self._topic = Topic.ATTACK
        self._subject = subject
        self._target = target


class AttackedContentBuilder(AttackContentBuilder):
    """Builder class for the report of an attack."""

    def __init__(self, target: Agent, *, subject: Agent = C.AGENT_UNSPEC) -> None:
        """Initialize a new instance of AttackedContentBuilder.

        Args:
            target: The attacked agent.
            subject(optional): The agent that reports the attack. Defaults to C.AGENT_UNSPEC.
        """
        super().__init__(target, subject=subject)
        self._topic = Topic.ATTACKED


class DivinationContentBuilder(AttackContentBuilder):
    """Builder class for expressing a divination."""

    def __init__(self, target: Agent, *, subject: Agent = C.AGENT_UNSPEC) -> None:
        """Initialize a new instance of DivinationContentBuilder.

        Args:
            target: The agent that is an object of the divination.
            subject(optional): The agent that does the divination. Defaults to C.AGENT_UNSPEC.
        """
        super().__init__(target, subject=subject)
        self._topic = Topic.DIVINATION


class DivinedResultContentBuilder(ContentBuilder):
    """Builder class for the report of a divination."""

    def __init__(self, target: Agent, result: Species, *, subject: Agent = C.AGENT_UNSPEC) -> None:
        """Initialize a new instance of DivinedResultContentBuilder.

        Args:
            target: The agent that was an object of the divination.
            result: The species as the result of the divination.
            subject(optional): The agent that did the divination. Defaults to C.AGENT_UNSPEC.
        """
        super().__init__()
        self._topic = Topic.DIVINED
        self._subject = subject
        self._target = target
        self._result = result


class GuardContentBuilder(AttackContentBuilder):
    """Builder class for expressing a guard."""

    def __init__(self, target: Agent, *, subject: Agent = C.AGENT_UNSPEC) -> None:
        """Initialize a new instance of GuardContentBuilder.

        Args:
            target: The agent to be guarded.
            subject(optional): The agent that guards. Defaults to C.AGENT_UNSPEC.
        """
        super().__init__(target, subject=subject)
        self._topic = Topic.GUARD


class GuardedAgentContentBuilder(AttackContentBuilder):
    """Builder class for the report of a guard."""

    def __init__(self, target: Agent, *, subject: Agent = C.AGENT_UNSPEC) -> None:
        """Initialize a new instance of GurdedAgentContentBuilder.

        Args:
            target: The agent that was guarded.
            subject(optional): The agent that guarded. Defaults to C.AGENT_UNSPEC.
        """
        super().__init__(target, subject=subject)
        self._topic = Topic.GUARDED


class VoteContentBuilder(AttackContentBuilder):
    """Builder class for expressing a vote."""

    def __init__(self, target: Agent, *, subject: Agent = C.AGENT_UNSPEC) -> None:
        """Initialize a new instance of VoteContentBuilder.

        Args:
            target: The agent to be voted on.
            subject(optional): The agent that votes. Defaults to C.AGENT_UNSPEC.
        """
        super().__init__(target, subject=subject)
        self._topic = Topic.VOTE


class VotedContentBuilder(AttackContentBuilder):
    """Builder class for the report of a vote."""

    def __init__(self, target: Agent, *, subject: Agent = C.AGENT_UNSPEC) -> None:
        """Initialize a new instance of VotedContentBuilder.

        Args:
            target: The agent that was voted on.
            subject(optional): The agent that voted. Defaults to C.AGENT_UNSPEC.
        """
        super().__init__(target, subject=subject)
        self._topic = Topic.VOTED


class ComingoutContentBuilder(ContentBuilder):
    """Builder class for expressing a comingout."""

    def __init__(self, target: Agent, role: Role, *, subject: Agent = C.AGENT_UNSPEC) -> None:
        """Initialize a new instance of ComingoutContentBuilder.

        Args:
            target: The agent that is an object of the comingout.
            role: The role that is an object of the comingout.
            subject(optional): The agent that does the comingout. Defaults to C.AGENT_UNSPEC.
        """
        super().__init__()
        self._topic = Topic.COMINGOUT
        self._subject = subject
        self._target = target
        self._role = role


class EstimateContentBuilder(ComingoutContentBuilder):
    """Builder class for expressing a estimation."""

    def __init__(self, target: Agent, role: Role, *, subject: Agent = C.AGENT_UNSPEC) -> None:
        """Initialize a new instance of EstimateContentBuilder.

        Args:
            target: The agent that is an object of the estimation.
            role: The estimated role of the agent.
            subject(optional): The agent that estimates. Defaults to C.AGENT_UNSPEC.
        """
        super().__init__(target, role, subject=subject)
        self._topic = Topic.ESTIMATE


class IdentContentBuilder(DivinedResultContentBuilder):
    """Builder class for the report of an identification."""

    def __init__(self, target: Agent, result: Species, *, subject: Agent = C.AGENT_UNSPEC) -> None:
        """Initialize a new instance of IdentContentBuilder.

        Args:
            target: The agent that was an object of the identification.
            result: The species of the agent revealed as a result of the identification.
            subject(optional): The agent that did the identification. Defaults to C.AGENT_UNSPEC.
        """
        super().__init__(target, result, subject=subject)
        self._topic = Topic.IDENTIFIED


class RequestContentBuilder(ContentBuilder):
    """Builder class for expressing a request."""

    def __init__(self, target: Agent, action: Content, *, subject: Agent = C.AGENT_UNSPEC) -> None:
        """Initialize a new instance of RequestContentBuilder.

        Args:
            target: The agent that is an object of the request.
            action: The requested action.
            subject(optional): The agent that requests. Defaults to C.AGENT_UNSPEC.
        """
        super().__init__()
        self._topic = Topic.OPERATOR
        self._operator = Operator.REQUEST
        self._subject = subject
        self._target = target
        self._content_list.append(action.clone())


class InquiryContentBuilder(RequestContentBuilder):
    """Builder class for expressing an inquiry."""

    def __init__(self, target: Agent, action: Content, *, subject: Agent = C.AGENT_UNSPEC) -> None:
        """Initialize a new instance of InquiryContentBuilder.

        Args:
            target: The agent that reveives the inquiry.
            action: The matter inquired.
            subject(optional): The agent that makes the inquiry. Defaults to C.AGENT_UNSPEC.
        """
        super().__init__(target, action, subject=subject)
        self._operator = Operator.INQUIRE


class BecauseContentBuilder(ContentBuilder):
    """Builder class for expressing a reason."""

    def __init__(self, reason: Content, action: Content, *, subject: Agent = C.AGENT_UNSPEC) -> None:
        """Initialize a new instance of BecauseContentBuilder.

        Args:
            reason: The reason for the action.
            action: The action based on the reason.
            subject(optional): The agent that expresses the action and its reason. Defaults to C.AGENT_UNSPEC.
        """
        super().__init__()
        self._topic = Topic.OPERATOR
        self._operator = Operator.BECAUSE
        self._subject = subject
        self._content_list.append(reason.clone())
        self._content_list.append(action.clone())


class AndContentBuilder(ContentBuilder):
    """Builder class for expressing a conjunctive clause."""

    def __init__(self, contents: List[Content], *, subject: Agent = C.AGENT_UNSPEC) -> None:
        """Initialize a new instance of AndContentBuilder.

        Args:
            contents: The series of the conjuncts.
            subject(optional): The agent that expresses the conjunctie clause. Defaults to C.AGENT_UNSPEC.

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

    def __init__(self, contents: List[Content], *, subject: Agent = C.AGENT_UNSPEC) -> None:
        """Initialize a new instance of OrContentBuilder.

        Args:
            contents: The series of the disjuncts.
            subject(optional): The agent that expresses the disjunctive clause. Defaults to C.AGENT_UNSPEC.
        """
        super().__init__(contents, subject=subject)
        self._operator = Operator.OR


class XorContentBuilder(BecauseContentBuilder):
    """Builder class for expressing a exclusive disjunctive clause."""

    def __init__(self, disjunct1: Content, disjunct2: Content, *, subject: Agent = C.AGENT_UNSPEC) -> None:
        """Initialize a new instance of XorContentBuilder.

        Args:
            disjunct1: The first disjunct.
            disjunct2: The second disjunct.
            subject(optional): The agent that expresses the exclusive disjunctive clause. Defaults to C.AGENT_UNSPEC.
        """
        super().__init__(disjunct1, disjunct2, subject=subject)
        self._operator = Operator.XOR


class NotContentBuilder(ContentBuilder):
    """Builder class for expressing a negation."""

    def __init__(self, content: Content, *, subject: Agent = C.AGENT_UNSPEC) -> None:
        """Initialize a new instance of NotContentBuilder.

        Args:
            content: The content to be negated.
            subject(optional): The agent that expresses the negation. Defaults to C.AGENT_UNSPEC.
        """
        super().__init__()
        self._topic = Topic.OPERATOR
        self._operator = Operator.NOT
        self._subject = subject
        self._content_list.append(content.clone())


class DayContentBuilder(ContentBuilder):
    """Builder class for adding a date to the Content."""

    def __init__(self, day: int, content: Content, *, subject: Agent = C.AGENT_UNSPEC) -> None:
        """Initialize a new instance of DayContentBuilder.

        Args:
            day: The date of the Content.
            content: The content to which the date is added.
            subject(optional): The agent that adds the date to the Content. Defaults to C.AGENT_UNSPEC.
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


class EmptyContentBuilder(ContentBuilder):
    """Builder class for expressing an empty Content."""

    def __init__(self) -> None:
        """Initialize a new instance of EmptyContentBuilder."""
        super().__init__()
        self._topic = Topic.DUMMY
