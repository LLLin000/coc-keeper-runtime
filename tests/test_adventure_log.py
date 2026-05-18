"""Tests for adventure log."""


class TestAdventureLog:
    def test_log_entry(self):
        from dm_bot.character.adventure_log import AdventureLog, LogEntry

        entry = LogEntry(session_id="ses_1", entry_type="skill_improvement", detail="spot_hidden 40->50")
        log = AdventureLog()
        log.add_entry(entry)
        entries = log.get_entries("ses_1")
        assert len(entries) == 1
        assert entries[0].entry_type == "skill_improvement"

    def test_log_order(self):
        from dm_bot.character.adventure_log import AdventureLog, LogEntry

        log = AdventureLog()
        log.add_entry(LogEntry(session_id="ses_1", entry_type="first", detail="a"))
        log.add_entry(LogEntry(session_id="ses_1", entry_type="second", detail="b"))
        entries = log.get_entries("ses_1")
        assert entries[0].entry_type == "first"
        assert entries[1].entry_type == "second"
