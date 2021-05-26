import math

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class Grid(QWidget):
    def __init__(self, *args, grid, state, **kwargs):
        super().__init__(*args, **kwargs)
        self.game_array = grid
        self.grid_size = len(self.game_array)
        self.agent_row = math.floor(state / self.grid_size)
        self.agent_column = state % self.grid_size

    def resizeEvent(self, event):
        # compute the square size based on the aspect ratio, assuming that the
        # column and row numbers are fixed
        reference = self.width() * self.grid_size / self.grid_size
        if reference > self.height():
            # the window is larger than the aspect ratio
            # use the height as a reference (minus 1 pixel)
            self.squareSize = (self.height() - 1) / self.grid_size
        else:
            # the opposite
            self.squareSize = (self.width() - 1) / self.grid_size

    # ToDo Remove Logic from paintEvent
    def paintEvent(self, event):
        qp = QPainter(self)
        # translate the painter by half a pixel to ensure correct line painting
        qp.translate(.5, .5)
        qp.setRenderHints(qp.Antialiasing)

        width = self.squareSize * self.grid_size
        height = self.squareSize * self.grid_size
        # center the grid
        left = (self.width() - width) / 2
        top = (self.height() - height) / 2

        y = top
        for row in range(self.grid_size + 1):
            if row == 0 or row == self.grid_size:
                qp.drawLine(int(left), int(y), int(left + width), int(y))
            y += self.squareSize
        x = left
        for column in range(self.grid_size + 1):
            if column == 0 or column == self.grid_size:
                qp.drawLine(int(x), int(top), int(x), int(top + height))
            x += self.squareSize

        # create a smaller rectangle
        objectSize = self.squareSize * .8
        margin = self.squareSize * .1
        objectRect = QRectF(margin, margin, objectSize, objectSize)  # init with margin as position
        for col in range(self.grid_size):
            for row in range(self.grid_size):
                if self.game_array[row][col] == "F" or self.game_array[row][col] == "S":
                    qp.fillRect(objectRect.translated(
                        left + col * self.squareSize, top + row * self.squareSize), QColor('#b9e8ea'))
                elif self.game_array[row][col] == "H":
                    black = QColor('#5d5955')
                    black.setAlphaF(0.4)
                    qp.fillRect(objectRect.translated(
                        left + col * self.squareSize, top + row * self.squareSize), black)
                elif self.game_array[row][col] == "G":
                    green = QColor('#7CFC00')
                    green.setAlphaF(0.2)
                    qp.fillRect(objectRect.translated(
                        left + col * self.squareSize, top + row * self.squareSize), green)

                f = qp.font()
                qp.setFont(f)
                qp.drawText(objectRect.translated(
                    left + col * self.squareSize, top + row * self.squareSize), Qt.AlignCenter,
                    str(self.game_array[row][col]))
                if col == self.agent_column and row == self.agent_row:
                    red = QColor('red')
                    red.setAlphaF(0.4)
                    qp.fillRect(objectRect.translated(
                        left + col * self.squareSize, top + row * self.squareSize), red)

    def update_value(self, state):
        self.agent_row = math.floor(state / self.grid_size)
        self.agent_column = state % self.grid_size
        self.update()
