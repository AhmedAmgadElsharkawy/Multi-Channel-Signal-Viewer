from PyQt6.QtWidgets import QWidget,QHBoxLayout
import pyqtgraph as pg
from scipy.interpolate import interp1d


class GlueGraph(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        main_layout = QHBoxLayout()

        self.glue_plot = pg.PlotWidget()
        main_layout.addWidget(self.glue_plot)
        self.setFixedHeight(200)

        self.setLayout(main_layout)

    def plot_glue(self,x1,y1,x2,y2):
        pass
        



        
        