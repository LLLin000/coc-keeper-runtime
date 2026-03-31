# Repository Sync Self-Check

This note describes how to verify that `C:\Users\tan\coc-keeper-runtime` matches the latest GitHub `master`, and how to sync safely when local changes exist.

## Goal

Use this checklist to answer two questions:

1. Is my local repository already aligned with `origin/master`?
2. If not, how do I sync without losing local work?

## Quick check

Run these commands from `C:\Users\tan\coc-keeper-runtime`:

```powershell
git status --short --branch
git remote -v
git fetch --all --prune
git branch -vv
git rev-list --left-right --count HEAD...origin/master
git log --oneline HEAD..origin/master
```

How to read the result:

- `git status --short --branch`
  - If you see only `## master...origin/master`, the working tree is clean and you are on `master`.
  - If you see `M`, `D`, `??`, or other entries, you have local changes to protect before syncing.
- `git rev-list --left-right --count HEAD...origin/master`
  - Output format is `<local-only> <remote-only>`.
  - Example: `0 0` means fully aligned.
  - Example: `1 27` means your current commit has 1 local-only commit and is missing 27 remote commits.
- `git log --oneline HEAD..origin/master`
  - Lists commits that exist on GitHub but not locally.

## Safe sync to latest master

If you want the local repo to exactly follow the latest remote `master`, use this flow:

```powershell
git stash push -u -m "sync-before-master-YYYY-MM-DD"
git checkout master
git fetch --all --prune
git merge --ff-only origin/master
git status --short --branch
git rev-list --left-right --count HEAD...origin/master
```

Expected success state:

- `git status --short --branch` shows `## master...origin/master`
- `git rev-list --left-right --count HEAD...origin/master` prints `0 0`

## Why this flow is safe

- `git stash push -u` protects tracked and untracked local changes before switching branches.
- `git checkout master` moves you to the branch that tracks GitHub's default branch.
- `git merge --ff-only origin/master` updates local `master` without creating an extra merge commit.
- The final status and rev-list checks confirm that the local branch matches the remote branch tip.

## Restore your previous local work

If you need the stashed work again:

```powershell
git stash list
git stash show --stat stash@{0}
git stash pop stash@{0}
```

Notes:

- Prefer `git stash show --stat` first so you know what will come back.
- If you want to keep the stash after restoring it, use `git stash apply stash@{0}` instead of `pop`.
- If the stash came from another branch, apply it carefully because file paths may have changed after sync.

## Repo-specific notes

For this repository, `origin` is:

```powershell
https://github.com/tanlearner123/coc-keeper-runtime
```

If Git blocks commands with a `detected dubious ownership` error in the Codex sandbox, allow this repo once:

```powershell
git config --global --add safe.directory C:/Users/tan/coc-keeper-runtime
```

## One-command verification set

When you only want to confirm alignment and not change anything:

```powershell
git fetch --all --prune
git status --short --branch
git rev-list --left-right --count HEAD...origin/master
git show -s --format="%H%n%ci%n%s" HEAD
git show -s --format="%H%n%ci%n%s" origin/master
```

Interpretation:

- If the two `git show` outputs match, local `HEAD` and `origin/master` point to the same commit.
- If they differ, the repo is not fully synced to the latest GitHub `master`.
