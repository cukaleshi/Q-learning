import time

import numpy
import pandas as pd
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class TableModel(QtCore.QAbstractTableModel):

    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data
        self.color_enabled = False
        self.color_back = QColor('Light green')  # just something there
        self.color_back.setAlphaF(0.5)
        self.blink_index = []
        # self.table.model().change_color(Qt.red, True)
        #

    def data(self, index, role):
        #print(index.row(), index.column(), role)
        if role == Qt.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            value = "%.7f" % value
            # print("setting values")
            return str(value)
        if role == Qt.BackgroundRole and self.blink_index == index:
            # print("coloring")
            return QBrush(self.color_back)

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        # print("entering setdata")
        if role == QtCore.Qt.EditRole:
            self._data.iloc[index.row(), index.column()] = value
            # print("entering blink")
            if self.blink_index != []:
                self.change_blink_index()
            # print("back from blink")
            self.blink_index = index
            self.dataChanged.emit(index, index)
            # print("table loop finished")

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return self._data.shape[1]

    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])

            if orientation == Qt.Vertical:
                return str(self._data.index[section])

    def change_blink_index(self):
        # print("changing blink")
        self.dataChanged.emit(self.blink_index,
                              self.blink_index)  # happens after instructions from the main thread finish

    @pyqtSlot(object, QtCore.QVariant)
    def update_item(self, index, value):
        # print("entering table")
        self.setData(index, value)

    @pyqtSlot(numpy.ndarray)
    def update_all(self, new_table):
        for i in range(16):
            for j in range(4):
                self.setData(self.index(i, j), new_table[i, j])
