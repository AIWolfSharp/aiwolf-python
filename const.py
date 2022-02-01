"""
const.py

(c) 2022 OTSUKI Takashi

"""
from aiwolf.constant import Constant
from aiwolf.content import Content, OverContentBuilder, SkipContentBuilder


class Const:
    AGENT_NONE = Constant.AGENT_NONE
    AGENT_UNSPEC = Constant.AGENT_UNSPEC
    AGENT_ANY = Constant.AGENT_ANY
    CONTENT_SKIP = Content(SkipContentBuilder())
    CONTENT_OVER = Content(OverContentBuilder())
