"""Laptop recommendation engine — pure pandas filters, no Streamlit imports.

The public surface is :func:`apply_filters` plus the per-axis filter functions.
Each per-axis function is a pure (df, selected) -> df transformation; chaining
them yields the same result as the legacy in-line ``filterLaptops()`` body but
fixes two operator-precedence bugs that previously caused the Portability and
Graphics axes to filter on the wrong column.
"""

from .filters import (
    apply_filters,
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
)

__all__ = [
    "apply_filters",
    "filter_by_intended_use",
    "filter_by_brand",
    "filter_by_processor_performance",
    "filter_by_budget",
    "filter_by_os",
    "filter_by_ram",
    "filter_by_storage",
    "filter_by_screen_size",
    "filter_by_graphics",
    "filter_by_portability",
    "filter_by_touchscreen",
    "filter_by_warranty",
]
