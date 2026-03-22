#! python3  # noqa: E265

# ----------------------------------------------------------
# Copyright (C) 2015 Martin Dobias
# ----------------------------------------------------------
# Licensed under the terms of GNU GPL 2
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# --------------------------------------------------------------------

# -*- coding: utf-8 -*-

def classFactory(iface):
    """
    QGIS richiama questa funzione per istanziare il plugin.
    """
    from .hypsometric_curve import HypsometricCurve
    return HypsometricCurve(iface)