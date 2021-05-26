# TODO: fix this mess

import sys
import time

import numpy
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import pandas as pd
from workers import TrainWorker, PlayWorker, UndergroundWorker
from agent import Agent
from game_grid import Grid
from pandasTableModel import TableModel
from plots import MplCanvas, NavigationToolbar, BarCanvas

label_style = "color: white;margin-left:5px;margin-right:5px;border-radius:10%;font-size:20px;" \
              "padding: 8px;margin-top:10px;font-family:Arial;background-color: rgb(76,175,80,0.5);"
button_active_style = "QPushButton{background-color: white;border: 1px solid #505050;padding: 15px 65px;" \
                      "margin-bottom:20px;border-radius:5%;}"
button_disabled_style = "QPushButton:disabled {border: 2px solid #f44336;background-color: #D0D0D0}"

progress_bar_style = "margin-left:5px;margin-right:5px;"


class SignalManager(QtCore.QObject):
    tableChanged = QtCore.pyqtSignal(object, QtCore.QVariant)
    tableFinished = QtCore.pyqtSignal(numpy.ndarray)


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.signal = SignalManager()
        self.gui_updated = pyqtSignal()
        self.agent = Agent(0.99)

        central_widget = QWidget()
        main_layout = QHBoxLayout()
        buttons_layout = QVBoxLayout()
        left_layout = QVBoxLayout()
        label_table_layout = QVBoxLayout()
        plots_layout = QGridLayout()
        self.label_grid = QGridLayout()

        self.init_buttons()
        # init and position labels
        self.set_labels()
        self.init_plots()

        self.label_grid.addWidget(self.step_label, 0, 0)
        self.label_grid.addWidget(self.action_label, 1, 1)
        self.label_grid.addWidget(self.state_action_label, 1, 0)
        self.label_grid.addWidget(self.life_label, 0, 1)

        # init and position game grid
        self.grid = Grid(grid=self.agent.getGame_repr(), state=self.agent.state)
        left_layout.addLayout(self.label_grid)
        left_layout.addWidget(self.grid, Qt.AlignJustify)

        buttons1_layout = QHBoxLayout()
        buttons2_layout = QHBoxLayout()

        buttons1_layout.addWidget(self.start_button, Qt.AlignJustify)
        buttons1_layout.addWidget(self.stop_button, Qt.AlignJustify)
        buttons2_layout.addWidget(self.play_button, Qt.AlignJustify)
        buttons2_layout.addWidget(self.restart_button, Qt.AlignJustify)
        buttons_layout.addLayout(buttons1_layout, Qt.AlignJustify)
        buttons_layout.addLayout(buttons2_layout, Qt.AlignJustify)
        buttons_layout.addWidget(self.train_background_button, Qt.AlignJustify)

        left_layout.addLayout(buttons_layout, Qt.AlignJustify)
        main_layout.addLayout(left_layout, Qt.AlignJustify)

        self.data = pd.DataFrame(self.agent.brain.qtable.copy(), columns=['LEFT', 'DOWN', 'RIGHT', 'UP'],
                                 index=[i for i in range(self.agent.env.observation_space.n)])
        self.table = QtWidgets.QTableView()
        self.model = TableModel(self.data)
        self.table.setModel(self.model)
        self.commentary_label = QLabel("New Training")
        self.commentary_label.setStyleSheet(label_style)
        label_table_layout.addWidget(self.commentary_label)
        self.progress = QProgressBar(self)
        self.progress.setStyleSheet(progress_bar_style)
        self.progress.setAlignment(Qt.AlignCenter)
        label_table_layout.addWidget(self.progress, Qt.AlignJustify)
        label_table_layout.addWidget(self.table, Qt.AlignJustify)
        label_table_layout.addWidget(self.commentary_label)

        main_layout.addLayout(label_table_layout, Qt.AlignJustify)
        self.table.setAlternatingRowColors(True)  # self.table.setMinimumWidth(300)
        self.table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # plot3_layout = QVBoxLayout()
        # toolbar2 = NavigationToolbar(sc2, self)
        # plot3_layout.addWidget(toolbar2)
        # plots_layout.addWidget(toolbar2, 0, 0)
        plots_layout.addWidget(self.sc2, 0, 1)

        # plot4_layout = QVBoxLayout()
        # toolbar4 = NavigationToolbar(self.sc4, self)
        # plot4_layout.addWidget(toolbar4)
        # plots_layout.addWidget(toolbar4, 0, 1)
        plots_layout.addWidget(self.sc4, 1, 1)

        self._plot_ref = None
        main_layout.addLayout(plots_layout, Qt.AlignJustify)
        central_widget.setLayout(main_layout)

        self.signal.tableChanged.connect(self.model.update_item)
        self.signal.tableFinished.connect(self.model.update_all)
        self.setCentralWidget(central_widget)
        self.show()

    def set_labels(self):
        self.step_label = QLabel()
        self.step_label.setStyleSheet(label_style)
        self.action_label = QLabel()
        self.action_label.setStyleSheet(label_style)
        self.life_label = QLabel()
        self.life_label.setStyleSheet(label_style)
        self.state_action_label = QLabel()
        self.state_action_label.setStyleSheet(label_style)
        self.init_stats_labels()

    def init_stats_labels(self):
        self.step_label.setText("steps: 0")
        self.action_label.setText("action: 0")
        self.life_label.setText("life: 1")
        self.state_action_label.setText("state: 0")

    def init_buttons(self):
        self.start_button = QPushButton("Train")
        self.start_button.setCursor(Qt.PointingHandCursor)
        self.start_button.setStyleSheet(button_active_style + button_disabled_style)
        self.start_button.clicked.connect(self.start_train)
        self.stop_button = QPushButton("Cancel")
        self.stop_button.setCursor(Qt.PointingHandCursor)
        self.stop_button.setStyleSheet(button_active_style)
        self.stop_button.clicked.connect(self.stop_train)
        self.train_background_button = QPushButton("Full Train in background")
        self.train_background_button.setCursor(Qt.PointingHandCursor)
        self.train_background_button.setStyleSheet(button_active_style + button_disabled_style)
        self.train_background_button.clicked.connect(self.train_in_background)
        self.restart_button = QPushButton("Restart")
        self.restart_button.setCursor(Qt.PointingHandCursor)
        self.restart_button.setStyleSheet(button_active_style + button_disabled_style)
        self.restart_button.clicked.connect(self.restart)
        self.play_button = QPushButton("Play")
        self.play_button.setCursor(Qt.PointingHandCursor)
        self.play_button.setStyleSheet(button_active_style + button_disabled_style)
        self.play_button.clicked.connect(self.play)

    def init_plots(self):
        self.sc2 = MplCanvas(self)
        self.sc2.axes.set_title("Exploration Rate")

        self.sc4 = BarCanvas(self)
        self.sc4.axes.set_title("Exploration History")
        self.names = ['gambled', 'predicted']
        self.values = [0, 0]
        self.sc4.axes.bar(self.names, self.values)

    def clear_plots(self):
        self.sc4.axes.cla()
        self.values = [0, 0]
        self.sc4.draw()
        self.sc2.axes.cla()
        self.sc2.draw()

    def play(self):
        self.worker = PlayWorker(self.agent)
        self.worker.signals.progress.connect(self.update_after_train)
        self.worker.signals.finished.connect(self.worker.quit)
        self.worker.start()
        self.start_button.setEnabled(False)
        self.train_background_button.setEnabled(False)
        self.restart_button.setEnabled(False)
        self.play_button.setEnabled(False)
        self.commentary_label.setText("Playing")

        # self.button.setStyleSheet(self.button_disabled_style)
        # QPushButton.
        # self.button.
        self.worker.signals.finished.connect(
            lambda: self.enable_buttons()
        )

    def restart(self):
        self.init_stats_labels()
        self.clear_plots()
        self.agent.restart()
        self.signal.tableFinished.emit(self.agent.brain.qtable.copy())

    def train_in_background(self):
        self.commentary_label.setText("Training...")
        self.worker = UndergroundWorker(self.agent)
        self.worker.signals.progress.connect(self.update_progress)
        self.worker.signals.finished.connect(self.worker.quit)
        self.worker.start()
        self.start_button.setEnabled(False)
        self.train_background_button.setEnabled(False)
        self.restart_button.setEnabled(False)
        self.play_button.setEnabled(False)

        # self.button.setStyleSheet(self.button_disabled_style)
        # QPushButton.
        # self.button.
        self.worker.signals.finished.connect(
            lambda: self.finish_train()
        )

    def stop_train(self):
        self.worker.kill()

    def start_train(self):
        self.worker = TrainWorker(self.agent)
        self.worker.signals.progress.connect(self.update_after_train)
        self.worker.signals.finished.connect(self.worker.quit)
        self.worker.start()
        self.start_button.setEnabled(False)
        self.train_background_button.setEnabled(False)
        self.restart_button.setEnabled(False)
        self.play_button.setEnabled(False)
        self.commentary_label.setText("Training")
        # self.button.setStyleSheet(self.button_disabled_style)
        # QPushButton.
        # self.button.
        self.worker.signals.finished.connect(
            lambda: self.enable_buttons()
        )

    def update_progress(self, progress):
        # print("getting and seting value: " + str(progress))
        self.progress.setValue(progress)
        self.progress.show()

    def enable_buttons(self):
        self.start_button.setEnabled(True)
        self.train_background_button.setEnabled(True)
        self.restart_button.setEnabled(True)
        self.play_button.setEnabled(True)
        self.commentary_label.setText("canceled")


    def finish_train(self):
        if self.worker.killi:
            self.commentary_label.setText("canceled")
        else:
            self.commentary_label.setText("Training complete")
        self.start_button.setEnabled(True)
        self.train_background_button.setEnabled(True)
        self.restart_button.setEnabled(True)
        self.play_button.setEnabled(True)

        self.life_label.setText("life: " + str(self.agent.lifes_spent + 1))

        self.sc4.axes.cla()
        self.sc4.axes.bar(self.names, self.agent.gamble_history)
        self.sc4.axes.set_title("Exploration History")
        self.sc4.draw()

        self.sc2.axes.cla()
        self.sc2.axes.plot([i for i in range(len(self.agent.exploration_rate_history))], self.agent.exploration_rate_history)
        self.sc2.axes.set_title("Exploration Rate")
        self.sc2.draw()
        # print(self.agent.brain.qtable)
        self.signal.tableFinished.emit(self.agent.brain.qtable.copy())

    def update_after_train(self, state, old_state, action, qtable, gambled, steps, lifes_spent, steps_life):
        # print("entering loop")
        self.step_label.setText("steps: " + str(steps))
        self.life_label.setText("life: " + str(lifes_spent + 1))
        self.action_label.setText("action: " + str(action))
        self.state_action_label.setText("state: " + str(state))
        # to change colors
        self.signal.tableChanged.emit(self.table.model().index(old_state, action),
                                      qtable)
        # self.table.model().setData(self.table.model().index(old_state, action),
        #                            qtable,
        #                            role=QtCore.Qt.EditRole)
        # print("bkack to main executing game grid change")
        self.grid.update_value(state)
        # print("bkack to main executing plot change")
        self.update_plot(gambled, steps_life)

    def update_plot(self, gambled, exploration_rate):
        self.sc4.axes.cla()

        if gambled:
            self.values[0] = self.values[0] + 1
        else:
            self.values[1] = self.values[1] + 1

        self.sc4.axes.bar(self.names, self.values)
        self.sc4.axes.set_title("Exploration History")
        self.sc4.draw()

        self.sc2.axes.cla()
        self.sc2.axes.plot([i for i in range(len(exploration_rate))], exploration_rate)
        self.sc2.axes.set_title("Exploration Rate")
        self.sc2.draw()


app = QApplication(sys.argv)
window = MainWindow()
window.show()

app.exec_()
