<!--
Thanks for opening a PR. Filling these in well is the fastest path to a merge.
-->

## Summary

<!-- What does this PR do, in one sentence? -->

## Why

<!-- Linked issue, or 1–2 lines on the user-visible problem this solves. -->

Closes #

## What changed

<!-- Bullet list of the actual changes. -->

-

## How to verify

<!-- The exact steps a reviewer should take to confirm this works. -->

1.
2.
3.

## Screenshots / GIF

<!-- Required for any UI change. Drag-drop into the comment box. -->

## Checklist

- [ ] `ruff check .` passes
- [ ] `ruff format --check .` passes
- [ ] `pytest --cov=recommender` passes
- [ ] Branch name and commits follow Conventional Commits
- [ ] No catalogue CSVs regenerated unless that is the subject of this PR
- [ ] No unrelated formatting churn
- [ ] If a new dependency was added: justified in the PR body
- [ ] If a filter axis changed: tests added or updated in `tests/test_filters.py`
- [ ] If UI change: screenshot or GIF attached above

## Out of scope

<!-- Anything reviewers might expect but is intentionally not in this PR. -->

-
