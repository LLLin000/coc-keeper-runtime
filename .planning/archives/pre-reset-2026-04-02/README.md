# Planning Archive Snapshot — `pre-reset-2026-04-02`

This archive captures the repository planning state before the 2026-04-02 planning reset.

## Why This Exists

The previous planning tree had accumulated:

- overlapping track ownership
- mixed old and new milestone conventions
- duplicated or stale planning entrypoints
- legacy phase directories left in active planning roots

Instead of deleting history, this snapshot preserves the pre-reset planning state in one place and lets the active `.planning/` root restart from a cleaner baseline.

## What Was Archived

- previous root planning documents and milestone history
- previous 5-track workstream layout
- legacy `governance-milestone` workstream
- root `phases/`, `quick/`, `debug/`, `reports/`, `research/`, `seeds/`
- old execution and analysis artifacts that no longer define active truth

## What Replaced It

The active planning root now uses 4 workstreams with clearer canonical ownership:

1. `track-runtime`
2. `track-identity`
3. `track-surface`
4. `track-ops`

See the active root:

- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/STATE.md`
- `.planning/active-workstream`
- `.planning/workstreams/`

## Notes

This is a cleaned archive snapshot, not a byte-for-byte forensic image. Obvious duplicate or superseded planning entrypoints were grouped before archiving so the historical tree remains understandable.

## Snapshot Index

- `root-snapshot/PROJECT.md` — old 5-track ownership model summary
- `root-snapshot/ROADMAP.md` — old repository planning index summary
- `root-snapshot/STATE.md` — active workstream and milestone state at reset time
- `root-snapshot/MILESTONES.md` — milestone-history summary and location notes
