#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""--- main.py ---

Main GUI window.

@author   Hank Adler
@version  0.1.0
@license  MIT

--- Copyright (C) 2020 Hank Adler ---
"""


import sys

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMenu, QAction, QFileDialog, QStatusBar,
    QTabWidget)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot

from gui.widgets import Data, InputWidget, ScreenWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle('Stocks Daemon')
        self.setWindowIcon(QIcon('resources/ha.ico'))
        self.add_tabs()
        self.add_menubar()
        self.setStatusBar(QStatusBar(self))
        self.show()

    def add_menubar(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu('File')

        import_action = QAction('Import', self)
        import_action.triggered.connect(self.on_import)
        import_action.setStatusTip('Import input data')

        export_action = QAction('Export', self)
        export_action.triggered.connect(self.on_export)
        export_action.setStatusTip('Export input data')

        clear_action = QAction('Clear', self)
        clear_action.triggered.connect(self.input_widget.clear)
        clear_action.setStatusTip('Clear input data')

        file_menu.addAction(import_action)
        file_menu.addAction(export_action)
        file_menu.addAction(clear_action)

    def add_tabs(self):
        self.tabs = QTabWidget(self)
        self.setCentralWidget(self.tabs)
        self.input_widget = InputWidget()
        self.screen_widget = ScreenWidget()
        self.tabs.addTab(self.input_widget, 'Input')
        self.tabs.addTab(self.screen_widget, 'Screen')

    @pyqtSlot()
    def on_import(self):
        fname, _ = QFileDialog.getOpenFileName(
            self, 'Import input', '.', "JSON files (*.json)")
        if fname:
            self.input_widget.from_json(fname)

    @pyqtSlot()
    def on_export(self):
        fname, _ = QFileDialog.getSaveFileName(
            self, 'Export input', '.', "JSON files (*.json)")
        if fname:
            self.input_widget.to_json(fname)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
