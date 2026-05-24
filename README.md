# 💻 Laptop Price Recommender

> A Streamlit recommendation app that takes a laptop shopper's spec preferences across nine dimensions — intended use, budget, RAM, storage, screen size, OS, graphics, portability, warranty — and returns the matching laptops from a cleaned Flipkart dataset, with live image and price scraping on click-through.

[![Built with Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![pandas](https://img.shields.io/badge/pandas-150458?logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![ci](https://github.com/shubhyansh/laptop-price-recommender/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/shubhyansh/laptop-price-recommender/actions/workflows/ci.yml)
[![codeql](https://github.com/shubhyansh/laptop-price-recommender/actions/workflows/codeql.yml/badge.svg?branch=main)](https://github.com/shubhyansh/laptop-price-recommender/actions/workflows/codeql.yml)
[![ruff](https://img.shields.io/badge/lint-ruff-D7FF64?logo=ruff&logoColor=black)](https://docs.astral.sh/ruff/)
[![pytest](https://img.shields.io/badge/tested%20with-pytest-0A9EDC?logo=pytest&logoColor=white)](https://docs.pytest.org/)

---

## What it does

A shopper opens the app and walks through nine multi-select preference questions:

| # | Question | Example options |
|---|----------|-----------------|
| 1 | Intended use | Studying, Programming, Gaming, Multimedia |
| 2 | Preferred brand | HP, Dell, Lenovo, Apple, ASUS, … |
| 3 | Processor performance | Moderate (i5/Ryzen 5), Intensive (i7-i9/Ryzen 7-9) |
| 4 | Budget range | Under 40k, 40-55k, 55-70k, 70-85k, 85k+ |
| 5 | RAM | 4-8 GB, 8-16 GB, 16 GB+ |
| 6 | Storage | 0-128 GB, 128-256 GB, 256-512 GB, 512 GB-1 TB, 1 TB+ |
| 7 | Screen size | 11-13", 13-14", 14-15", 15"+ |
| 8 | OS | Windows, macOS, ChromeOS, Linux, DOS |
| 9 | Graphics / portability / touch / warranty filters | (independent toggles) |

Submit → the app filters the cleaned Flipkart catalogue (≈ 900 rows, January 2024 snapshot) and returns matches sorted by latest price. Click a result → the app re-scrapes its Flipkart page live to refresh the image and the current price (catalogue prices are read-only).

## Demo

A pre-recorded walkthrough is checked in at [`demo.mp4`](demo.mp4) and [`demo.webm`](demo.webm). A live Streamlit Community Cloud deployment is linked from the repo's "About" sidebar once it lands.

## Quick start

```bash
git clone git@github.com:shubhyansh/laptop-price-recommender.git
cd laptop-price-recommender
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

The app reads `cleaned_laptops_updated.csv` from the repo root and binds to `localhost:8501`.
## Running the tests

```bash
pip install -r requirements-dev.txt
pytest --cov=recommender
```

The suite has 52 tests covering each filter axis plus a snapshot test that pins the dispatcher output against the catalogue CSV. CI runs the suite across Python 3.10 / 3.11 / 3.12 on every push and pull request to `main`.

## Data

Three CSVs ship with the repo, each a successive refinement of a Flipkart scrape captured in early 2024:

| File | Rows | Purpose |
|------|------|---------|
| `laptops_updated.csv` | raw | Initial scrape — kept for reproducibility |
| `cleaned_laptops_updated.csv` | cleaned | Used by `app.py` — flat boolean feature columns for each use-case |
| `cleaned_laptops_final.csv` | cleaned + extra normalisations | Used by the analysis notebooks |
| `Cleaned_Laptop_data.csv` | smaller side-cut | Used by `id.ipynb` for the product-ID join |

## Notebooks

| Notebook | What's in it |
|----------|--------------|
| `analysis.ipynb` | Price-distribution EDA, feature importance, correlation heatmaps |
| `price.ipynb` | Price-prediction model exploration (regression baselines) |
| `image.ipynb` | Product-image fetch + thumbnail caching experiments |
| `id.ipynb` | Product-ID reconciliation between scrape passes |

## Repo layout

```
laptop-price-recommender/
├── app.py                          Streamlit app — filters + result rendering
├── requirements.txt                Pinned runtime deps
├── .streamlit/config.toml          Theme (Flipkart-pink primary)
├── cleaned_laptops_updated.csv     Catalogue used by the app
├── cleaned_laptops_final.csv       Notebook catalogue
├── laptops_updated.csv             Raw scrape
├── Cleaned_Laptop_data.csv         ID-join side-cut
├── analysis.ipynb                  EDA
├── price.ipynb                     Price prediction
├── image.ipynb                     Image scraping/caching experiments
├── id.ipynb                        Product-ID reconciliation
├── flipkarLogo.png, OIG.jpeg       Static assets used by the app UI
├── demo.mp4 / demo.webm            Pre-recorded walkthrough
└── LICENSE
```

## Caveats

- The Flipkart scraper inside `get_image_and_price()` depends on Flipkart's HTML class names (`_2c7YLP`, `_396cs4`, `_30jeq3`) — those rotate periodically. If the click-through preview stops rendering, the selector is the first place to look.
- The catalogue is a January 2024 snapshot. Prices and stock are read-only against that snapshot until a fresh scrape lands.
- The filter logic intentionally widens the result set when a category is left blank, on the assumption that "no preference stated" means "open to anything." Some filters use exclusion-then-rejoin rather than direct equality — see `filterLaptops()` in `app.py`.

## License

MIT. See [LICENSE](LICENSE).

---

**Built by [@shubhyansh](https://github.com/shubhyansh).**
