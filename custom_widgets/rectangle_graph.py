from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QVBoxLayout, QFileDialog,QScrollArea
import pyqtgraph as pg
from PyQt6.QtCore import Qt
import pandas as pd
from custom_widgets.signal import Signal


class RectangleGraph(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        # self.setStyleSheet("background-color:red")
        self.signals = []
        self.xLimit = 4

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

        self.signals_list1 = QScrollArea()
        self.signals_list1.setFixedSize(150,200)
        

        # Create buttons
        self.insert_button1 = QPushButton("Insert")
        self.play_button1 = QPushButton("Play")
        self.stop_button1 = QPushButton("Stop")

        # Add buttons to the layout
        rectangle_plot1_controls.addWidget(self.insert_button1)
        rectangle_plot1_controls.addWidget(self.play_button1)
        rectangle_plot1_controls.addWidget(self.stop_button1)

        # Add plot and controls to the container
        rectangle_and_controls_container.addWidget(self.rectangle_plot1)
        rectangle_and_controls_container.addWidget(rectangle_signal_conntrols_widget)
        rectangle_and_controls_container.addWidget(self.signals_list1)


        # Add the container to the main layout
        main_layout.addWidget(rectangle_signal_widget)
        self.setLayout(main_layout)

        # Connect insert button to file browser
        self.insert_button1.clicked.connect(self.browse_file)

    def add_signal(self, file_path):
        # Read CSV file
        if not file_path:
            pass

        signal  = Signal(file_path,len(self.signals))
        if signal.MaxX > self.xLimit:
            self.xLimit = signal.MaxX
        self.signals.append(signal)
        print(self.signals)
        self.plot()
        

    def browse_file(self):
        # Open file dialog to select a CSV file
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)")

        if file_path:
            self.add_signal(file_path)

    def plot(self):
        for signal in self.signals:
            self.rectangle_plot1.plot(signal.y)

