#!/usr/bin/python3
import sys

from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox

class MainWindow(QMainWindow):
    def __init__(self, reactor):
        super().__init__()
        self.reactor = reactor
        self.init_ui()
        
    def init_ui(self):               
        self.statusBar().showMessage('Ready')
        self.setGeometry(300, 300, 600, 450)
        self.setWindowTitle('CPChain Wallet')    
        self.show()

    def closeEvent(self, event):
        self.reactor.stop()


def _handle_keyboard_interrupt():
    def sigint_handler(*args):
        # if QMessageBox.question(None, '', "Are you sure you want to quit?",
        #                         QMessageBox.Yes | QMessageBox.No,
        #                         QMessageBox.No) == QMessageBox.Yes:
        #     QApplication.quit()
        QApplication.quit()


    import signal
    signal.signal(signal.SIGINT, sigint_handler)

    # cf. https://stackoverflow.com/a/4939113/855160
    from PyQt5.QtCore import QTimer

    # make it global, o.w. the timer will soon vanish.
    _handle_keyboard_interrupt.timer = QTimer()
    timer = _handle_keyboard_interrupt.timer
    timer.start(300) # run each 300ms
    timer.timeout.connect(lambda: None)


def main():
    app = QApplication(sys.argv)

    import qt5reactor
    qt5reactor.install()
    from twisted.internet import reactor

    main_wnd = MainWindow(reactor)

    _handle_keyboard_interrupt()
    sys.exit(reactor.run())


if __name__ == '__main__':
    main()
