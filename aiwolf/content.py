"""
content.py

(c) 2022 OTSUKI Takashi

"""
from __future__ import annotations

import re
from enum import Enum
from typing import List, Match, Optional, Pattern

from aiwolf.agent import Agent, Role, Species
from aiwolf.constant import Constant as C
from aiwolf.utterance import Talk, Utterance, UtteranceType, Whisper


class Content:

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

    def __init__(self, builder: ContentBuilder) -> None:
        self.topic: Topic = builder.topic
        self.subject: Agent = builder.subject
        self.target: Agent = builder.target
        self.role: Role = builder.role
        self.result: Species = builder.result
        self.utterance: Utterance = builder.utterance
        self.operator: Operator = builder.operator
        self.content_list: List[Content] = builder.content_list
        self.day: int = builder.day
        self.text: str = ""
        self.complete_inner_subject()
        self.normalize_text()

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
        return self.text == other.text


class Topic(Enum):
    DUMMY = "DUMMY"
    ESTIMATE = "ESTIMATE"
    COMINGOUT = "COMINGOUT"
    DIVINATION = "DIVINATION"
    DIVINED = "DIVINED"
    IDENTIFIED = "IDENTIFIED"
    GUARD = "GUARD"
    GUARDED = "GUARDED"
    VOTE = "VOTE"
    VOTED = "VOTED"
    ATTACK = "ATTACK"
    ATTACKED = "ATTACKED"
    AGREE = "AGREE"
    DISAGREE = "DISAGREE"
    Over = "Over"
    Skip = "Skip"
    OPERATOR = "OPERATOR"


class Operator(Enum):
    NOP = "NOP"
    REQUEST = "REQUEST"
    INQUIRE = "INQUIRE"
    BECAUSE = "BECAUSE"
    DAY = "DAY"
    NOT = "NOT"
    AND = "AND"
    OR = "OR"
    XOR = "XOR"


class ContentBuilder:
    def __init__(self) -> None:
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
    def __init__(self, utterance_type: UtteranceType, day: int, idx: int, *, subject: Agent = C.AGENT_UNSPEC) -> None:
        super().__init__()
        self.topic = Topic.AGREE
        self.subject = subject
        if utterance_type is UtteranceType.TALK:
            self.utterance = Talk(day, C.AGENT_NONE, idx, "", 0)
        else:
            self.utterance = Whisper(day, C.AGENT_NONE, idx, "", 0)


class DisagreeContentBuilder(AgreeContentBuilder):
    def __init__(self, utterance_type: UtteranceType, day: int, idx: int, *, subject: Agent = C.AGENT_UNSPEC) -> None:
        super().__init__(utterance_type, day, idx, subject=subject)
        self.topic = Topic.DISAGREE


class AttackContentBuilder(ContentBuilder):
    def __init__(self, target: Agent, *, subject: Agent = C.AGENT_UNSPEC) -> None:
        super().__init__()
        self.topic = Topic.ATTACK
        self.subject = subject
        self.target = target


class AttackedContentBuilder(AttackContentBuilder):
    def __init__(self, target: Agent, *, subject: Agent = C.AGENT_UNSPEC) -> None:
        super().__init__(target, subject=subject)
        self.topic = Topic.ATTACKED


class DivinationContentBuilder(AttackContentBuilder):
    def __init__(self, target: Agent, *, subject: Agent = C.AGENT_UNSPEC) -> None:
        super().__init__(target, subject=subject)
        self.topic = Topic.DIVINATION


class DivinedResultContentBuilder(ContentBuilder):
    def __init__(self, target: Agent, result: Species, *, subject: Agent = C.AGENT_UNSPEC) -> None:
        super().__init__()
        self.topic = Topic.DIVINED
        self.subject = subject
        self.target = target
        self.result = result


class GuardContentBuilder(AttackContentBuilder):
    def __init__(self, target: Agent, *, subject: Agent = C.AGENT_UNSPEC) -> None:
        super().__init__(target, subject=subject)
        self.topic = Topic.GUARD


class GuardedAgentContentBuilder(AttackContentBuilder):
    def __init__(self, target: Agent, *, subject: Agent = C.AGENT_UNSPEC) -> None:
        super().__init__(target, subject=subject)
        self.topic = Topic.GUARDED


class VoteContentBuilder(AttackContentBuilder):
    def __init__(self, target: Agent, *, subject: Agent = C.AGENT_UNSPEC) -> None:
        super().__init__(target, subject=subject)
        self.topic = Topic.VOTE


class VotedContentBuilder(AttackContentBuilder):
    def __init__(self, target: Agent, *, subject: Agent = C.AGENT_UNSPEC) -> None:
        super().__init__(target, subject=subject)
        self.topic = Topic.VOTED


class ComingoutContentBuilder(ContentBuilder):
    def __init__(self, target: Agent, role: Role, *, subject: Agent = C.AGENT_UNSPEC) -> None:
        super().__init__()
        self.topic = Topic.COMINGOUT
        self.subject = subject
        self.target = target
        self.role = role


class EstimateContentBuilder(ComingoutContentBuilder):
    def __init__(self, target: Agent, role: Role, *, subject: Agent = C.AGENT_UNSPEC) -> None:
        super().__init__(target, role, subject=subject)
        self.topic = Topic.ESTIMATE


class IdentContentBuilder(DivinedResultContentBuilder):
    def __init__(self, target: Agent, result: Species, *, subject: Agent = C.AGENT_UNSPEC) -> None:
        super().__init__(target, result, subject=subject)
        self.topic = Topic.IDENTIFIED


class RequestContentBuilder(ContentBuilder):
    def __init__(self, target: Agent, action: Content, *, subject: Agent = C.AGENT_UNSPEC) -> None:
        super().__init__()
        self.topic = Topic.OPERATOR
        self.operator = Operator.REQUEST
        self.subject = subject
        self.target = target
        self.content_list.append(action.clone())


class InquiryContentBuilder(RequestContentBuilder):
    def __init__(self, target: Agent, action: Content, *, subject: Agent = C.AGENT_UNSPEC) -> None:
        super().__init__(target, action, subject=subject)
        self.operator = Operator.INQUIRE


class BecauseContentBuilder(ContentBuilder):
    def __init__(self, reason: Content, action: Content, *, subject: Agent = C.AGENT_UNSPEC) -> None:
        super().__init__()
        self.topic = Topic.OPERATOR
        self.operator = Operator.BECAUSE
        self.subject = subject
        self.content_list.append(reason.clone())
        self.content_list.append(action.clone())


class AndContentBuilder(ContentBuilder):
    def __init__(self, contents: List[Content], *, subject: Agent = C.AGENT_UNSPEC) -> None:
        super().__init__()
        self.topic = Topic.OPERATOR
        self.operator = Operator.AND
        self.subject = subject
        if not contents:
            raise ValueError("Invalid argument: contents is empty")
        self.content_list.extend([c.clone() for c in contents])


class OrContentBuilder(AndContentBuilder):
    def __init__(self, contents: List[Content], *, subject: Agent = C.AGENT_UNSPEC) -> None:
        super().__init__(contents, subject=subject)
        self.operator = Operator.OR


class XorContentBuilder(BecauseContentBuilder):
    def __init__(self, disjunct1: Content, disjunct2: Content, *, subject: Agent = C.AGENT_UNSPEC) -> None:
        super().__init__(disjunct1, disjunct2, subject=subject)
        self.operator = Operator.XOR


class NotContentBuilder(ContentBuilder):
    def __init__(self, content: Content, *, subject: Agent = C.AGENT_UNSPEC) -> None:
        super().__init__()
        self.topic = Topic.OPERATOR
        self.operator = Operator.NOT
        self.subject = subject
        self.content_list.append(content.clone())


class DayContentBuilder(ContentBuilder):
    def __init__(self, day: int, content: Content, *, subject: Agent = C.AGENT_UNSPEC) -> None:
        super().__init__()
        self.topic = Topic.OPERATOR
        self.operator = Operator.DAY
        self.subject = subject
        self.day = day
        self.content_list.append(content.clone())


class SkipContentBuilder(ContentBuilder):
    def __init__(self) -> None:
        super().__init__()
        self.topic = Topic.Skip


class OverContentBuilder(ContentBuilder):
    def __init__(self) -> None:
        super().__init__()
        self.topic = Topic.Over


class EmptyContentBuilder(ContentBuilder):
    def __init__(self) -> None:
        super().__init__()
        self.topic = Topic.DUMMY
