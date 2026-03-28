# -*- coding: utf-8 -*-

def classFactory(iface):
    """
    QGIS richiama questa funzione per istanziare il plugin.
    """
    from .hypsometric_curve import HypsometricCurve
    return HypsometricCurve(iface)