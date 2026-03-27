from enum import StrEnum
import re


class MessageDisposition(StrEnum):
    PROCESS = "process"
    IGNORE_OOC = "ignore_ooc"
    IGNORE_SOCIAL = "ignore_social"
    IGNORE_EMPTY = "ignore_empty"


ACTION_HINTS = (
    "我",
    "我们",
    "先",
    "要",
    "去",
    "攻击",
    "施法",
    "观察",
    "推",
    "调查",
    "询问",
    "说",
    "喊",
    "躲",
    "检查",
    "进入",
    "打开",
    "冲",
    "走",
    "看",
    "听",
    "搜索",
    "潜行",
    "尝试",
)

SOCIAL_HINTS = (
    "在吗",
    "晚上",
    "几点",
    "等下",
    "等等",
    "晚点",
    "收到",
    "谢谢",
    "ok",
    "OK",
    "好的",
    "还打吗",
)


def classify_message(content: str, *, mention_count: int) -> MessageDisposition:
    stripped = content.strip()
    if not stripped:
        return MessageDisposition.IGNORE_EMPTY
    if stripped.startswith("//"):
        return MessageDisposition.IGNORE_OOC

    mention_light = re.sub(r"<@!?\d+>", "", stripped).strip()
    if mention_count and not mention_light:
        return MessageDisposition.IGNORE_SOCIAL

    if mention_count and any(hint in stripped for hint in SOCIAL_HINTS) and not any(
        hint in stripped for hint in ACTION_HINTS
    ):
        return MessageDisposition.IGNORE_SOCIAL

    return MessageDisposition.PROCESS
