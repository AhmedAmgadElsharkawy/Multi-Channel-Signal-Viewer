import sys
from PyQt6.QtWidgets import QApplication,QMainWindow,QVBoxLayout,QHBoxLayout,QGridLayout,QWidget,QLabel

from custom_widgets.example import Example
from custom_widgets.rectangle_graph import RectangleGraph

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
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
        rectangle_plots = RectangleGraph()
        main_layout.addWidget(rectangle_plots)
        

        # set main layout of central widget
        central_widget.setLayout(main_layout)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()