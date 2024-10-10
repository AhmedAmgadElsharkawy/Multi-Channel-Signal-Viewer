from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QVBoxLayout, QFileDialog
import pyqtgraph as pg
from PyQt6.QtCore import Qt
import pandas as pd


class RectangleGraph(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        # self.setStyleSheet("background-color:red")

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
        rectangle_plot1_controls = QVBoxLayout()
        rectangle_plot1_controls.setAlignment(Qt.AlignmentFlag.AlignTop)

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
        rectangle_and_controls_container.addLayout(rectangle_plot1_controls)

        # Add the container to the main layout
        main_layout.addWidget(rectangle_signal_widget)
        self.setLayout(main_layout)

        # Connect insert button to file browser
        self.insert_button1.clicked.connect(self.browse_file)

    def load_and_plot_data(self, file_path):
        # Read CSV file
        data = pd.read_csv(file_path).iloc[:, 1]
        print(data)

        # # Clear any previous plots
        # self.rectangle_plot1.clear()

        # # Extract the data for plotting
        # x = data['Time [s]'].values  # Time values
        # y = data[' V'].values          # V values

        # # Plot the data
        # self.rectangle_plot1.plot(x, y)  # Blue line with circles

    def browse_file(self):
        # Open file dialog to select a CSV file
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)")

        if file_path:
            self.load_and_plot_data(file_path)
