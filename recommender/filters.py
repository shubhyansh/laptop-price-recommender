"""Per-axis filter functions for the laptop recommender.

Each ``filter_by_*`` is a pure function:
    (df: pd.DataFrame, selected: list[str]) -> pd.DataFrame

If ``selected`` is empty the function returns ``df`` unchanged (no-op) — this
mirrors the legacy ``filterLaptops()`` contract where an empty multiselect on
the sidebar meant "don't filter on that axis".

The legacy in-line implementation in ``app.py`` had two operator-precedence
bugs that silently filtered on the wrong axis:

* Graphics axis: ``df["Gaming"] == True | df["Programming"] == True`` — the
  bitwise ``|`` binds tighter than ``==``, so this parsed as
  ``df["Gaming"] == (True | df["Programming"]) == True``.
* Portability axis: same shape on the ``weight`` column.

The fixed expressions in :func:`filter_by_graphics` and
:func:`filter_by_portability` parenthesise each equality.
"""

from __future__ import annotations

from typing import Iterable, Mapping

import pandas as pd


# ---------------------------------------------------------------------------
# Per-axis filters
# ---------------------------------------------------------------------------


def filter_by_intended_use(df: pd.DataFrame, selected: Iterable[str]) -> pd.DataFrame:
    """Keep rows flagged for at least one of the selected intended-use buckets.

    The dataset carries four boolean columns: ``Studying``, ``Programming``,
    ``Gaming``, ``Multimedia``. A row "matches" the intended-use selection if
    any of the user-picked columns is ``True`` on that row.
    """
    selected = list(selected)
    if not selected:
        return df
    all_options = ["Studying", "Programming", "Gaming", "Multimedia"]
    picked = [opt for opt in selected if opt in all_options]
    if not picked:
        return df
    mask = pd.Series(False, index=df.index)
    for opt in picked:
        mask = mask | (df[opt] == True)  # noqa: E712 (pandas requires == for vector compare)
    return df[mask]


def filter_by_brand(df: pd.DataFrame, selected: Iterable[str]) -> pd.DataFrame:
    selected = list(selected)
    if not selected:
        return df
    return df[df["brand"].isin(selected)]


def filter_by_processor_performance(
    df: pd.DataFrame, selected: Iterable[str]
) -> pd.DataFrame:
    """Map the human-readable processor tier strings onto the dataset's
    boolean columns ``Medium`` (i5 / Ryzen 5) and ``Advanced`` (i7-i9 / Ryzen 7-9).

    Basic tier has no dedicated column — every laptop is at least basic — so
    selecting it alone is effectively a no-op against the catalogue.
    """
    selected = list(selected)
    if not selected:
        return df
    tier_columns = {
        "Moderate multitasking (Intel Core i5 or equivalent AMD Ryzen 5)": "Medium",
        "Intensive tasks (Intel Core i7/i9 or equivalent AMD Ryzen 7/9)": "Advanced",
    }
    picked_columns = [col for label, col in tier_columns.items() if label in selected]
    if not picked_columns:
        # Only "Basic tasks" picked — every row qualifies; return df unchanged.
        return df
    mask = pd.Series(False, index=df.index)
    for col in picked_columns:
        mask = mask | (df[col] == True)  # noqa: E712
    return df[mask]


def filter_by_budget(df: pd.DataFrame, selected: Iterable[str]) -> pd.DataFrame:
    """Budget buckets are inclusive at the low end and exclusive at the high end.

    ``Under 40k`` → ``price < 40000``
    ``40k - 55k`` → ``40000 <= price < 55000``
    ``55k - 70k`` → ``55000 <= price < 70000``
    ``70k - 85k`` → ``70000 <= price < 85000``
    ``85k above`` → ``price >= 85000``

    Multiple selections union together.
    """
    selected = list(selected)
    if not selected:
        return df
    bands = {
        "Under 40k": (None, 40000),
        "40k - 55k": (40000, 55000),
        "55k - 70k": (55000, 70000),
        "70k - 85k": (70000, 85000),
        "85k above": (85000, None),
    }
    mask = pd.Series(False, index=df.index)
    for label in selected:
        if label not in bands:
            continue
        low, high = bands[label]
        band_mask = pd.Series(True, index=df.index)
        if low is not None:
            band_mask &= df["latest_price"] >= low
        if high is not None:
            band_mask &= df["latest_price"] < high
        mask = mask | band_mask
    return df[mask]


def filter_by_os(df: pd.DataFrame, selected: Iterable[str]) -> pd.DataFrame:
    selected = list(selected)
    if not selected:
        return df
    return df[df["os"].isin(selected)]


def filter_by_ram(df: pd.DataFrame, selected: Iterable[str]) -> pd.DataFrame:
    selected = list(selected)
    if not selected:
        return df
    bands = {
        "4GB - 8GB": (4, 8),
        "8GB - 16GB": (8, 16),
        "16GB+": (16, None),
    }
    mask = pd.Series(False, index=df.index)
    for label in selected:
        if label not in bands:
            continue
        low, high = bands[label]
        band_mask = df["ram_gb"] >= low
        if high is not None:
            band_mask &= df["ram_gb"] <= high
        mask = mask | band_mask
    return df[mask]


def filter_by_storage(df: pd.DataFrame, selected: Iterable[str]) -> pd.DataFrame:
    """Storage is the sum of ``ssd`` and ``hdd`` columns (both GB).

    Buckets are inclusive on both ends.
    """
    selected = list(selected)
    if not selected:
        return df
    bands = {
        "0 GB - 128GB": (0, 128),
        "128GB - 256GB": (128, 256),
        "256GB - 512GB": (256, 512),
        "512GB - 1TB": (512, 1024),
        "1TB+": (1024, None),
    }
    total = df["ssd"] + df["hdd"]
    mask = pd.Series(False, index=df.index)
    for label in selected:
        if label not in bands:
            continue
        low, high = bands[label]
        band_mask = total >= low
        if high is not None:
            band_mask &= total <= high
        mask = mask | band_mask
    return df[mask]


def filter_by_screen_size(df: pd.DataFrame, selected: Iterable[str]) -> pd.DataFrame:
    selected = list(selected)
    if not selected:
        return df
    bands = {
        "11 - 13 inches": (11, 13),
        "13 - 14 inches": (13, 14),
        "14 - 15 inches": (14, 15),
        "15+ inches": (15, None),
    }
    mask = pd.Series(False, index=df.index)
    for label in selected:
        if label not in bands:
            continue
        low, high = bands[label]
        band_mask = df["display_size"] >= low
        if high is not None:
            band_mask &= df["display_size"] <= high
        mask = mask | band_mask
    return df[mask]


def filter_by_graphics(df: pd.DataFrame, selected: Iterable[str]) -> pd.DataFrame:
    """Bug-fix axis (#1).

    Legacy code:
        df[df["Gaming"] == True | df["Programming"] == True]
    Because ``|`` binds tighter than ``==``, that parsed as
        df[df["Gaming"] == (True | df["Programming"]) == True]
    which evaluated the truthiness of the column itself. Fix: parenthesise each
    equality.
    """
    selected = list(selected)
    if not selected:
        return df
    if "Heavy gaming or professional video editing/rendering" in selected:
        return df[df["Gaming"] == True]  # noqa: E712
    if "Moderate gaming and video editing" in selected:
        return df[(df["Gaming"] == True) | (df["Programming"] == True)]  # noqa: E712
    return df


def filter_by_portability(df: pd.DataFrame, selected: Iterable[str]) -> pd.DataFrame:
    """Bug-fix axis (#2).

    Same precedence bug as :func:`filter_by_graphics`, this time on the
    ``weight`` column. ``df["weight"] == "Casual" | df["weight"] == "ThinNlight"``
    parsed as ``df["weight"] == ("Casual" | df["weight"]) == "ThinNlight"``.
    Fix: parenthesise.
    """
    selected = list(selected)
    if not selected:
        return df
    if "Very important (Looking for lightweight options)" in selected:
        return df[df["weight"] == "ThinNlight"]
    if "Moderate (Balanced weight and performance)" in selected:
        return df[(df["weight"] == "Casual") | (df["weight"] == "ThinNlight")]
    return df


def filter_by_touchscreen(df: pd.DataFrame, selected: Iterable[str]) -> pd.DataFrame:
    selected = list(selected)
    if not selected:
        return df
    if "Yes, I prefer a touchscreen" in selected:
        return df[df["Touchscreen"] == True]  # noqa: E712
    if "No, I don't need a touchscreen" in selected:
        return df[df["Touchscreen"] == False]  # noqa: E712
    return df


def filter_by_warranty(df: pd.DataFrame, selected: Iterable[str]) -> pd.DataFrame:
    selected = list(selected)
    if not selected:
        return df
    if "Longer warranty and premium support services" in selected:
        return df[df["warranty"] >= 1]
    return df


# ---------------------------------------------------------------------------
# Top-level dispatcher
# ---------------------------------------------------------------------------


# Mapping: spec-dict key  ->  per-axis filter function.
# Order is preserved so chained behaviour is deterministic; the only axes that
# actually filter against the dataset are listed here. Unused spec keys
# (``Display Panel Type``, ``Display Resolution``, ``Battery Life Priority``,
# ``Necessary Ports and Connectivity``, ``Importance of Upgradability``,
# ``Keyboard Type``, ``Fingerprint Reader/Security Features``) are accepted by
# the dispatcher but ignored — the dataset doesn't carry the columns to back
# them. This matches the legacy ``filterLaptops()`` body, which silently
# ignored the same keys.
_AXIS_DISPATCH = (
    ("Intended Use", filter_by_intended_use),
    ("Preferred Brands or Models", filter_by_brand),
    ("Processor Performance", filter_by_processor_performance),
    ("Budget Range", filter_by_budget),
    ("Operating System Preference", filter_by_os),
    ("RAM Requirement", filter_by_ram),
    ("Desired Storage Space", filter_by_storage),
    ("Preferred Screen Size", filter_by_screen_size),
    ("Graphics-Intensive Tasks", filter_by_graphics),
    ("Portability Importance", filter_by_portability),
    ("Touchscreen Preference", filter_by_touchscreen),
    ("Warranty and Support", filter_by_warranty),
)


def apply_filters(df: pd.DataFrame, specification: Mapping[str, Iterable[str]]) -> pd.DataFrame:
    """Apply every axis filter in turn and return the surviving rows.

    Behaviour-preserving drop-in replacement for the legacy
    ``filterLaptops(specification, df)`` body in ``app.py`` — except the two
    precedence bugs in the Graphics and Portability axes are fixed (see the
    docstrings on those functions).
    """
    result = df.copy()
    for key, fn in _AXIS_DISPATCH:
        selected = specification.get(key, [])
        result = fn(result, selected)
    return result
