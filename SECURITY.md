# Security policy

## Supported versions

This project is pre-1.0. Only the latest tagged release on `main` receives
security fixes. There is no long-term-support branch.

| Version | Supported |
|---------|-----------|
| Latest tagged release | ✅ |
| Older releases | ❌ |
| Unreleased `main` | Best-effort |

## Reporting a vulnerability

Please **do not** file a public GitHub issue for security problems.

Instead, email **shubhayansh@gmail.com** with:

- A description of the issue and its impact.
- Steps to reproduce, or a minimal proof of concept.
- The commit hash or release version you tested against.

You should get a first reply within 7 days. If you don't, please nudge by
replying to your own email; mail filters are imperfect.

## Scope

This is a single-page Streamlit data app. It has no authentication, no user
accounts, and stores no personal data. The meaningful security surface is
small and worth being explicit about.

In scope:

- **The Flipkart scraper** (`get_image_and_price()` in `app.py`). It issues an
  outbound HTTP request to a URL drawn from the catalogue CSV and parses the
  response with BeautifulSoup. Anything that could turn a crafted catalogue
  row or a crafted Flipkart response into request forgery, code execution, or
  a denial-of-service against the host is in scope.
- **Catalogue ingestion.** The app reads `cleaned_laptops_updated.csv` at
  start-up. Anything that could make a malicious CSV escalate beyond a bad
  recommendation — for example via pandas parsing or downstream string
  formatting — is in scope.
- **Dependency vulnerabilities** in the pinned runtime stack (`streamlit`,
  `pandas`, `requests`, `beautifulsoup4`, `lxml`).

Out of scope:

- Issues that require physical access to the host machine.
- The accuracy or freshness of recommendations — the catalogue is a known
  January 2024 snapshot.
- Broken click-through previews caused by Flipkart rotating its HTML class
  names. That is a documented caveat, not a vulnerability.
- Findings against a self-hosted deployment's own infrastructure
  (reverse proxy, TLS termination, hosting platform).

## Disclosure timeline

The default is coordinated disclosure. Once a fix ships in a tagged release,
an advisory is published in the repository's Security Advisories tab,
crediting the reporter (or anonymous if preferred).

## What this project does not do

- Does not collect, store, or transmit personal data.
- Does not require or store any credentials or API keys.
- Does not transmit telemetry.
