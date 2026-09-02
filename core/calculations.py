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
        """Returns an array of interval boundaries."""
        num_classes = int(num_classes)
        if num_classes < 1:
            raise ValueError("Il numero di classi deve essere maggiore di zero.")
        if h_max < h_min:
            raise ValueError("L'elevazione massima non può essere inferiore a quella minima.")
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
        if np.ma.isMaskedArray(valid):
            valid = valid.compressed()
        else:
            valid = np.asarray(valid)

        partial_areas = []
        num_classes = len(intervals) - 1

        for i in range(num_classes):
            lower = intervals[i]
            upper = intervals[i + 1]

            # Boolean mask for interval
            if i == num_classes - 1:
                interval_mask = (valid >= lower) & (valid <= upper)
            else:
                interval_mask = (valid >= lower) & (valid < upper)
            area = np.count_nonzero(interval_mask) * cell_area
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
        if np.ma.isMaskedArray(valid):
            valid = valid.compressed()
        else:
            valid = np.asarray(valid)
        means = []
        num_classes = len(intervals) - 1

        for i in range(num_classes):
            lower = intervals[i]
            upper = intervals[i + 1]

            if i == num_classes - 1:
                interval_values = valid[(valid >= lower) & (valid <= upper)]
            else:
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
        if np.ma.isMaskedArray(valid):
            valid = valid.compressed()
        else:
            valid = np.asarray(valid)
        if valid.size == 0:
            raise ValueError("Nessun valore valido disponibile nel bacino.")
        return float(valid.mean())

    # ------------------------------------------------------------------ #
    # HYPSOMETRIC INTEGRAL (HI)
    # ------------------------------------------------------------------ #

    def compute_HI(self, h_med, h_min, h_max):
        """
        Computes the Hypsometric Integral (Pike & Wilson, 1971):
        HI = (h_med - h_min) / (h_max - h_min)
        """
        if h_max == h_min:
            return 0.0
        return float((h_med - h_min) / (h_max - h_min))
