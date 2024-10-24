import sys
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QFileDialog, QPushButton
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.animation import FuncAnimation

class radar_graph(QMainWindow):
    def __init__(self, sweep_window=30):
        super().__init__()

        self.setWindowTitle("Radar-style Polar Coordinates Graph with Sweep Effect")
        self.setGeometry(100, 100, 800, 600)

        radar_widget = QWidget()
        radar_widget.setStyleSheet("background-color: #201c1c")
        radar_layout = QVBoxLayout(radar_widget)

        self.fig, self.ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize=(8, 6))

        self.fig.patch.set_facecolor('#201c1c')
        self.ax.set_facecolor('black')

        self.ax.set_xticklabels([])
        self.ax.set_yticklabels([])

        self.ax.spines['polar'].set_visible(False)

        self.line, = self.ax.plot([], [], 'r-', linewidth=2)

        self.fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

        self.canvas = FigureCanvas(self.fig)
        radar_layout.addWidget(self.canvas)
        self.setCentralWidget(radar_widget)
        
        self.is_paused = False
        self.current_frame = 0

        self.sweep_window = sweep_window

    def read_csv(self, file_path):
        self.data = pd.read_csv(file_path)

        time = self.data['Elapsed time']
        self.radius = self.data['ii']

        max_time = max(time)
        self.theta = time * (2 * np.pi / max_time)

        if hasattr(self, 'anim'):
            self.anim.event_source.stop()
        self.start_animation()

        if len(self.theta) == 0 or len(self.radius) == 0:
            print("Error: Data length is zero. Animation cannot proceed.")
            return

        self.ax.set_ylim(min(self.radius), max(self.radius))

    def start_animation(self, from_frame=0):
        if len(self.theta) > 0 and len(self.radius) > 0:
            self.anim = FuncAnimation(self.fig, self.update_plot, frames=np.arange(from_frame, len(self.theta)),
                                      interval=50, repeat=False)
            self.canvas.draw()
        else:
            print("Error: Cannot start animation due to insufficient data.")

    def update_plot(self, frame):
        if self.is_paused:
            return
        if frame < len(self.theta):
            self.current_frame = frame
            self.line.set_data(self.theta[:frame], self.radius[:frame])
        return self.line,

    def pause_radar(self):
            if hasattr(self, 'anim'):
                self.anim.event_source.stop()  
            self.is_paused = True

    def play_radar(self):
        if not self.is_paused:
            return
        self.is_paused = False
        print(self.current_frame)
        self.start_animation(self.current_frame)

    def clear_radar(self):
        self.is_paused = True
        self.current_frame = 0
        self.anim.event_source.stop()

        self.line.set_data([], [])
        
        self.ax.cla()
        self.ax.set_facecolor('black')
        self.ax.set_xticklabels([])
        self.ax.set_yticklabels([])
        self.ax.spines['polar'].set_visible(False)
        
        self.canvas.draw()