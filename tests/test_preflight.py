"""Tests for preflight/diagnostics."""


class TestPreflight:
    def test_check_store_memory(self):
        from dm_bot.main import check_store
        result = check_store(":memory:")
        assert result["status"] == "ok"

    def test_check_modules_all_ok(self):
        from dm_bot.main import check_modules
        result = check_modules()
        assert result["all_ok"] is True
        assert len(result["modules"]) > 5
