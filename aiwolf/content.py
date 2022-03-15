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
    def get_contents(input: str) -> List[Content]:
        return [Content.compile(s) for s in Content.get_content_strings(input)]

    @staticmethod
    def get_content_strings(input: str) -> List[str]:
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
        self.topic: Topic = builder.topic
        """The topic of this Content."""
        self.subject: Agent = builder.subject
        """The Agent that is the subject of this Content."""
        self.target: Agent = builder.target
        """The Agent that is the object of this Content."""
        self.role: Role = builder.role
        """The role this Content refers to."""
        self.result: Species = builder.result
        """The species this Content refers to."""
        self.utterance: Utterance = builder.utterance
        """The utterance this Content refers to."""
        self.operator: Operator = builder.operator
        """The operator in this Content."""
        self.content_list: List[Content] = builder.content_list
        """The list of the operands in this Content."""
        self.day: int = builder.day
        """The date added to the operand in this Content."""
        self.text: str = ""
        """The text representing this Content."""
        self.complete_inner_subject()
        self.normalize_text()

    def complete_inner_subject(self) -> None:
        if not self.content_list:
            return
        self.content_list = [self.process_inner_content(c) for c in self.content_list]

    def process_inner_content(self, inner: Content) -> Content:
        if inner.subject is C.AGENT_UNSPEC:
            if self.operator is Operator.INQUIRE or self.operator is Operator.REQUEST:
                return inner.copy_and_replace_subject(self.target)
            if self.subject is not C.AGENT_UNSPEC:
                return inner.copy_and_replace_subject(self.subject)
        inner.complete_inner_subject()
        return inner

    def copy_and_replace_subject(self, new_subject: Agent) -> Content:
        c: Content = self.clone()
        c.subject = new_subject
        c.complete_inner_subject()
        c.normalize_text()
        return c

    def normalize_text(self) -> None:
        str_sub: str = "" if self.subject is C.AGENT_UNSPEC else "ANY " if self.subject is C.AGENT_ANY else str(self.subject)+" "
        str_tgt: str = "ANY" if self.target is C.AGENT_ANY or self.target is C.AGENT_UNSPEC else str(self.target)
        if self.topic is not Topic.OPERATOR:
            if self.topic is Topic.DUMMY:
                self.text = ""
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
                self.text = str_sub + " ".join([self.operator.value, str_tgt, "("+Content.strip_subject(self.content_list[0].text) +
                                                ")" if self.content_list[0].subject is self.target else "("+self.content_list[0].text+")"])
            elif self.operator is Operator.BECAUSE or self.operator is Operator.XOR:
                self.text = str_sub + " ".join([self.operator.value] + ["("+Content.strip_subject(self.content_list[i].text) +
                                                                          ")" if self.content_list[i].subject is self.subject else "("+self.content_list[i].text+")" for i in [0, 1]])
            elif self.operator is Operator.AND or self.operator is Operator.OR:
                self.text = str_sub + " ".join([self.operator.value] + ["("+Content.strip_subject(c.text)+")" if c.subject is self.subject else "("+c.text+")" for c in self.content_list])
            elif self.operator is Operator.NOT:
                self.text = str_sub + " ".join([self.operator.value, "("+Content.strip_subject(self.content_list[0].text) +
                                                ")" if self.content_list[0].subject is self.subject else "("+self.content_list[0].text+")"])
            elif self.operator is Operator.DAY:
                self.text = str_sub + " ".join([self.operator.value, str(self.day), "("+Content.strip_subject(self.content_list[0].text) +
                                                ")" if self.content_list[0].subject is self.subject else "("+self.content_list[0].text+")"])

    strip_pattern: Pattern[str] = re.compile(r"^(Agent\[\d+\]|ANY|)\s*([A-Z]+.*)$")

    @staticmethod
    def strip_subject(input: str) -> str:
        m: Optional[Match[str]] = Content.strip_pattern.match(input)
        if m:
            return m.group(2)
        return input

    def clone(self) -> Content:
        """Clone this Content.

        Returns:
            The cloned Content.
        """
        content: Content = Content(ContentBuilder())
        content.topic = self.topic
        content.subject = self.subject
        content.target = self.target
        content.role = self.role
        content.result = self.result
        content.utterance = self.utterance
        content.operator = self.operator
        content.content_list = self.content_list
        content.day = self.day
        content.text = self.text
        return content

    regex_agent: str = r"\s+(Agent\[\d+\]|ANY)"
    regex_subject: str = r"^(Agent\[\d+\]|ANY|)\s*"
    regex_talk: str = r"\s+([A-Z]+)\s+day(\d+)\s+ID:(\d+)"
    regex_role_species: str = r"\s+([A-Z]+)"
    regex_paren: str = r"(\(.*\))"
    regex_digit: str = r"(\d+)"
    agree_pattern: Pattern[str] = re.compile(regex_subject + "(AGREE|DISAGREE)" + regex_talk + "$")
    estimate_pattern: Pattern[str] = re.compile(regex_subject + "(ESTIMATE|COMINGOUT)" + regex_agent + regex_role_species + "$")
    divined_pattern: Pattern[str] = re.compile(regex_subject + "(DIVINED|IDENTIFIED)" + regex_agent + regex_role_species + "$")
    attack_pattern: Pattern[str] = re.compile(regex_subject + "(ATTACK|ATTACKED|DIVINATION|GUARD|GUARDED|VOTE|VOTED)" + regex_agent + "$")
    request_pattern: Pattern[str] = re.compile(regex_subject + "(REQUEST|INQUIRE)" + regex_agent + r"\s+" + regex_paren + "$")
    because_pattern: Pattern[str] = re.compile(regex_subject + r"(BECAUSE|AND|OR|XOR|NOT|REQUEST)\s+" + regex_paren + "$")
    day_pattern: Pattern[str] = re.compile(regex_subject + r"DAY\s+" + regex_digit + r"\s+" + regex_paren + "$")
    skip_pattern: Pattern[str] = re.compile("^(Skip|Over)$")

    @staticmethod
    def compile(text: str) -> Content:
        """Convert the uttered text into a Content.

        Args:
            text: The uttered text.

        Returns:
            The Content converted from the given text.
        """
        trimmed: str = text.strip()
        m_agree: Optional[Match[str]] = Content.agree_pattern.match(trimmed)
        m_estimate: Optional[Match[str]] = Content.estimate_pattern.match(trimmed)
        m_divined: Optional[Match[str]] = Content.divined_pattern.match(trimmed)
        m_attack: Optional[Match[str]] = Content.attack_pattern.match(trimmed)
        m_request: Optional[Match[str]] = Content.request_pattern.match(trimmed)
        m_because: Optional[Match[str]] = Content.because_pattern.match(trimmed)
        m_day: Optional[Match[str]] = Content.day_pattern.match(trimmed)
        m_skip: Optional[Match[str]] = Content.skip_pattern.match(trimmed)
        content: Content = Content(SkipContentBuilder())
        if m_skip:
            content.topic = Topic[m_skip.group(1)]
        elif m_agree:
            content.subject = Agent.compile(m_agree.group(1))
            content.topic = Topic[m_agree.group(2)]
            if UtteranceType[m_agree.group(3)] is UtteranceType.TALK:
                content.utterance = Talk(int(m_agree.group(5)), C.AGENT_NONE, int(m_agree.group(4)), "", 0)
            else:
                content.utterance = Whisper(int(m_agree.group(5)), C.AGENT_NONE, int(m_agree.group(4)), "", 0)
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
            content.content_list = Content.get_contents(m_request.group(4))
        elif m_because:
            content.topic = Topic.OPERATOR
            content.subject = Agent.compile(m_because.group(1))
            content.operator = Operator[m_because.group(2)]
            content.content_list = Content.get_contents(m_because.group(3))
            if content.operator is Operator.REQUEST:
                content.target = C.AGENT_ANY if content.content_list[0].subject is C.AGENT_UNSPEC else content.content_list[0].subject
        elif m_day:
            content.topic = Topic.OPERATOR
            content.subject = Agent.compile(m_day.group(1))
            content.operator = Operator.DAY
            content.day = int(m_day.group(2))
            content.content_list = Content.get_contents(m_day.group(3))
        else:
            content.topic = Topic.Skip
        content.complete_inner_subject()
        content.normalize_text()
        return content

    def equals(self, other: Content) -> bool:
        """Show whether or not the given Content is equivalent to this Content.

        Args:
            other: The Content to be compared.

        Returns:
            True if other is equivalent to this, otherwise false.
        """
        return self.text == other.text


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
        self.subject: Agent = C.AGENT_UNSPEC
        self.target: Agent = C.AGENT_ANY
        self.topic: Topic = Topic.DUMMY
        self.role: Role = Role.UNC
        self.result: Species = Species.UNC
        self.utterance: Utterance = Utterance()
        self.operator: Operator = Operator.NOP
        self.content_list: List[Content] = []
        self.day: int = -1


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
        self.topic = Topic.AGREE
        self.subject = subject
        if utterance_type is UtteranceType.TALK:
            self.utterance = Talk(day, C.AGENT_NONE, idx, "", 0)
        else:
            self.utterance = Whisper(day, C.AGENT_NONE, idx, "", 0)


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
        self.topic = Topic.DISAGREE


class AttackContentBuilder(ContentBuilder):
    """Builder class for expressing the will to attack."""

    def __init__(self, target: Agent, *, subject: Agent = C.AGENT_UNSPEC) -> None:
        """Initialize a new instance of AttackContentBuilder.

        Args:
            target: The agent the utterer wants to attack.
            subject(optional): The agent that expresses the will to attack. Defaults to C.AGENT_UNSPEC.
        """
        super().__init__()
        self.topic = Topic.ATTACK
        self.subject = subject
        self.target = target


class AttackedContentBuilder(AttackContentBuilder):
    """Builder class for the report of an attack."""

    def __init__(self, target: Agent, *, subject: Agent = C.AGENT_UNSPEC) -> None:
        """Initialize a new instance of AttackedContentBuilder.

        Args:
            target: The attacked agent.
            subject(optional): The agent that reports the attack. Defaults to C.AGENT_UNSPEC.
        """
        super().__init__(target, subject=subject)
        self.topic = Topic.ATTACKED


class DivinationContentBuilder(AttackContentBuilder):
    """Builder class for expressing a divination."""

    def __init__(self, target: Agent, *, subject: Agent = C.AGENT_UNSPEC) -> None:
        """Initialize a new instance of DivinationContentBuilder.

        Args:
            target: The agent that is an object of the divination.
            subject(optional): The agent that does the divination. Defaults to C.AGENT_UNSPEC.
        """
        super().__init__(target, subject=subject)
        self.topic = Topic.DIVINATION


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
        self.topic = Topic.DIVINED
        self.subject = subject
        self.target = target
        self.result = result


class GuardContentBuilder(AttackContentBuilder):
    """Builder class for expressing a guard."""

    def __init__(self, target: Agent, *, subject: Agent = C.AGENT_UNSPEC) -> None:
        """Initialize a new instance of GuardContentBuilder.

        Args:
            target: The agent to be guarded.
            subject(optional): The agent that guards. Defaults to C.AGENT_UNSPEC.
        """
        super().__init__(target, subject=subject)
        self.topic = Topic.GUARD


class GuardedAgentContentBuilder(AttackContentBuilder):
    """Builder class for the report of a guard."""

    def __init__(self, target: Agent, *, subject: Agent = C.AGENT_UNSPEC) -> None:
        """Initialize a new instance of GurdedAgentContentBuilder.

        Args:
            target: The agent that was guarded.
            subject(optional): The agent that guarded. Defaults to C.AGENT_UNSPEC.
        """
        super().__init__(target, subject=subject)
        self.topic = Topic.GUARDED


class VoteContentBuilder(AttackContentBuilder):
    """Builder class for expressing a vote."""

    def __init__(self, target: Agent, *, subject: Agent = C.AGENT_UNSPEC) -> None:
        """Initialize a new instance of VoteContentBuilder.

        Args:
            target: The agent to be voted on.
            subject(optional): The agent that votes. Defaults to C.AGENT_UNSPEC.
        """
        super().__init__(target, subject=subject)
        self.topic = Topic.VOTE


class VotedContentBuilder(AttackContentBuilder):
    """Builder class for the report of a vote."""

    def __init__(self, target: Agent, *, subject: Agent = C.AGENT_UNSPEC) -> None:
        """Initialize a new instance of VotedContentBuilder.

        Args:
            target: The agent that was voted on.
            subject(optional): The agent that voted. Defaults to C.AGENT_UNSPEC.
        """
        super().__init__(target, subject=subject)
        self.topic = Topic.VOTED


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
        self.topic = Topic.COMINGOUT
        self.subject = subject
        self.target = target
        self.role = role


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
        self.topic = Topic.ESTIMATE


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
        self.topic = Topic.IDENTIFIED


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
        self.topic = Topic.OPERATOR
        self.operator = Operator.REQUEST
        self.subject = subject
        self.target = target
        self.content_list.append(action.clone())


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
        self.operator = Operator.INQUIRE


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
        self.topic = Topic.OPERATOR
        self.operator = Operator.BECAUSE
        self.subject = subject
        self.content_list.append(reason.clone())
        self.content_list.append(action.clone())


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
        self.topic = Topic.OPERATOR
        self.operator = Operator.AND
        self.subject = subject
        if not contents:
            raise ValueError("Invalid argument: contents is empty")
        self.content_list.extend([c.clone() for c in contents])


class OrContentBuilder(AndContentBuilder):
    """Builder class for expressing a disjunctive clause."""

    def __init__(self, contents: List[Content], *, subject: Agent = C.AGENT_UNSPEC) -> None:
        """Initialize a new instance of OrContentBuilder.

        Args:
            contents: The series of the disjuncts.
            subject(optional): The agent that expresses the disjunctive clause. Defaults to C.AGENT_UNSPEC.
        """
        super().__init__(contents, subject=subject)
        self.operator = Operator.OR


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
        self.operator = Operator.XOR


class NotContentBuilder(ContentBuilder):
    """Builder class for expressing a negation."""

    def __init__(self, content: Content, *, subject: Agent = C.AGENT_UNSPEC) -> None:
        """Initialize a new instance of NotContentBuilder.

        Args:
            content: The content to be negated.
            subject(optional): The agent that expresses the negation. Defaults to C.AGENT_UNSPEC.
        """
        super().__init__()
        self.topic = Topic.OPERATOR
        self.operator = Operator.NOT
        self.subject = subject
        self.content_list.append(content.clone())


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
        self.topic = Topic.OPERATOR
        self.operator = Operator.DAY
        self.subject = subject
        self.day = day
        self.content_list.append(content.clone())


class SkipContentBuilder(ContentBuilder):
    """Builder class for the skip of this turn's utterance."""

    def __init__(self) -> None:
        """Initialize a new instance of SkipContentBuilder."""
        super().__init__()
        self.topic = Topic.Skip


class OverContentBuilder(ContentBuilder):
    """Builder class for expressing that there is nothing to utter."""

    def __init__(self) -> None:
        """Initialize a new instance of OverContentBuilder."""
        super().__init__()
        self.topic = Topic.Over


class EmptyContentBuilder(ContentBuilder):
    """Builder class for expressing an empty Content."""

    def __init__(self) -> None:
        """Initialize a new instance of EmptyContentBuilder."""
        super().__init__()
        self.topic = Topic.DUMMY
