from PyQt6.QtWidgets import QWidget,QLabel

class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        label = QLabel("example-custom-widget",self)
        label.setProperty("class","example-label")

        self.setStyleSheet("""
            .example-label{
                           background-color:blue;
                           padding:4px;
                           border-radius:5px;
            }
            .example-label:hover{
                           background-color:white;
                           color:blue;
            }
        """)