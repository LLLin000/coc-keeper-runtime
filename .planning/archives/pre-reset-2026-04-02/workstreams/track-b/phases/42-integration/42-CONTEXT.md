# Phase 42 Context

## Goal

Integrate the normalization and synthesis layers into live archive and campaign flows without breaking existing Track B behavior.

## Focus

- Preserve explicit player intent fields during writeback
- Automatically sync selected archive profiles into campaign projections
- Surface projection sync status through diagnostics
- Keep backward-compatible fallback behavior when model synthesis is weak or missing

## Non-Goals

- Full redesign of builder UX
- New Discord command families beyond Track B integration needs
- Activity or rich UI panel work
