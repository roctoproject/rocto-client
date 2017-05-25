# import sys
# import time
# from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import pyqtSignal, pyqtSlot

from ..client import client
from .mainwindow import *
from .gui_settings import *

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.InitUi()
        self.settings = QtCore.QSettings('ROctopus', 'ROctopus')

    def InitUi(self):
        self.ui.actionSettings.triggered.connect(self.InitSettings)
        self.ui.connect_button.clicked.connect(self.connect_to_server)
        self.ui.run_button.clicked.connect(self.start_thread)
        self.ui.quit_button.clicked.connect(QtCore.QCoreApplication.instance().quit)
        self.show()
        # QtCore.QCoreApplication.instance().quit()

    def InitSettings(self):
        self.dialog = SettingsDialog()
        if self.dialog.exec_(): # Modal window. Use .show() for modeless.
            values = self.dialog.getValues()
            print(values)
            for (key, value) in values.items():
                self.settings.setValue(key, value)
        # TODO: Check for errors.

    def get_file(self):
        fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '/home')
        # TODO: Find a way to write this to the line edit.

    def update_statusbar(self, text):
        self.statusBar().showMessage(text)

    def connect_to_server(self):
        # Gets task already at the moment.
        print(self.settings.value('server_ip', type=str))
        print(self.settings.value('port', type=int))
        self.task = client.Task(self.settings.value('server_ip', type=str), self.settings.value('port', type=int))
        self.ui.groupBox.setEnabled(True)

    def create_thread(self):
        self.workerthread = QtCore.QThread()
        self.workerthread.start()

    def start_thread(self):
        try:
            self.worker = threadWorker(self.task, self.settings.value('server_ip', type=str), self.settings.value('port', type=int))
            self.worker.start.connect(self.worker.run)
            self.worker.start.connect(self.update_statusbar)
            self.worker.finished.connect(self.update_statusbar)
            self.worker.sent.connect(self.update_statusbar)
            self.worker.moveToThread(self.workerthread)
            self.worker.start.emit('Task starts!')
        except AttributeError:
            self.create_thread()

            self.worker = threadWorker(self.task, self.settings.value('server_ip', type=str), self.settings.value('port', type=int))
            self.worker.start.connect(self.worker.run)
            self.worker.start.connect(self.update_statusbar)
            self.worker.finished.connect(self.update_statusbar)
            self.worker.sent.connect(self.update_statusbar)
            self.worker.moveToThread(self.workerthread)
            self.worker.start.emit('Task starts!')


    def process_thread(self):
        self.statusBar().showMessage('Task finished and output sent back!')

class threadWorker(QtCore.QObject):
    def __init__(self, task, ip, port):
        super().__init__()
        self.task = task
        self.ip = ip
        self.port = port

    start = pyqtSignal(str)
    finished = pyqtSignal(str)
    sent = pyqtSignal(str)
    @pyqtSlot()
    def run(self):
        print('Worker started!')
        self.task.run()
        self.finished.emit('Task finished!')
        self.task.send_results(self.ip, self.port)
        self.sent.emit('Task sent!')