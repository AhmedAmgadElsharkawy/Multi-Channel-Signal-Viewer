import sys
import requests
import json
import numpy as np
from PyQt6 import QtWidgets, QtCore
import pyqtgraph as pg

def fetch_live_signal():
    url = "https://quantifycrypto.com/api/v1/general/currencies"
    headers = {
        'QC-Access-Key': 'DWD5OZ2AT831T18DHXOM',
        'QC-Secret-Key': 'aXhLbgAROtwAXZZ9UyUFNaKHDGVcClR2YNCDwa9rE0YiDCmv',
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        values = [float(currency['conv_rate']) for currency in data['data']] 
        return values
    else:
        print("Error fetching data:", response.status_code, response.text)
        return np.random.normal(size=100)  

class SignalViewerApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Raafat's Non-Rectangle Signal Viewer")
        self.setGeometry(100, 100, 1200, 500)  # Updated layout size
        
        self.is_paused = False
        self.is_rewind = False
        self.signal_color = 'g'  # the Default color i used (there are other 4 colors)
        self.signal_label = "Live Signal"
        self.show_signal = True
        
        self.timer = QtCore.QTimer(self) ######################################################
        self.timer.timeout.connect(self.update_signal)
        
        self.init_ui()
        
        self.signal_data = fetch_live_signal()
        self.index = 0
        self.update_signal()
        self.timer.start(200)  # Set the update rate (u can use higher number for slower update)
        
    def init_ui(self):
        # our Main layout
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        layout = QtWidgets.QHBoxLayout(central_widget) # choosing a horizontal layout
        
        # Create PyQtGraph plot for signal visualization
        self.plot_widget = pg.PlotWidget()
        layout.addWidget(self.plot_widget, stretch=10) # giving the plot a 10 in terms of space space (we are giving the control layout 1 so its smaller)

        # Customize non-rectangle graph
        self.plot_widget.setBackground('k') # setting the color of the background of the graph
        self.plot_widget.setTitle("Crypto Signal", color='w', size='15pt')
        self.plot_widget.setLabel('left', 'Price')
        self.plot_widget.setLabel('bottom', 'Time')
        self.plot_widget.addLegend()
        
        # Generate a custom non-rectangle path (e.g., sinusoidal path) ##############################################3
        self.curve = self.plot_widget.plot(pen=pg.mkPen(self.signal_color, width=5), name=self.signal_label)
        
        # Create a small section for control buttons on the right
        control_layout = QtWidgets.QVBoxLayout()
        control_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        
        # Play, Pause, Rewind buttons
        play_button = QtWidgets.QPushButton("Play")
        play_button.clicked.connect(self.play_signal) # chosing the event that happens when clicking the play button
        pause_button = QtWidgets.QPushButton("Pause")
        pause_button.clicked.connect(self.pause_signal)
        rewind_button = QtWidgets.QPushButton("Rewind")
        rewind_button.clicked.connect(self.rewind_signal)
        
        control_layout.addWidget(play_button) # adding the widget to our program
        control_layout.addWidget(pause_button)
        control_layout.addWidget(rewind_button)

        # Color, Label, Toggle visibility controls
        color_button = QtWidgets.QPushButton("Change Color")
        color_button.clicked.connect(self.change_color)
        control_layout.addWidget(color_button)

        label_input = QtWidgets.QLineEdit()
        label_input.setPlaceholderText("Enter label")
        control_layout.addWidget(label_input)
        label_button = QtWidgets.QPushButton("Add Label")
        label_button.clicked.connect(lambda: self.add_label(label_input.text()))
        control_layout.addWidget(label_button)

        toggle_signal_button = QtWidgets.QPushButton("Toggle Signal")
        toggle_signal_button.clicked.connect(self.toggle_signal)
        control_layout.addWidget(toggle_signal_button)

        # Zoom controls
        zoom_in_button = QtWidgets.QPushButton("Zoom In")
        zoom_in_button.clicked.connect(self.zoom_in)
        control_layout.addWidget(zoom_in_button)

        zoom_out_button = QtWidgets.QPushButton("Zoom Out")
        zoom_out_button.clicked.connect(self.zoom_out)
        control_layout.addWidget(zoom_out_button)

        # Add control layout to the right side ( i gave it 1 to be smaller on the right)
        layout.addLayout(control_layout, stretch=1)

    def update_signal(self): ##################################################3
        if not self.is_paused:
            if self.is_rewind:
                self.index = max(0, self.index - 1)
            else:
                self.index = (self.index + 1) % len(self.signal_data) #ensures that when self.index reaches the end of the signal data, it loops back to the beginning.
            
            # Simulate the cine mode by showing a slice of data
            start_idx = max(0, self.index - 100)
            end_idx = self.index
            self.curve.setData(self.signal_data[start_idx:end_idx])
    
    def play_signal(self):
        self.is_paused = False
        self.is_rewind = False
    
    def pause_signal(self):
        self.is_paused = True
    
    def rewind_signal(self):
        self.is_rewind = True

    def change_color(self):
        # Switch between different colors for the signal
        color_list = ['g', 'r', 'b', 'y']
        current_index = color_list.index(self.signal_color)
        self.signal_color = color_list[(current_index + 1) % len(color_list)]
        self.curve.setPen(pg.mkPen(self.signal_color, width=5))
        self.plot_widget.update()

    def add_label(self, label):
        if label:
            self.signal_label = label
            self.plot_widget.setTitle(label, color='w', size='15pt')

    def toggle_signal(self):
        if self.show_signal:
            self.curve.hide()
        else:
            self.curve.show()
        self.show_signal = not self.show_signal

    def zoom_in(self):
    # Get current view range for both axes
        x_min, x_max = self.plot_widget.viewRange()[0]
        y_min, y_max = self.plot_widget.viewRange()[1]
        
        # Calculate current range and center
        x_range = x_max - x_min
        y_range = y_max - y_min
        x_center = (x_max + x_min) / 2
        y_center = (y_max + y_min) / 2
        
        # Set new zoomed range with a scale factor
        scale_factor = 0.9  # You can adjust the zoom factor if necessary
        self.plot_widget.setXRange(x_center - x_range * scale_factor / 2, x_center + x_range * scale_factor / 2)
        self.plot_widget.setYRange(y_center - y_range * scale_factor / 2, y_center + y_range * scale_factor / 2)

    def zoom_out(self):
        # Get current view range for both axes
        x_min, x_max = self.plot_widget.viewRange()[0]
        y_min, y_max = self.plot_widget.viewRange()[1]
        
        # Calculate current range and center
        x_range = x_max - x_min
        y_range = y_max - y_min
        x_center = (x_max + x_min) / 2
        y_center = (y_max + y_min) / 2
        
        # Set new zoomed-out range with a scale factor
        scale_factor = 1.1  # You can adjust the zoom factor if necessary
        self.plot_widget.setXRange(x_center - x_range * scale_factor / 2, x_center + x_range * scale_factor / 2)
        self.plot_widget.setYRange(y_center - y_range * scale_factor / 2, y_center + y_range * scale_factor / 2)



def main():
    app = QtWidgets.QApplication(sys.argv)
    viewer = SignalViewerApp()
    viewer.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
