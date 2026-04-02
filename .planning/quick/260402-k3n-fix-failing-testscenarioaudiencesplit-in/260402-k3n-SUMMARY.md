# Quick Task 260402-k3n Summary

## What changed

- Updated `tests/test_ai_contract.py` so `TestScenarioAudienceSplit` uses the same player preconditions now required by the scenario runtime:
  - create a test profile
  - join the campaign as the player
  - set the player role
  - select the profile
  - ready the player
  - start the session and complete onboarding before sending a message
- Replaced the stale `"hello"` public-output assertion with `"游戏开始"`, which is a stable public output produced by the current lifecycle flow.

## Why

The failing test was asserting an outdated scenario shape from before E93. The runtime now requires profile/role selection before `ready()`, so the old fixture never reached a valid public-output path.

## Verification

- `uv run pytest -q tests\\test_ai_contract.py -k scenario_with_audience_outputs`
- `uv run pytest -q`
- `uv run python -m dm_bot.main smoke-check`
