# Pre-Reset Root Snapshot — `PROJECT.md`

At reset time, the repository root still described the product through 5 long-lived tracks:

1. `track-a` — module and rules runtime
2. `track-b` — character builder, archive, governance
3. `track-c` — Discord interaction layer
4. `track-d` — presentation and keeper-feel
5. `track-e` — runtime control and verification

That model was good enough to bootstrap parallel work, but started to accumulate overlap:

- runtime semantics leaked between A and C
- archive truth and presentation split awkwardly across B and D
- Discord operator UX and operational verification blurred between C and E

The reset replaced that model with 4 clearer ownership lanes:

- `track-runtime`
- `track-identity`
- `track-surface`
- `track-ops`

See archived workstream directories under:

- `../workstreams/`
