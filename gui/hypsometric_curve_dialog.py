# -*- coding: utf-8 -*-
"""
HypsometricCurveDialog – Qt6 version
Loads the .ui file and exposes the dialog widgets.
"""

import os
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog


FORM_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "hypsometric_curve_dialog_base.ui")
)


class HypsometricCurveDialog(QDialog, FORM_CLASS):
    """
    Main dialog for the Hypsometric Curve plugin.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # The dialog is intentionally minimal.
        # All logic is handled by hypsometric_curve.py and core/ modules.
