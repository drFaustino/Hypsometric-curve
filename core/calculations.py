# -*- coding: utf-8 -*-
"""
Hypsometric calculations module
QGIS 4 + Qt6 + NumPy optimization
"""

import numpy as np


class HypsometricCalculator:
    """
    Handles all numerical computations:
    - intervals
    - partial and cumulative areas
    - statistical means
    - h_med
    - HI (Hypsometric Integral)
    """

    # ------------------------------------------------------------------ #
    # INTERVALS
    # ------------------------------------------------------------------ #

    def compute_intervals(self, h_min, h_max, num_classes):
        """
        Returns an array of interval boundaries.
        """
        return np.linspace(h_min, h_max, num_classes + 1)

    # ------------------------------------------------------------------ #
    # AREAS
    # ------------------------------------------------------------------ #

    def compute_areas(self, data, mask, intervals, cell_area):
        """
        Computes:
        - partial areas for each elevation interval
        - cumulative areas (from top to bottom)
        """

        # Extract only valid pixels inside basin
        valid = data[mask]

        partial_areas = []
        num_classes = len(intervals) - 1

        for i in range(num_classes):
            lower = intervals[i]
            upper = intervals[i + 1]

            # Boolean mask for interval
            interval_mask = (valid >= lower) & (valid < upper)
            area = np.sum(interval_mask) * cell_area
            partial_areas.append(area)

        partial_areas = np.array(partial_areas)

        # Cumulative areas from top to bottom
        cumulative_areas = np.cumsum(partial_areas[::-1])[::-1]

        return partial_areas, cumulative_areas

    # ------------------------------------------------------------------ #
    # STATISTICS
    # ------------------------------------------------------------------ #

    def compute_statistical_means(self, data, mask, intervals):
        """
        Computes mean elevation for each interval.
        """

        valid = data[mask]
        means = []
        num_classes = len(intervals) - 1

        for i in range(num_classes):
            lower = intervals[i]
            upper = intervals[i + 1]

            interval_values = valid[(valid >= lower) & (valid < upper)]
            means.append(interval_values.mean() if interval_values.size > 0 else 0)

        return np.array(means)

    # ------------------------------------------------------------------ #
    # H_MED
    # ------------------------------------------------------------------ #

    def compute_h_med(self, data, mask):
        """
        Computes the mean elevation of the basin.
        Equivalent to the mean of all valid pixels.
        """
        valid = data[mask]
        return float(valid.mean())

    # ------------------------------------------------------------------ #
    # HYPSOMETRIC INTEGRAL (HI)
    # ------------------------------------------------------------------ #

    def compute_HI(self, intervals, h_min, h_max):
        """
        Computes the Hypsometric Integral using the classical formula:
        HI = (mean elevation - h_min) / (h_max - h_min)
        """

        if h_max == h_min:
            return 0.0

        # Mean of interval midpoints
        mids = (intervals[:-1] + intervals[1:]) / 2
        mean_mid = mids.mean()

        return float((mean_mid - h_min) / (h_max - h_min))
