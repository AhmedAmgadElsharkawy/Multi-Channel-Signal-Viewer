import sys
from PyQt6.QtWidgets import QApplication,QMainWindow,QVBoxLayout,QHBoxLayout,QGridLayout,QWidget,QLabel, QPushButton, QCheckBox, QMessageBox,QComboBox,QSizePolicy
from PyQt6.QtCore import Qt
from custom_widgets.example import Example
from custom_widgets.rectangle_graph import RectangleGraph
from custom_widgets.glue_graph import GlueGraph
import numpy as np


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.isSyncingX = False
        self.setWindowTitle("Multi-Channel-Signal-Viewer")
        self.resize(800, 600)
        self.initUI()

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        main_layout.setSpacing(1)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Here’s an example showing how to use custom widgets; feel free to uncomment it.
        # example = Example()
        # main_layout.addWidget(example)

        # add your custom widgets below
        self.rectangle_plot1 = RectangleGraph()
        self.rectangle_plot2 = RectangleGraph()
        self.rectangle_plot1.move_button.setText("Move Down")
        self.rectangle_plot2.move_button.setText("Move Up")
        self.rectangle_plot1.move_button.clicked.connect(self.move_down)
        self.rectangle_plot2.move_button.clicked.connect(self.move_up)
        main_layout.addWidget(self.rectangle_plot1)
        self.link_h_widget = QWidget()
        self.link_h_box = QHBoxLayout()
        self.link_h_widget.setLayout(self.link_h_box)
        self.line_container = QHBoxLayout()
        self.link_options_widget = QWidget()
        self.link_options = QHBoxLayout()
        self.link_options_widget.setLayout(self.link_options)
        self.link_button = QCheckBox("Link graphs", self) 
        self.link_h_box.addLayout(self.line_container)
        self.line_container.addWidget(self.link_button)
        self.line_container.addWidget(self.link_options_widget)
        self.link_h_widget.setFixedHeight(50)
        self.line_container.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.link_options_widget.setVisible(False)

        self.pause_link = QPushButton("Pause", self)
        self.play_link = QPushButton("Play", self)
        self.speed_up_link = QPushButton("Speed up", self)
        self.speed_down_link = QPushButton("Speed down", self)
        self.rewind_link = QPushButton("Rewind", self)
        self.link_options.addWidget(self.pause_link)
        self.link_options.addWidget(self.play_link)
        self.link_options.addWidget(self.rewind_link)
        self.link_options.addWidget(self.speed_up_link)
        self.link_options.addWidget(self.speed_down_link)
        self.pause_link.clicked.connect(self.pasue_linked_signals)
        self.play_link.clicked.connect(self.play_linked_signals)
        self.speed_up_link.clicked.connect(self.speed_up_linked_signals)
        self.speed_down_link.clicked.connect(self.speed_down_linked_signals)
        self.rewind_link.clicked.connect(self.rewind_linked_signals)
        self.link_button.setEnabled(False)

        
        main_layout.addWidget(self.rectangle_plot2)
        main_layout.addWidget(self.link_h_widget)

        self.link_button.setFixedHeight(20)  # Set the height of the checkbox
        


        


        glue_widget = QWidget()
        glue_widget_layout = QHBoxLayout()
        glue_widget.setLayout(glue_widget_layout)
        glue_widget_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.link_h_box.addWidget(glue_widget)
        self.glue_button = QPushButton("Glue")
        glue_widget_layout.addWidget(self.glue_button)
        self.confirm_glue_button = QPushButton("Confirm")
        self.cancel_glue_button = QPushButton("Cancel")
        self.next_button = QPushButton("Next")
        glue_widget_layout.addWidget(self.confirm_glue_button)
        glue_widget_layout.addWidget(self.cancel_glue_button)
        self.cancel_glue_button.hide()
        self.confirm_glue_button.hide()
        self.cancel_glue_button.clicked.connect(self.cancel_signals_glue)
        self.glue_button.clicked.connect(self.start_signals_glue)
        self.confirm_glue_button.clicked.connect(self.confirm_signals_glue)
        self.glue_button.setEnabled(False)
        self.rectangle_plot1.signals_combobox1.currentIndexChanged.connect(self.update_glue_button)
        self.rectangle_plot2.signals_combobox1.currentIndexChanged.connect(self.update_glue_button)
        self.glue_graph = GlueGraph()
        main_layout.addWidget(self.glue_graph)

        

        # set main layout of central widget
        self.link_button.stateChanged.connect(self.link_button_changed)
        central_widget.setLayout(main_layout)

        self.setStyleSheet("""
            *{
                           padding:0px;
                           margin:0px;
            }
        """)
    
    def start_signals_glue(self):
        self.rectangle_plot1.pauseSignals()
        self.rectangle_plot2.pauseSignals()
        self.rectangle_plot1.linear_region_item.setVisible(True)
        self.rectangle_plot2.linear_region_item.setVisible(True)
        rectangle_plot1_xRange = self.rectangle_plot1.rectangle_plot.getViewBox().viewRange()[0]
        rectangle_plot2_xRange = self.rectangle_plot2.rectangle_plot.getViewBox().viewRange()[0]
        linear_region_item1_end = ((self.rectangle_plot1.ptr)/1000 - rectangle_plot1_xRange[0])/2 + rectangle_plot1_xRange[0]
        linear_region_item2_end = ((self.rectangle_plot2.ptr)/1000 - rectangle_plot2_xRange[0])/2 + rectangle_plot2_xRange[0]
        self.rectangle_plot1.linear_region_item.setBounds([0,(self.rectangle_plot1.ptr)/1000])
        self.rectangle_plot2.linear_region_item.setBounds([0,(self.rectangle_plot2.ptr)/1000])
        self.rectangle_plot1.linear_region_item.setRegion([rectangle_plot1_xRange[0],linear_region_item1_end])
        self.rectangle_plot2.linear_region_item.setRegion([rectangle_plot2_xRange[0],linear_region_item2_end])
        self.glue_button.hide()
        # self.choose_glue_signal1.show()
        # self.choose_glue_signal2.show()
        self.confirm_glue_button.show()
        self.cancel_glue_button.show()
        signal1_index = self.rectangle_plot1.signals_combobox1.currentIndex()
        signal2_index = self.rectangle_plot2.signals_combobox1.currentIndex()
        for i,curve in enumerate(self.rectangle_plot1.curves):
            if i == signal1_index:
                continue
            self.rectangle_plot1.rectangle_plot.removeItem(curve)

        for i,curve in enumerate(self.rectangle_plot2.curves):
            if i == signal2_index:
                continue
            self.rectangle_plot2.rectangle_plot.removeItem(curve)


    def cancel_signals_glue(self):
        self.rectangle_plot1.linear_region_item.setVisible(False)
        self.rectangle_plot2.linear_region_item.setVisible(False)
        self.rectangle_plot1.playSignals()
        self.rectangle_plot2.playSignals()
        self.glue_button.show()
        # self.choose_glue_signal1.hide()
        # self.choose_glue_signal2.hide()
        self.cancel_glue_button.hide()
        self.confirm_glue_button.hide()

        signal1_index = self.rectangle_plot1.signals_combobox1.currentIndex()
        signal2_index = self.rectangle_plot2.signals_combobox1.currentIndex()

        for i,curve in enumerate(self.rectangle_plot1.curves):
            if i == signal1_index:
                continue
            self.rectangle_plot1.rectangle_plot.addItem(curve)
            
        for i,curve in enumerate(self.rectangle_plot2.curves):
            if i == signal2_index:
                continue
            self.rectangle_plot2.rectangle_plot.addItem(curve)

    def confirm_signals_glue(self):
        signal_region1 = self.rectangle_plot1.linear_region_item.getRegion()
        signal_region2 = self.rectangle_plot2.linear_region_item.getRegion()

        new_x1 = []
        new_y1 = []
        new_x2 = []
        new_y2 = []
        x1 = self.rectangle_plot1.signals[self.rectangle_plot1.signals_combobox1.currentIndex()].x
        x2 = self.rectangle_plot2.signals[self.rectangle_plot2.signals_combobox1.currentIndex()].x
        y1 = self.rectangle_plot1.signals[self.rectangle_plot1.signals_combobox1.currentIndex()].y
        y2 = self.rectangle_plot2.signals[self.rectangle_plot2.signals_combobox1.currentIndex()].y
        
        for i,x in enumerate(x1):
            if x >= signal_region1[0] and x <= signal_region1[1]:
                new_x1.append(x)
                new_y1.append(y1[i])

        for i,x in enumerate(x2):
            if x >= signal_region2[0] and x <= signal_region2[1]:
                new_x2.append(x)
                new_y2.append(y2[i])
        
        new_x1 = np.array(new_x1)
        new_y1 = np.array(new_y1)
        new_x2 = np.array(new_x2)
        new_y2 = np.array(new_y2)

        self.glue_graph.plot_glue(new_x1,new_y1,new_x2,new_y2)




        
    def update_glue_button(self):
        if self.rectangle_plot1.signals_combobox1.currentIndex() >=0 and self.rectangle_plot2.signals_combobox1.currentIndex() >=0:
            self.glue_button.setEnabled(True)
            self.link_button.setEnabled(True)
        else:
            self.glue_button.setEnabled(False)
            self.link_button.setEnabled(False)
            self.link_button.setCheckState(Qt.CheckState.Unchecked)
    

        



    def link_button_changed(self):
        sender = self.sender()
        if sender.isChecked():
            self.rectangle_plot1.rewindSignals()
            self.rectangle_plot2.rewindSignals()
            self.rectangle_plot1.rectangle_plot.getViewBox().sigXRangeChanged.connect(self.synchronizePosGraph1)
            self.rectangle_plot2.rectangle_plot.getViewBox().sigXRangeChanged.connect(self.synchronizePosGraph2)
            self.rectangle_plot1.rectangle_plot.getViewBox().sigYRangeChanged.connect(self.synchronizePosGraph1)
            self.rectangle_plot2.rectangle_plot.getViewBox().sigYRangeChanged.connect(self.synchronizePosGraph2)
            self.link_options_widget.setVisible(True)
            self.rectangle_plot1.disable_controls_buttons()
            self.rectangle_plot2.disable_controls_buttons()
        else:
            self.rectangle_plot1.enable_controls_buttons()
            self.rectangle_plot2.enable_controls_buttons()
            self.link_options_widget.setVisible(False)
            self.rectangle_plot1.rectangle_plot.getViewBox().sigXRangeChanged.disconnect(self.synchronizePosGraph1)
            self.rectangle_plot2.rectangle_plot.getViewBox().sigXRangeChanged.disconnect(self.synchronizePosGraph2)
            self.rectangle_plot1.rectangle_plot.getViewBox().sigYRangeChanged.disconnect(self.synchronizePosGraph1)
            self.rectangle_plot2.rectangle_plot.getViewBox().sigYRangeChanged.disconnect(self.synchronizePosGraph2)

    def pasue_linked_signals(self):
        self.rectangle_plot1.pauseSignals()
        self.rectangle_plot2.pauseSignals()
    
    def play_linked_signals(self):
        self.rectangle_plot1.playSignals()
        self.rectangle_plot2.playSignals()

    def speed_up_linked_signals(self):
        self.rectangle_plot1.increaseSpeed()
        self.rectangle_plot2.increaseSpeed()


    def speed_down_linked_signals(self):
        self.rectangle_plot1.decreaseSpeed()
        self.rectangle_plot2.decreaseSpeed()

    def rewind_linked_signals(self):
        self.rectangle_plot1.rewindSignals()
        self.rectangle_plot2.rewindSignals()

    def synchronizePosGraph1(self):
        if not self.isSyncingX and not self.rectangle_plot1.isRunning:
            self.rectangle_plot2.rectangle_plot.getViewBox().sigXRangeChanged.disconnect(self.synchronizePosGraph2)
            self.rectangle_plot2.rectangle_plot.getViewBox().sigYRangeChanged.disconnect(self.synchronizePosGraph2)
                
            # Set the X-axis range of graph2 based on graph1
            xRange = self.rectangle_plot1.rectangle_plot.getViewBox().viewRange()[0]
            yRange = self.rectangle_plot1.rectangle_plot.getViewBox().viewRange()[1]
            self.isSyncingX = True
            self.rectangle_plot2.rectangle_plot.getViewBox().setXRange(*xRange)
            self.rectangle_plot2.rectangle_plot.getViewBox().setYRange(*yRange)
            self.isSyncingX = False
            
            # Reconnect the signal
            self.rectangle_plot2.rectangle_plot.getViewBox().sigXRangeChanged.connect(self.synchronizePosGraph2)
            self.rectangle_plot2.rectangle_plot.getViewBox().sigYRangeChanged.connect(self.synchronizePosGraph2)

    def synchronizePosGraph2(self):
        if not self.isSyncingX and not self.rectangle_plot2.isRunning:
            self.rectangle_plot1.rectangle_plot.getViewBox().sigXRangeChanged.disconnect(self.synchronizePosGraph1)
            self.rectangle_plot1.rectangle_plot.getViewBox().sigYRangeChanged.disconnect(self.synchronizePosGraph1)
                
            # Set the X-axis range of graph2 based on graph1
            xRange = self.rectangle_plot2.rectangle_plot.getViewBox().viewRange()[0]
            yRange = self.rectangle_plot2.rectangle_plot.getViewBox().viewRange()[1]
            self.isSyncingX = True
            self.rectangle_plot1.rectangle_plot.getViewBox().setXRange(*xRange)
            self.rectangle_plot1.rectangle_plot.getViewBox().setYRange(*yRange)
            self.isSyncingX = False
            
            # Reconnect the signal
            self.rectangle_plot1.rectangle_plot.getViewBox().sigXRangeChanged.connect(self.synchronizePosGraph1)
            self.rectangle_plot1.rectangle_plot.getViewBox().sigYRangeChanged.connect(self.synchronizePosGraph1)

    
    def move_down(self):
        index = self.rectangle_plot1.signals_combobox1.currentIndex()
        signal = self.rectangle_plot1.signals[index]
        curve = self.rectangle_plot1.curves[index]
        self.rectangle_plot1.delete_signal()
        self.rectangle_plot2.signals.append(signal)
        self.rectangle_plot2.curves.append(curve)
        self.rectangle_plot2.signals_combobox1.addItem(signal.label)
        self.rectangle_plot2.rectangle_plot.addItem(curve)



    def move_up(self):
        index = self.rectangle_plot2.signals_combobox1.currentIndex()
        signal = self.rectangle_plot2.signals[index]
        curve = self.rectangle_plot2.curves[index]
        self.rectangle_plot2.delete_signal()
        self.rectangle_plot1.signals.append(signal)
        self.rectangle_plot1.curves.append(curve)
        self.rectangle_plot1.signals_combobox1.addItem(signal.label)
        self.rectangle_plot1.rectangle_plot.addItem(curve)
        
    

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()