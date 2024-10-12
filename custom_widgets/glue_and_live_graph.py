from PyQt6.QtWidgets import QWidget,QHBoxLayout,QVBoxLayout,QPushButton
import pyqtgraph as pg
from scipy.interpolate import interp1d


class GlueAndLiveGraph(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        main_layout = QHBoxLayout()

        self.glue_plot = pg.PlotWidget()
        main_layout.addWidget(self.glue_plot)
        self.setFixedHeight(240)

        self.controls_widget = QWidget()
        self.controls_widget_layout = QVBoxLayout()
        self.controls_widget.setLayout(self.controls_widget_layout)
        main_layout.addWidget(self.controls_widget)


        self.choose_signals_buttons_layout = QVBoxLayout()
        self.live_signal_button = QPushButton("Live")
        self.choose_signals_buttons_layout.addWidget(self.live_signal_button)
        self.controls_widget_layout.addLayout(self.choose_signals_buttons_layout)

        self.controls_widget_layout.addStretch()

        self.graph_controls_buttons_layout = QVBoxLayout()
        self.play_button = QPushButton("play")
        self.pause_button = QPushButton("pause")
        self.export_button = QPushButton("export")
        self.graph_controls_buttons_layout.addWidget(self.play_button)
        self.graph_controls_buttons_layout.addWidget(self.pause_button)
        self.graph_controls_buttons_layout.addWidget(self.export_button)
        self.controls_widget_layout.addLayout(self.graph_controls_buttons_layout)
        
        
        self.setLayout(main_layout)

        self.setStyleSheet("""
            QPushButton{
                padding:5px 20px
            }
        """)


    def plot_glue(self,x1,y1,x2,y2):
        pass
        



        
        