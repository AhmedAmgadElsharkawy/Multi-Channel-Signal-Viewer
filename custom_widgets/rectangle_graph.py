from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QVBoxLayout, QFileDialog,QScrollArea
import pyqtgraph as pg
from PyQt6.QtCore import Qt,QTimer
import pandas as pd
from custom_widgets.signal import Signal


class RectangleGraph(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        # self.setStyleSheet("background-color:red")
        self.signals = []
        self.xLimit = 0
        self.isRunning = True
        self.signalSpeed = 20
        self.timer = QTimer(self)
        self.curves = []
        self.colors = [
            (255, 0, 0),     # Red
            (0, 255, 0),     # Green
            (0, 0, 255),     # Blue
            (255, 255, 0),   # Yellow
            (255, 0, 255),   # Magenta
            (0, 255, 255),   # Cyan
            (128, 0, 128),   # Purple
            (255, 165, 0),   # Orange
            (0, 128, 128),   # Teal
            (128, 128, 0)    # Olive
        ]

    def initUI(self):
        main_layout = QVBoxLayout()

        rectangle_signal_widget = QWidget()
        rectangle_and_controls_container = QHBoxLayout()
        rectangle_signal_widget.setLayout(rectangle_and_controls_container)
        rectangle_signal_widget.setFixedHeight(210)

        # Create the plot widget
        self.rectangle_plot1 = pg.PlotWidget(name='Plot1')
        self.rectangle_plot1.setFixedSize(600, 200)

        # Create layout for controls and align to the top
        rectangle_signal_conntrols_widget = QWidget()
        rectangle_plot1_controls = QVBoxLayout()
        rectangle_signal_conntrols_widget.setLayout(rectangle_plot1_controls)
        rectangle_plot1_controls.setAlignment(Qt.AlignmentFlag.AlignTop)
        rectangle_signal_conntrols_widget.setFixedSize(100,200)
        self.rectangle_plot1.setLimits(xMin=0, xMax=1, yMin=-2, yMax=2)

        self.signals_list1 = QScrollArea()
        self.signals_list1.setFixedSize(150,200)
        

        # Create buttons
        self.insert_button1 = QPushButton("Insert")
        self.play_button1 = QPushButton("Play")
        self.pause_button1 = QPushButton("Pause")
        self.clear_button1 = QPushButton("Clear")
        self.speed_up_button1 = QPushButton("Speed Up")
        self.speed_down_button1 = QPushButton("Speed Down")

        # Add buttons to the layout
        rectangle_plot1_controls.addWidget(self.insert_button1)
        rectangle_plot1_controls.addWidget(self.play_button1)
        rectangle_plot1_controls.addWidget(self.pause_button1)
        rectangle_plot1_controls.addWidget(self.clear_button1)
        rectangle_plot1_controls.addWidget(self.speed_up_button1)
        rectangle_plot1_controls.addWidget(self.speed_down_button1)


        # Add plot and controls to the container
        rectangle_and_controls_container.addWidget(self.rectangle_plot1)
        rectangle_and_controls_container.addWidget(rectangle_signal_conntrols_widget)
        rectangle_and_controls_container.addWidget(self.signals_list1)


        # Add the container to the main layout
        main_layout.addWidget(rectangle_signal_widget)
        self.setLayout(main_layout)

        # Connect insert button to file browser
        self.insert_button1.clicked.connect(self.browse_file)
        self.pause_button1.clicked.connect(self.pauseSignals)
        self.play_button1.clicked.connect(self.playSignals)
        self.speed_up_button1.clicked.connect(self.increaseSpeed)
        self.speed_down_button1.clicked.connect(self.decreaseSpeed)

    def add_signal(self, file_path):
        # Read CSV file
        if not file_path:
            pass

        signal  = Signal(file_path,len(self.signals))
        if len(signal.x) > self.xLimit:
            self.xLimit = len(signal.x)
        self.signals.append(signal)
        self.isRunning = True
        self.timer.stop()
        self.signalSpeed = 20
        
        self.ptr = 0

        # self.rectangle_plot1.clear() 

        curve = self.rectangle_plot1.plot(pen=pg.mkPen(color=self.colors[len(self.curves)%len(self.colors)]))
        self.curves.append(curve)
        self.rectangle_plot1.setLabel('bottom', 'Time', 's')
        self.rectangle_plot1.setXRange(0, 1)  # Initial range
        self.rectangle_plot1.setYRange(-0.7, 0.7)

        # Set up the QTimer
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(20)  # 50 milliseconds
        

    def update_plot(self):
        if self.ptr < self.xLimit and self.isRunning:
            for i, signal in enumerate(self.signals):
                if len(signal.x) >= self.ptr:
                    self.curves[i].setData(signal.x[:self.ptr], signal.y[:self.ptr])  # Update each curve
                    if self.ptr / 1000 > 1:
                        self.rectangle_plot1.setLimits(xMin=0, xMax=((self.ptr / 1000)), yMin=-2, yMax=2)
            self.ptr += 1
            if self.ptr > 1000:
                self.rectangle_plot1.setXRange((self.ptr / 1000) - 1, self.ptr / 1000)

    def browse_file(self):
        # Open file dialog to select a CSV file
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)")

        if file_path:
            self.add_signal(file_path)

    def plot(self):
        for signal in self.signals:
            self.rectangle_plot1.plot(signal.y)

    def pauseSignals(self):
        self.isRunning = False

    def playSignals(self):
        self.isRunning = True

    def increaseSpeed(self):
        self.timer.stop()
        if (self.signalSpeed > 5):
            self.signalSpeed = int(self.signalSpeed / 2)
            print(self.signalSpeed)
        elif (self.signalSpeed == 5):
            self.signalSpeed = int(self.signalSpeed / 5)
            print(self.signalSpeed)
        self.timer.start(self.signalSpeed)

    def decreaseSpeed(self):
        self.timer.stop()
        if (self.signalSpeed == 1):
            self.signalSpeed = int(self.signalSpeed * 5)
            print(self.signalSpeed)
        elif (self.signalSpeed < 40):
            self.signalSpeed = int(self.signalSpeed * 2)
            print(self.signalSpeed)
        self.timer.start(self.signalSpeed)

