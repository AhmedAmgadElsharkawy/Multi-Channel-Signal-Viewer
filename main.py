import sys
from PyQt6.QtWidgets import QApplication,QMainWindow,QVBoxLayout,QHBoxLayout,QGridLayout,QWidget,QLabel, QPushButton, QCheckBox, QMessageBox

from custom_widgets.example import Example
from custom_widgets.rectangle_graph import RectangleGraph

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.isSyncingX = False
        self.setWindowTitle("Multi-Channel-Signal-Viewer")
        self.resize(800, 600)
        self.initUI()

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()

        # Here’s an example showing how to use custom widgets; feel free to uncomment it.
        # example = Example()
        # main_layout.addWidget(example)

        # add your custom widgets below
        self.rectangle_plot1 = RectangleGraph()
        self.link_h_box = QHBoxLayout()
        self.link_options = QHBoxLayout()
        self.link_button = QCheckBox("Link graphs", self) 
        self.rectangle_plot2 = RectangleGraph()
        self.link_h_box.addWidget(self.link_button)
        self.link_h_box.addLayout(self.link_options)
        main_layout.addWidget(self.rectangle_plot1)
        main_layout.addLayout(self.link_h_box)
        main_layout.addWidget(self.rectangle_plot2)
        

        # set main layout of central widget
        self.link_button.stateChanged.connect(self.link_button_changed)
        central_widget.setLayout(main_layout)


    def link_button_changed(self):
        sender = self.sender()
        if sender.isChecked():
            if len(self.rectangle_plot1.signals) == 0 or len(self.rectangle_plot2.signals) == 0:
                QMessageBox.warning(self,"Operation Failed","You can't link the two graphs if one of them is empty")
                sender.setChecked(False)
                return
            self.rectangle_plot1.insert_button1.setEnabled(False)
            self.rectangle_plot1.play_button1.setEnabled(False)
            self.rectangle_plot1.pause_button1.setEnabled(False) 
            self.rectangle_plot1.clear_button1.setEnabled(False) 
            self.rectangle_plot1.rewind_button1.setEnabled(False)
            self.rectangle_plot1.speed_up_button1.setEnabled(False)
            self.rectangle_plot1.speed_down_button1.setEnabled(False)
            self.rectangle_plot2.insert_button1.setEnabled(False)
            self.rectangle_plot2.play_button1.setEnabled(False)
            self.rectangle_plot2.pause_button1.setEnabled(False) 
            self.rectangle_plot2.clear_button1.setEnabled(False) 
            self.rectangle_plot2.rewind_button1.setEnabled(False)
            self.rectangle_plot2.speed_up_button1.setEnabled(False)
            self.rectangle_plot2.speed_down_button1.setEnabled(False)
            self.pause_link = QPushButton("Pause", self)
            self.play_link = QPushButton("Play", self)
            self.speed_up_link = QPushButton("Speed up", self)
            self.speed_down_link = QPushButton("Speed down", self)
            self.rewind_link = QPushButton("Rewind", self)
            self.link_options.addWidget(self.pause_link)
            self.link_options.addWidget(self.play_link)
            self.link_options.addWidget(self.rewind_link)
            self.link_options.addWidget(self.speed_up_link)
            self.link_options.addWidget(self.speed_down_link)
            self.pause_link.clicked.connect(self.pasue_linked_signals)
            self.play_link.clicked.connect(self.play_linked_signals)
            self.speed_up_link.clicked.connect(self.speed_up_linked_signals)
            self.speed_down_link.clicked.connect(self.speed_down_linked_signals)
            self.rewind_link.clicked.connect(self.rewind_linked_signals)
            self.rectangle_plot1.rewindSignals()
            self.rectangle_plot2.rewindSignals()
            self.rectangle_plot1.rectangle_plot.getViewBox().sigXRangeChanged.connect(self.synchronizePosGraph1)
            self.rectangle_plot2.rectangle_plot.getViewBox().sigXRangeChanged.connect(self.synchronizePosGraph2)
            self.rectangle_plot1.rectangle_plot.getViewBox().sigYRangeChanged.connect(self.synchronizePosGraph1)
            self.rectangle_plot2.rectangle_plot.getViewBox().sigYRangeChanged.connect(self.synchronizePosGraph2)
        else:
            self.rectangle_plot1.insert_button1.setEnabled(True)
            self.rectangle_plot1.play_button1.setEnabled(True)
            self.rectangle_plot1.pause_button1.setEnabled(True) 
            self.rectangle_plot1.clear_button1.setEnabled(True) 
            self.rectangle_plot1.rewind_button1.setEnabled(True)
            self.rectangle_plot1.speed_up_button1.setEnabled(True)
            self.rectangle_plot1.speed_down_button1.setEnabled(True)
            self.rectangle_plot2.insert_button1.setEnabled(True)
            self.rectangle_plot2.play_button1.setEnabled(True)
            self.rectangle_plot2.pause_button1.setEnabled(True) 
            self.rectangle_plot2.clear_button1.setEnabled(True) 
            self.rectangle_plot2.rewind_button1.setEnabled(True)
            self.rectangle_plot2.speed_up_button1.setEnabled(True)
            self.rectangle_plot2.speed_down_button1.setEnabled(True)
            self.remove_option_widgets()

    def pasue_linked_signals(self):
        self.rectangle_plot1.pauseSignals()
        self.rectangle_plot2.pauseSignals()
    
    def play_linked_signals(self):
        self.rectangle_plot1.playSignals()
        self.rectangle_plot2.playSignals()

    def speed_up_linked_signals(self):
        self.rectangle_plot1.increaseSpeed()
        self.rectangle_plot2.increaseSpeed()


    def speed_down_linked_signals(self):
        self.rectangle_plot1.decreaseSpeed()
        self.rectangle_plot2.decreaseSpeed()

    def rewind_linked_signals(self):
        self.rectangle_plot1.rewindSignals()
        self.rectangle_plot2.rewindSignals()

    def remove_option_widgets(self):
        while self.link_options.count():
            item = self.link_options.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def synchronizePosGraph1(self):
        if not self.isSyncingX and not self.rectangle_plot1.isRunning:
            self.rectangle_plot2.rectangle_plot.getViewBox().sigXRangeChanged.disconnect(self.synchronizePosGraph2)
            self.rectangle_plot2.rectangle_plot.getViewBox().sigYRangeChanged.disconnect(self.synchronizePosGraph2)
                
            # Set the X-axis range of graph2 based on graph1
            xRange = self.rectangle_plot1.rectangle_plot.getViewBox().viewRange()[0]
            yRange = self.rectangle_plot1.rectangle_plot.getViewBox().viewRange()[1]
            self.isSyncingX = True
            self.rectangle_plot2.rectangle_plot.getViewBox().setXRange(*xRange)
            self.rectangle_plot2.rectangle_plot.getViewBox().setYRange(*yRange)
            self.isSyncingX = False
            
            # Reconnect the signal
            self.rectangle_plot2.rectangle_plot.getViewBox().sigXRangeChanged.connect(self.synchronizePosGraph2)
            self.rectangle_plot2.rectangle_plot.getViewBox().sigYRangeChanged.connect(self.synchronizePosGraph2)

    def synchronizePosGraph2(self):
        if not self.isSyncingX and not self.rectangle_plot2.isRunning:
            self.rectangle_plot1.rectangle_plot.getViewBox().sigXRangeChanged.disconnect(self.synchronizePosGraph1)
            self.rectangle_plot1.rectangle_plot.getViewBox().sigYRangeChanged.disconnect(self.synchronizePosGraph1)
                
            # Set the X-axis range of graph2 based on graph1
            xRange = self.rectangle_plot2.rectangle_plot.getViewBox().viewRange()[0]
            yRange = self.rectangle_plot2.rectangle_plot.getViewBox().viewRange()[1]
            self.isSyncingX = True
            self.rectangle_plot1.rectangle_plot.getViewBox().setXRange(*xRange)
            self.rectangle_plot1.rectangle_plot.getViewBox().setYRange(*yRange)
            self.isSyncingX = False
            
            # Reconnect the signal
            self.rectangle_plot1.rectangle_plot.getViewBox().sigXRangeChanged.connect(self.synchronizePosGraph1)
            self.rectangle_plot1.rectangle_plot.getViewBox().sigYRangeChanged.connect(self.synchronizePosGraph1)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()