import unittest
from aiwolf.agent import Agent, Role, Species

from aiwolf.content import AgreeContentBuilder, AndContentBuilder, AttackContentBuilder, AttackedContentBuilder, BecauseContentBuilder, Content, ComingoutContentBuilder, DayContentBuilder, DisagreeContentBuilder, DivinationContentBuilder, DivinedResultContentBuilder, EmptyContentBuilder, EstimateContentBuilder, GuardContentBuilder, GuardedAgentContentBuilder, IdentContentBuilder, InquiryContentBuilder, NotContentBuilder, OrContentBuilder, OverContentBuilder, RequestContentBuilder, SkipContentBuilder, VoteContentBuilder, VotedContentBuilder, XorContentBuilder
from aiwolf.utterance import UtteranceType


class TestContent(unittest.TestCase):

    def test_skip_contentbuilder(self):
        c1 = Content(SkipContentBuilder())
        self.assertEqual(c1.text, "Skip")

    def test_over_contentbuilder(self):
        c1 = Content(OverContentBuilder())
        self.assertEqual(c1.text, "Over")

    def test_empty_contentbuilder(self):
        c1 = Content(EmptyContentBuilder())
        self.assertEqual(c1.text, "")

    def test_agree_contentbuilder(self):
        subject: Agent = Agent(1)
        day: int = 2
        idx: int = 3
        c1 = Content(AgreeContentBuilder(utterance_type=UtteranceType.TALK, day=day, idx=idx))
        self.assertEqual(c1.text, "AGREE TALK 2 3")
        c1 = Content(AgreeContentBuilder(utterance_type=UtteranceType.TALK, day=day, idx=idx, subject=subject))
        self.assertEqual(c1.text, "Agent[01] AGREE TALK 2 3")

    def test_disagree_contentbuilder(self):
        subject: Agent = Agent(1)
        day: int = 2
        idx: int = 3
        c1 = Content(DisagreeContentBuilder(utterance_type=UtteranceType.TALK, day=day, idx=idx))
        self.assertEqual(c1.text, "DISAGREE TALK 2 3")
        c1 = Content(DisagreeContentBuilder(utterance_type=UtteranceType.TALK, day=day, idx=idx, subject=subject))
        self.assertEqual(c1.text, "Agent[01] DISAGREE TALK 2 3")

    def test_attack_contentbuilder(self):
        subject: Agent = Agent(1)
        target: Agent = Agent(2)
        c1 = Content(AttackContentBuilder(target, subject=subject))
        self.assertEqual(c1.text, "Agent[01] ATTACK Agent[02]")
        c1 = Content(AttackContentBuilder(target))
        self.assertEqual(c1.text, "ATTACK Agent[02]")

    def test_attacked_contentbuilder(self):
        subject: Agent = Agent(1)
        target: Agent = Agent(2)
        c1 = Content(AttackedContentBuilder(target, subject=subject))
        self.assertEqual(c1.text, "Agent[01] ATTACKED Agent[02]")
        c1 = Content(AttackedContentBuilder(target))
        self.assertEqual(c1.text, "ATTACKED Agent[02]")

    def test_divination_contentbuilder(self):
        subject: Agent = Agent(1)
        target: Agent = Agent(2)
        c1 = Content(DivinationContentBuilder(target, subject=subject))
        self.assertEqual(c1.text, "Agent[01] DIVINATION Agent[02]")
        c1 = Content(DivinationContentBuilder(target))
        self.assertEqual(c1.text, "DIVINATION Agent[02]")

    def test_divied_result_contentbuilder(self):
        subject: Agent = Agent(1)
        target: Agent = Agent(2)
        result: Species = Species.WEREWOLF
        c1 = Content(DivinedResultContentBuilder(target, result, subject=subject))
        self.assertEqual(c1.text, "Agent[01] DIVINED Agent[02] WEREWOLF")
        c1 = Content(DivinedResultContentBuilder(target, result))
        self.assertEqual(c1.text, "DIVINED Agent[02] WEREWOLF")

    def test_guard_contentbuilder(self):
        subject: Agent = Agent(1)
        target: Agent = Agent(2)
        c1 = Content(GuardContentBuilder(target, subject=subject))
        self.assertEqual(c1.text, "Agent[01] GUARD Agent[02]")
        c1 = Content(GuardContentBuilder(target))
        self.assertEqual(c1.text, "GUARD Agent[02]")

    def test_guarded_contentbuilder(self):
        subject: Agent = Agent(1)
        target: Agent = Agent(2)
        c1 = Content(GuardedAgentContentBuilder(target, subject=subject))
        self.assertEqual(c1.text, "Agent[01] GUARDED Agent[02]")
        c1 = Content(GuardedAgentContentBuilder(target))
        self.assertEqual(c1.text, "GUARDED Agent[02]")

    def test_vote_contentbuilder(self):
        subject: Agent = Agent(1)
        target: Agent = Agent(2)
        c1 = Content(VoteContentBuilder(target, subject=subject))
        self.assertEqual(c1.text, "Agent[01] VOTE Agent[02]")
        c1 = Content(VoteContentBuilder(target))
        self.assertEqual(c1.text, "VOTE Agent[02]")

    def test_voted_contentbuilder(self):
        subject: Agent = Agent(1)
        target: Agent = Agent(2)
        c1 = Content(VotedContentBuilder(target, subject=subject))
        self.assertEqual(c1.text, "Agent[01] VOTED Agent[02]")
        c1 = Content(VotedContentBuilder(target))
        self.assertEqual(c1.text, "VOTED Agent[02]")

    def test_comingout_contentbuilder(self):
        subject: Agent = Agent(1)
        target: Agent = Agent(2)
        role: Role = Role.SEER
        c1 = Content(ComingoutContentBuilder(target, role, subject=subject))
        self.assertEqual(c1.text, "Agent[01] COMINGOUT Agent[02] SEER")
        c1 = Content(ComingoutContentBuilder(target, role))
        self.assertEqual(c1.text, "COMINGOUT Agent[02] SEER")

    def test_estimate_contentbuilder(self):
        subject: Agent = Agent(1)
        target: Agent = Agent(2)
        role: Role = Role.SEER
        c1 = Content(EstimateContentBuilder(target, role, subject=subject))
        self.assertEqual(c1.text, "Agent[01] ESTIMATE Agent[02] SEER")
        c1 = Content(EstimateContentBuilder(target, role))
        self.assertEqual(c1.text, "ESTIMATE Agent[02] SEER")

    def test_oident_contentbuilder(self):
        subject: Agent = Agent(1)
        target: Agent = Agent(2)
        result: Species = Species.WEREWOLF
        c1 = Content(IdentContentBuilder(target, result, subject=subject))
        self.assertEqual(c1.text, "Agent[01] IDENTIFIED Agent[02] WEREWOLF")
        c1 = Content(IdentContentBuilder(target, result))
        self.assertEqual(c1.text, "IDENTIFIED Agent[02] WEREWOLF")

    def test_request_contentbuilder(self):
        subject: Agent = Agent(1)
        target: Agent = Agent(2)
        action: Content = Content(VoteContentBuilder(Agent(3)))
        c1 = Content(RequestContentBuilder(target, action, subject=subject))
        self.assertEqual(c1.text, "Agent[01] REQUEST Agent[02] (VOTE Agent[03])")
        c1 = Content(RequestContentBuilder(target, action))
        self.assertEqual(c1.text, "REQUEST Agent[02] (VOTE Agent[03])")

    def test_inquiry_contentbuilder(self):
        subject: Agent = Agent(1)
        target: Agent = Agent(2)
        action: Content = Content(VoteContentBuilder(Agent(3)))
        c1 = Content(InquiryContentBuilder(target, action, subject=subject))
        self.assertEqual(c1.text, "Agent[01] INQUIRE Agent[02] (VOTE Agent[03])")
        c1 = Content(InquiryContentBuilder(target, action))
        self.assertEqual(c1.text, "INQUIRE Agent[02] (VOTE Agent[03])")

    def test_because_contentbuilder(self):
        subject: Agent = Agent(1)
        reason: Content = Content(VotedContentBuilder(subject=Agent(2), target=Agent(3)))
        action: Content = Content(VoteContentBuilder(Agent(3)))
        c1 = Content(BecauseContentBuilder(subject=subject, reason=reason, action=action))
        self.assertEqual(c1.text, "Agent[01] BECAUSE (Agent[02] VOTED Agent[03]) (VOTE Agent[03])")
        c1 = Content(BecauseContentBuilder(reason, action))
        self.assertEqual(c1.text, "BECAUSE (Agent[02] VOTED Agent[03]) (VOTE Agent[03])")

    def test_and_contentbuilder(self):
        subject: Agent = Agent(1)
        content1 = Content(DivinedResultContentBuilder(Agent(2), Species.HUMAN))
        content2 = Content(DivinedResultContentBuilder(Agent(3), Species.WEREWOLF))
        content3 = Content(DivinedResultContentBuilder(Agent(4), Species.WEREWOLF))
        c1 = Content(AndContentBuilder([content1, content2, content3], subject=subject))
        self.assertEqual(c1.text, "Agent[01] AND (DIVINED Agent[02] HUMAN) (DIVINED Agent[03] WEREWOLF) (DIVINED Agent[04] WEREWOLF)")
        c1 = Content(AndContentBuilder([content1, content2, content3]))
        self.assertEqual(c1.text, "AND (DIVINED Agent[02] HUMAN) (DIVINED Agent[03] WEREWOLF) (DIVINED Agent[04] WEREWOLF)")

    def test_or_contentbuilder(self):
        subject: Agent = Agent(1)
        content1 = Content(DivinedResultContentBuilder(Agent(2), Species.HUMAN))
        content2 = Content(DivinedResultContentBuilder(Agent(3), Species.WEREWOLF))
        content3 = Content(DivinedResultContentBuilder(Agent(4), Species.WEREWOLF))
        c1 = Content(OrContentBuilder([content1, content2, content3], subject=subject))
        self.assertEqual(c1.text, "Agent[01] OR (DIVINED Agent[02] HUMAN) (DIVINED Agent[03] WEREWOLF) (DIVINED Agent[04] WEREWOLF)")
        c1 = Content(OrContentBuilder([content1, content2, content3]))
        self.assertEqual(c1.text, "OR (DIVINED Agent[02] HUMAN) (DIVINED Agent[03] WEREWOLF) (DIVINED Agent[04] WEREWOLF)")

    def test_xor_contentbuilder(self):
        subject: Agent = Agent(1)
        content1 = Content(DivinedResultContentBuilder(Agent(2), Species.HUMAN))
        content2 = Content(DivinedResultContentBuilder(Agent(3), Species.WEREWOLF))
        c1 = Content(XorContentBuilder(content1, content2, subject=subject))
        self.assertEqual(c1.text, "Agent[01] XOR (DIVINED Agent[02] HUMAN) (DIVINED Agent[03] WEREWOLF)")
        c1 = Content(XorContentBuilder(content1, content2))
        self.assertEqual(c1.text, "XOR (DIVINED Agent[02] HUMAN) (DIVINED Agent[03] WEREWOLF)")

    def test_not_contentbuilder(self):
        subject: Agent = Agent(1)
        content1 = Content(DivinedResultContentBuilder(Agent(2), Species.HUMAN))
        content2 = Content(DivinedResultContentBuilder(Agent(3), Species.WEREWOLF))
        c1 = Content(XorContentBuilder(content1, content2, subject=Agent(4)))
        c2 = Content(NotContentBuilder(c1, subject=subject))
        self.assertEqual(c2.text, "Agent[01] NOT (Agent[04] XOR (DIVINED Agent[02] HUMAN) (DIVINED Agent[03] WEREWOLF))")
        c2 = Content(NotContentBuilder(c1))
        self.assertEqual(c2.text, "NOT (Agent[04] XOR (DIVINED Agent[02] HUMAN) (DIVINED Agent[03] WEREWOLF))")

    def test_day_contentbuilder(self):
        subject: Agent = Agent(1)
        content1 = Content(DivinedResultContentBuilder(Agent(2), Species.HUMAN))
        c1 = Content(DayContentBuilder(2, content1, subject=subject))
        self.assertEqual(c1.text, "Agent[01] DAY 2 (DIVINED Agent[02] HUMAN)")
        c2 = Content(DayContentBuilder(2, content1))
        self.assertEqual(c2.text, "DAY 2 (DIVINED Agent[02] HUMAN)")
