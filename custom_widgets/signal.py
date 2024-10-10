from PyQt6.QtWidgets import QWidget,QLabel
import pandas as pd


class Signal(QWidget):
    def __init__(self,file_path,index):
        super().__init__()
        self.name = f"signal_{index}"
        data = pd.read_csv(file_path).iloc[:,0:2]
        self.x = data.iloc[:,0]
        self.y = data.iloc[:,1]


        