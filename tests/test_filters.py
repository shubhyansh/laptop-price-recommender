"""Unit + snapshot tests for ``recommender.filters``.

Per-axis unit tests run against the in-memory ``synthetic_df`` fixture so the
suite is self-contained. The dispatcher's behaviour against the real
catalogue (``cleaned_laptops_updated.csv``, 896 rows) is pinned by a single
snapshot test that uses the ``real_df`` fixture and skips when the CSV is
absent.

The two operator-precedence bug-fixes called out in
``recommender/filters.py`` (Graphics and Portability axes) have dedicated
positive tests so a regression that re-introduces the bug fails loudly.
"""

from __future__ import annotations

import pandas as pd
import pytest

from recommender import apply_filters
from recommender.filters import (
    filter_by_brand,
    filter_by_budget,
    filter_by_graphics,
    filter_by_intended_use,
    filter_by_os,
    filter_by_portability,
    filter_by_processor_performance,
    filter_by_ram,
    filter_by_screen_size,
    filter_by_storage,
    filter_by_touchscreen,
    filter_by_warranty,
)

# ---------------------------------------------------------------------------
# Empty-selection no-op contract — every axis must return the input unchanged.
# ---------------------------------------------------------------------------

EVERY_AXIS = [
    filter_by_intended_use,
    filter_by_brand,
    filter_by_processor_performance,
    filter_by_budget,
    filter_by_os,
    filter_by_ram,
    filter_by_storage,
    filter_by_screen_size,
    filter_by_graphics,
    filter_by_portability,
    filter_by_touchscreen,
    filter_by_warranty,
]


@pytest.mark.parametrize("fn", EVERY_AXIS)
def test_empty_selection_is_noop(fn, synthetic_df):
    out = fn(synthetic_df, [])
    assert len(out) == len(synthetic_df)
    pd.testing.assert_frame_equal(out, synthetic_df)


# Function-mapped axes (intended_use / processor_performance / graphics /
# portability / touchscreen / warranty) fall through to ``return df`` when no
# recognised label is selected — pin that behaviour. Band/isin axes (brand /
# os / budget / ram / storage / screen_size) do NOT have this guarantee — an
# unknown label returns an empty frame because the isin/mask matches nothing,
# matching the legacy app.py contract.

FALLTHROUGH_AXES = [
    filter_by_intended_use,
    filter_by_processor_performance,
    filter_by_graphics,
    filter_by_portability,
    filter_by_touchscreen,
    filter_by_warranty,
]


@pytest.mark.parametrize("fn", FALLTHROUGH_AXES)
def test_unknown_label_falls_through(fn, synthetic_df):
    out = fn(synthetic_df, ["this-label-does-not-exist"])
    assert len(out) == len(synthetic_df)


# ---------------------------------------------------------------------------
# Intended Use — union semantics
# ---------------------------------------------------------------------------


def test_intended_use_single_axis(synthetic_df):
    assert len(filter_by_intended_use(synthetic_df, ["Gaming"])) == 7
    assert len(filter_by_intended_use(synthetic_df, ["Studying"])) == 8


def test_intended_use_union_of_two_axes(synthetic_df):
    # Programming has 13 rows, Gaming has 7, overlap = 5 (rows 5,9,10,11,16).
    out = filter_by_intended_use(synthetic_df, ["Programming", "Gaming"])
    assert len(out) == 15


# ---------------------------------------------------------------------------
# Brand / OS — straight isin
# ---------------------------------------------------------------------------


def test_brand_single(synthetic_df):
    out = filter_by_brand(synthetic_df, ["HP"])
    assert len(out) == 3
    assert (out["brand"] == "HP").all()


def test_brand_multi(synthetic_df):
    out = filter_by_brand(synthetic_df, ["HP", "Dell", "Apple"])
    assert len(out) == 7
    assert set(out["brand"].unique()) == {"HP", "Dell", "Apple"}


def test_os_filter(synthetic_df):
    assert len(filter_by_os(synthetic_df, ["Windows"])) == 17
    assert len(filter_by_os(synthetic_df, ["macOS"])) == 1
    assert len(filter_by_os(synthetic_df, ["Linux", "DOS"])) == 2


# ---------------------------------------------------------------------------
# Budget — exact band counts + disjoint union
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "label,expected_count,price_check",
    [
        ("Under 40k", 5, lambda s: (s < 40000).all()),
        ("40k - 55k", 3, lambda s: ((s >= 40000) & (s < 55000)).all()),
        ("55k - 70k", 3, lambda s: ((s >= 55000) & (s < 70000)).all()),
        ("70k - 85k", 3, lambda s: ((s >= 70000) & (s < 85000)).all()),
        ("85k above", 6, lambda s: (s >= 85000).all()),
    ],
)
def test_budget_band(synthetic_df, label, expected_count, price_check):
    out = filter_by_budget(synthetic_df, [label])
    assert len(out) == expected_count
    assert price_check(out["latest_price"])


def test_budget_bands_partition_the_catalogue(synthetic_df):
    """All five bands together must cover every row exactly once."""
    all_bands = ["Under 40k", "40k - 55k", "55k - 70k", "70k - 85k", "85k above"]
    out = filter_by_budget(synthetic_df, all_bands)
    assert len(out) == len(synthetic_df)


# ---------------------------------------------------------------------------
# RAM bands
# ---------------------------------------------------------------------------


def test_ram_low_band(synthetic_df):
    out = filter_by_ram(synthetic_df, ["4GB - 8GB"])
    assert len(out) == 12
    assert ((out["ram_gb"] >= 4) & (out["ram_gb"] <= 8)).all()


def test_ram_high_band_no_upper_bound(synthetic_df):
    out = filter_by_ram(synthetic_df, ["16GB+"])
    assert len(out) == 8
    assert (out["ram_gb"] >= 16).all()


# ---------------------------------------------------------------------------
# Storage — uses ssd + hdd sum
# ---------------------------------------------------------------------------


def test_storage_1tb_plus(synthetic_df):
    out = filter_by_storage(synthetic_df, ["1TB+"])
    assert len(out) == 4
    total = out["ssd"] + out["hdd"]
    assert (total >= 1024).all()


def test_storage_low_band(synthetic_df):
    out = filter_by_storage(synthetic_df, ["0 GB - 128GB"])
    total = out["ssd"] + out["hdd"]
    assert (total <= 128).all()


# ---------------------------------------------------------------------------
# Screen size
# ---------------------------------------------------------------------------


def test_screen_15_plus(synthetic_df):
    out = filter_by_screen_size(synthetic_df, ["15+ inches"])
    assert len(out) == 9
    assert (out["display_size"] >= 15).all()


def test_screen_11_13_empty(synthetic_df):
    # No 11-13" laptops in the synthetic catalogue.
    out = filter_by_screen_size(synthetic_df, ["11 - 13 inches"])
    assert len(out) == 0


# ---------------------------------------------------------------------------
# Processor Performance — Basic-tasks alone is a no-op
# ---------------------------------------------------------------------------


def test_processor_basic_alone_is_noop(synthetic_df):
    """Behaviour change called out in the refactor: legacy code returned an
    empty frame when only "Basic tasks" was selected because the dispatch
    table had no entry. The fixed implementation treats it as no-op."""
    out = filter_by_processor_performance(
        synthetic_df, ["Basic tasks (Intel Core i3 or equivalent AMD)"]
    )
    assert len(out) == len(synthetic_df)


def test_processor_moderate(synthetic_df):
    out = filter_by_processor_performance(
        synthetic_df, ["Moderate multitasking (Intel Core i5 or equivalent AMD Ryzen 5)"]
    )
    assert len(out) == 10
    assert (out["Medium"] == True).all()  # noqa: E712


def test_processor_intensive(synthetic_df):
    out = filter_by_processor_performance(
        synthetic_df, ["Intensive tasks (Intel Core i7/i9 or equivalent AMD Ryzen 7/9)"]
    )
    assert len(out) == 7
    assert (out["Advanced"] == True).all()  # noqa: E712


def test_processor_union_of_two(synthetic_df):
    out = filter_by_processor_performance(
        synthetic_df,
        [
            "Moderate multitasking (Intel Core i5 or equivalent AMD Ryzen 5)",
            "Intensive tasks (Intel Core i7/i9 or equivalent AMD Ryzen 7/9)",
        ],
    )
    # Medium=10, Advanced=7, overlap=1 (row 5 carries both flags).
    assert len(out) == 16


# ---------------------------------------------------------------------------
# Graphics — the parenthesised-OR bug-fix
# ---------------------------------------------------------------------------


def test_graphics_heavy_is_gaming_only(synthetic_df):
    out = filter_by_graphics(synthetic_df, ["Heavy gaming or professional video editing/rendering"])
    assert len(out) == 7
    assert (out["Gaming"] == True).all()  # noqa: E712


def test_graphics_moderate_is_gaming_or_programming(synthetic_df):
    """Regression-pin for bug-fix #1.

    Legacy: ``df["Gaming"] == True | df["Programming"] == True`` parsed as
    ``df["Gaming"] == (True | df["Programming"]) == True`` — i.e. truthiness
    on the column. The fixed expression is a real OR over both equalities,
    which on the synthetic frame equals 15 rows (Gaming=7 ∪ Programming=13,
    overlap=5).
    """
    out = filter_by_graphics(synthetic_df, ["Moderate gaming and video editing"])
    assert len(out) == 15
    # Every surviving row must be flagged Gaming or Programming.
    assert ((out["Gaming"] == True) | (out["Programming"] == True)).all()  # noqa: E712


# ---------------------------------------------------------------------------
# Portability — the second parenthesised-OR bug-fix
# ---------------------------------------------------------------------------


def test_portability_very_important_is_thinNlight_only(synthetic_df):
    out = filter_by_portability(synthetic_df, ["Very important (Looking for lightweight options)"])
    assert len(out) == 6
    assert (out["weight"] == "ThinNlight").all()


def test_portability_moderate_excludes_gaming_weight(synthetic_df):
    """Regression-pin for bug-fix #2.

    The synthetic frame has 9 Casual + 6 ThinNlight + 5 Gaming-weight rows.
    "Moderate" should match Casual ∪ ThinNlight = 15 rows; every Gaming-weight
    row must be filtered out.
    """
    out = filter_by_portability(synthetic_df, ["Moderate (Balanced weight and performance)"])
    assert len(out) == 15
    assert (out["weight"] != "Gaming").all()
    assert set(out["weight"].unique()) == {"Casual", "ThinNlight"}


# ---------------------------------------------------------------------------
# Touchscreen — boolean column
# ---------------------------------------------------------------------------


def test_touchscreen_yes(synthetic_df):
    out = filter_by_touchscreen(synthetic_df, ["Yes, I prefer a touchscreen"])
    assert len(out) == 2
    assert (out["Touchscreen"] == True).all()  # noqa: E712


def test_touchscreen_no(synthetic_df):
    out = filter_by_touchscreen(synthetic_df, ["No, I don't need a touchscreen"])
    assert len(out) == 18
    assert (out["Touchscreen"] == False).all()  # noqa: E712


# ---------------------------------------------------------------------------
# Warranty — inline frame (synthetic catalogue has no warranty=0 rows)
# ---------------------------------------------------------------------------


def test_warranty_longer_filters_zero_warranty_rows():
    inline = pd.DataFrame({"warranty": [0, 1, 2, 0, 1]})
    out = filter_by_warranty(inline, ["Longer warranty and premium support services"])
    assert len(out) == 3
    assert (out["warranty"] >= 1).all()


# ---------------------------------------------------------------------------
# apply_filters dispatcher — composition + spec-key tolerance
# ---------------------------------------------------------------------------


def test_apply_filters_empty_spec_returns_all(synthetic_df):
    out = apply_filters(synthetic_df, {})
    assert len(out) == len(synthetic_df)


def test_apply_filters_ignores_unmapped_spec_keys(synthetic_df):
    """Keys the dataset can't back (Display Panel Type, Battery Life, etc.)
    must be silently ignored — matches the legacy app.py behaviour."""
    out = apply_filters(
        synthetic_df,
        {
            "Display Panel Type": ["IPS LCD"],
            "Battery Life Priority": ["Long"],
            "Keyboard Type": ["Backlit"],
        },
    )
    assert len(out) == len(synthetic_df)


def test_apply_filters_composes_two_axes(synthetic_df):
    """RAM 16GB+ ∩ Brand=Dell. From synthetic_df:
    16GB+ rows = 8 (rows 4,5,8,9,10,11,16,17), Brand=Dell = 3 (rows 4,5,6).
    Intersection on row indices {4,5} → 2 rows.
    """
    out = apply_filters(
        synthetic_df,
        {
            "RAM Requirement": ["16GB+"],
            "Preferred Brands or Models": ["Dell"],
        },
    )
    assert len(out) == 2
    assert (out["ram_gb"] >= 16).all()
    assert (out["brand"] == "Dell").all()


def test_apply_filters_does_not_mutate_input(synthetic_df):
    """The dispatcher copies df at entry — callers must see the original frame
    untouched even after a heavy filter pass."""
    before = synthetic_df.copy()
    _ = apply_filters(
        synthetic_df,
        {
            "Intended Use": ["Programming"],
            "Budget Range": ["55k - 70k"],
            "RAM Requirement": ["8GB - 16GB"],
        },
    )
    pd.testing.assert_frame_equal(synthetic_df, before)


# ---------------------------------------------------------------------------
# Real-catalogue snapshot test (W21 Build PR pinned this exact spec → 99 rows)
# ---------------------------------------------------------------------------


def test_apply_filters_spec_snapshot(real_df):
    """Regression pin captured during the W21 Build day smoke test.

    Spec: Intended Use = Programming, Budget = 55k - 70k, RAM = 8GB - 16GB.
    Against ``cleaned_laptops_updated.csv`` (896 rows), this filters to 99
    rows. The number is the contract — if the catalogue changes the test
    breaks and the new count gets reviewed.
    """
    spec = {
        "Intended Use": ["Programming"],
        "Budget Range": ["55k - 70k"],
        "RAM Requirement": ["8GB - 16GB"],
    }
    out = apply_filters(real_df, spec)
    assert len(out) == 99


def test_real_catalogue_row_count(real_df):
    """Catalogue is 896 rows in W21. A test that breaks if the CSV is
    re-cut without updating the snapshot pins above."""
    assert len(real_df) == 896
