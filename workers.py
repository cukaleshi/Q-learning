import time

from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot


class WorkerSignals(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int, int, int, float, bool, int, int, list)


class TrainWorker(QThread):

    def __init__(self, agent):
        super(TrainWorker, self).__init__()
        self.agent = agent
        self.signals = WorkerSignals()
        self.waiting = False
        self.killi = False

    @pyqtSlot(int, int, int, float, bool, int, int, list)
    def run(self):
        self.killi = False
        """Long-running task."""
        for i in range(100):
            # print("i = " + str(i))
            if self.killi:
                break

                # print("starting train in thread")
            self.agent.train_once()
            # print("emiting change")
            self.signals.progress.emit(self.agent.state, self.agent.old_state, self.agent.action,
                                       self.agent.brain.qtable[self.agent.old_state, self.agent.action],
                                       self.agent.gambled, self.agent.steps, self.agent.lifes_spent,
                                       self.agent.exploration_rate_history)
            # print("self steps = " + str(self.agent.steps))

            # self.sleep(1)
            # print("thread sleep")
            time.sleep(1)

        self.signals.finished.emit()

    # def unlock(self):
    # pass

    def kill(self):
        self.killi = True


class PlayWorker(QThread):

    def __init__(self, agent):
        super(PlayWorker, self).__init__()
        self.agent = agent
        self.signals = WorkerSignals()
        self.waiting = False
        self.killi = False

    @pyqtSlot(int, int, int, float, bool, int, int, list)
    def run(self):
        self.killi = False
        """Long-running task."""
        while not self.agent.dead:
            # print("i = " + str(i))
            if self.killi:
                break

            self.agent.play()
            self.signals.progress.emit(self.agent.state, self.agent.old_state, self.agent.action,
                                       self.agent.brain.qtable[self.agent.old_state, self.agent.action],
                                       self.agent.gambled, self.agent.steps, self.agent.lifes_spent,
                                       self.agent.exploration_rate_history)
            # self.sleep(1)
            # print("thread sleep")
            time.sleep(0.3)
        self.agent.reset()
        self.signals.finished.emit()

    # def unlock(self):
    # pass

    def kill(self):
        self.killi = True


class UndergroundWorkerSignals(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)


class UndergroundWorker(QThread):

    def __init__(self, agent):
        super(UndergroundWorker, self).__init__()
        self.agent = agent
        self.signals = UndergroundWorkerSignals()
        self.waiting = False
        self.killi = False

    def run(self):
        self.killi = False
        """Long-running task."""
        for i in range(20000):
            # print("life nr: " + str(i))
            if self.killi:
                break
            while not self.agent.dead:
                # print("i = " + str(i))

                self.agent.train_once()
            if (i + 1) % 200 == 0:
                # print("emiting values")
                self.signals.progress.emit(((i + 1) / 20000) * 100)
                time.sleep(0.5)
            # print("thread sleep")
            self.agent.reset()
        self.signals.finished.emit()

    # def unlock(self):
    # pass

    def kill(self):
        self.killi = True
