# -*- coding: utf-8 -*-
"""
# Ibiraté - APP Analises | https://www.ibirate.com.br/
(C) 2026 by Poliana Cursino Betella | Pedro Cursino Betella Gomes
betella.poliana@gmail.com | pedro.cursino.gomes@gmail.com
"""

import os
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from .dock import AppComplianceDock

class AppCompliance:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.dock = None

    def initGui(self):
        icon_path = os.path.join(self.plugin_dir, 'icon.png')
        self.action = QAction(QIcon(icon_path), "Ibiraté - APP Analises", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToVectorMenu("Ibiraté", self.action)

    def unload(self):
        self.iface.removePluginVectorMenu("Ibiraté", self.action)
        self.iface.removeToolBarIcon(self.action)

    def run(self):
        if not self.dock:
            self.dock = AppComplianceDock(self.iface)
            self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dock)
        self.dock.show()