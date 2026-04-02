# Phase 41 Context

## Goal

Build the core synthesis path that turns normalized builder answers into a cohesive COC archive profile instead of copying player answers verbatim.

## Inputs

- Phase 40 contracts and normalization seam
- Existing builder interview flow
- Existing heuristic semantic extraction used by Track B archive creation

## Scope

- Add synthesizer abstraction for archive-facing character summaries
- Add model-guided synthesis path with heuristic fallback
- Add section normalization step that maps synthesis output back into archive writeback payloads
- Wire the builder flow to use synthesis before archive creation

## Non-Goals

- No confirmation-before-overwrite UX yet
- No archive/projection sync diagnostics yet
- No redesign of Discord-facing archive commands beyond consuming richer data
