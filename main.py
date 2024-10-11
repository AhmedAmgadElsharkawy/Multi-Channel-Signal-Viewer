import sys
from PyQt6.QtWidgets import QApplication,QMainWindow,QVBoxLayout,QHBoxLayout,QGridLayout,QWidget,QLabel, QPushButton, QCheckBox, QMessageBox

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
        self.rectangle_plots = RectangleGraph()
        self.link_h_box = QHBoxLayout()
        self.link_options = QHBoxLayout()
        self.link_button = QCheckBox("Link graphs", self) 
        self.rectangle_plots1 = RectangleGraph()
        self.link_h_box.addWidget(self.link_button)
        self.link_h_box.addLayout(self.link_options)
        main_layout.addWidget(self.rectangle_plots)
        main_layout.addLayout(self.link_h_box)
        main_layout.addWidget(self.rectangle_plots1)
        

        # set main layout of central widget
        self.link_button.stateChanged.connect(self.link_button_changed)
        central_widget.setLayout(main_layout)


    def link_button_changed(self):
        sender = self.sender()
        if sender.isChecked():
            if len(self.rectangle_plots.signals) == 0 or len(self.rectangle_plots1.signals) == 0:
                QMessageBox.warning(self,"Operation Failed","You can't link the two graphs if one of them is empty")
                sender.setChecked(False)
                return
            self.rectangle_plots.insert_button1.setEnabled(False)
            self.rectangle_plots.play_button1.setEnabled(False)
            self.rectangle_plots.pause_button1.setEnabled(False) 
            self.rectangle_plots.clear_button1.setEnabled(False) 
            self.rectangle_plots.rewind_button1.setEnabled(False)
            self.rectangle_plots.speed_up_button1.setEnabled(False)
            self.rectangle_plots.speed_down_button1.setEnabled(False)
            self.rectangle_plots1.insert_button1.setEnabled(False)
            self.rectangle_plots1.play_button1.setEnabled(False)
            self.rectangle_plots1.pause_button1.setEnabled(False) 
            self.rectangle_plots1.clear_button1.setEnabled(False) 
            self.rectangle_plots1.rewind_button1.setEnabled(False)
            self.rectangle_plots1.speed_up_button1.setEnabled(False)
            self.rectangle_plots1.speed_down_button1.setEnabled(False)
            self.pause_link = QPushButton("Pause", self)
            self.play_link = QPushButton("Play", self)
            self.zoom_in_link = QPushButton("Zoom in", self)
            self.zoom_out_link = QPushButton("Zoom out", self)
            self.link_options.addWidget(self.pause_link)
            self.link_options.addWidget(self.play_link)
            self.link_options.addWidget(self.zoom_in_link)
            self.link_options.addWidget(self.zoom_out_link)
            

        else:
            self.rectangle_plots.insert_button1.setEnabled(True)
            self.rectangle_plots.play_button1.setEnabled(True)
            self.rectangle_plots.pause_button1.setEnabled(True) 
            self.rectangle_plots.clear_button1.setEnabled(True) 
            self.rectangle_plots.rewind_button1.setEnabled(True)
            self.rectangle_plots.speed_up_button1.setEnabled(True)
            self.rectangle_plots.speed_down_button1.setEnabled(True)
            self.rectangle_plots1.insert_button1.setEnabled(True)
            self.rectangle_plots1.play_button1.setEnabled(True)
            self.rectangle_plots1.pause_button1.setEnabled(True) 
            self.rectangle_plots1.clear_button1.setEnabled(True) 
            self.rectangle_plots1.rewind_button1.setEnabled(True)
            self.rectangle_plots1.speed_up_button1.setEnabled(True)
            self.rectangle_plots1.speed_down_button1.setEnabled(True)
            self.remove_option_widgets()

    def remove_option_widgets(self):
        while self.link_options.count():
            item = self.link_options.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()



def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()