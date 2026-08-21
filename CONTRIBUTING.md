# Contributing to Laptop Price Recommender

Thanks for considering a contribution. This is a small, focused project: a
Streamlit app that filters a cleaned Flipkart catalogue across a set of
preference axes. Contributions that keep it small and focused are the ones
that land fastest.

## Before you start

- Open an issue first for anything bigger than a typo or a one-file fix. A
  short discussion up front saves a round of rework.
- Check existing issues and PRs to avoid duplicate effort.
- Items tracked under the `v0.1.0` milestone are the current priorities.

## Local setup

```bash
git clone git@github.com:shubhyansh/laptop-price-recommender.git
cd laptop-price-recommender
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
streamlit run app.py
```

The app reads `cleaned_laptops_updated.csv` from the repo root and serves on
`localhost:8501`.

## Development workflow

1. Fork the repo and branch off `main`:
   ```bash
   git checkout -b feat/short-name-of-thing
   ```
2. Make focused commits. Branch names and commit subjects follow
   [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat:` new user-visible capability
   - `fix:` bug fix
   - `refactor:` no behaviour change
   - `docs:`, `test:`, `chore:`, `ci:`, `perf:`
3. Keep one logical change per commit. Squash fixups before opening the PR.
4. Run the checks before pushing:
   ```bash
   ruff check .
   ruff format --check .
   pytest --cov=recommender
   ```
5. Push, open a PR against `main`, and fill in the PR template.

## Commit-message hook

The repo ships a versioned `commit-msg` hook that rejects commit subjects that
don't follow Conventional Commits (and rejects lazy subjects like `update`,
`wip`, `stuff`). Enable it once per clone:

```bash
git config core.hooksPath .githooks
```

On Windows the hook runs under Git Bash, which ships with Git for Windows — no
extra setup needed. To check a message without committing:

```bash
echo "feat: add a thing" | .githooks/commit-msg /dev/stdin
```

## Adding a new filter axis

The filter logic lives in `recommender/filters.py` as one pure function per
axis. To add an axis:

1. Write `filter_by_<axis>(df, selected)` — it takes a DataFrame and the list
   of selected option strings, and returns a filtered DataFrame. No Streamlit
   imports; the function must stay pure and importable on its own.
2. An empty `selected` list must be a no-op (return the frame unchanged) — a
   blank preference means "open to anything."
3. Register the axis in `apply_filters()` in the same composition order the
   sidebar presents it.
4. Add the sidebar widget in `app.py` and wire its value into the
   `specification` dict.
5. Add tests in `tests/test_filters.py`: at minimum one positive case and one
   empty-selection no-op case.

## What "good" looks like for a PR

- A concrete, scoped title — no `update` / `wip`.
- A description that answers: what changed, why, how to verify. Screenshots or
  a GIF for any UI change.
- The smallest diff that solves the problem. No unrelated formatting churn.
- No new dependencies without a one-line justification in the PR body.
- No catalogue CSVs regenerated unless that is the explicit subject of the PR.

## Testing

`tests/test_filters.py` covers every filter axis plus the `apply_filters`
dispatcher. New filter logic needs a test alongside it. The suite uses a small
in-memory synthetic frame for unit coverage and skips the real-catalogue tests
cleanly if the CSV is absent, so a shallow checkout still passes.

## Reporting bugs

Open an issue with the **Bug report** template. A short, exact repro is the
single most useful thing you can provide. If the click-through preview breaks,
note that the Flipkart scraper depends on rotating HTML class names — see the
README "Caveats" section.

## Reporting security issues

Don't open a public issue for security problems. See [SECURITY.md](SECURITY.md).

## Code of conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md).
