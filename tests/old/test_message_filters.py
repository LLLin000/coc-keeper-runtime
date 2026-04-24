from dm_bot.orchestrator.message_filters import MessageDisposition, classify_message


def test_classify_message_ignores_ooc_prefix() -> None:
    decision = classify_message("//等我两分钟，我去接水", mention_count=0)

    assert decision == MessageDisposition.IGNORE_OOC


def test_classify_message_ignores_social_mention_chatter() -> None:
    decision = classify_message("@队友 你晚上还打吗", mention_count=1)

    assert decision == MessageDisposition.IGNORE_SOCIAL


def test_classify_message_accepts_action_even_with_mentions() -> None:
    decision = classify_message("@队友 我先去推门，你掩护我", mention_count=1)

    assert decision == MessageDisposition.PROCESS
