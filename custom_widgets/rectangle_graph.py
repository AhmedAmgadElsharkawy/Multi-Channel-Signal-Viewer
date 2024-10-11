from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QVBoxLayout, QFileDialog,QScrollArea,QComboBox,QLabel,QLineEdit,QColorDialog,QCheckBox
from PyQt6.QtGui import QPainter, QPen ,QColor
import pyqtgraph as pg
from PyQt6.QtCore import Qt,QTimer
import pandas as pd
from custom_widgets.signal import Signal


class RectangleGraph(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        # self.setStyleSheet("background-color:red")
        self.signals = []
        self.xLimit = 0
        self.isRunning = True
        self.signalSpeed = 20
        self.timer = QTimer(self)
        self.curves = []
        self.timer = QTimer(self)
        self.selected_signal = None
        self.colors = [
            '#ff0000',  # Red
            '#00ff00',  # Green
            '#0000ff',  # Blue
            '#ffff00',  # Yellow
            '#ff00ff',  # Magenta
            '#00ffff',  # Cyan
            '#800080',  # Purple
            '#ffa500',  # Orange
            '#008080',  # Teal
            '#808000'   # Olive
        ]


    def initUI(self):
        main_layout = QVBoxLayout()

        rectangle_signal_widget = QWidget()
        rectangle_and_controls_container = QHBoxLayout()
        rectangle_signal_widget.setLayout(rectangle_and_controls_container)
        rectangle_signal_widget.setFixedHeight(250)

        # Create the plot widget
        self.rectangle_plot = pg.PlotWidget(name='Plot1')
        self.rectangle_plot.resize(600, 240)

        # Create layout for controls and align to the top
        rectangle_signal_conntrols_widget = QWidget()
        rectangle_plot1_controls = QVBoxLayout()
        rectangle_signal_conntrols_widget.setLayout(rectangle_plot1_controls)
        rectangle_plot1_controls.setAlignment(Qt.AlignmentFlag.AlignTop)
        rectangle_signal_conntrols_widget.setFixedSize(100,200)
        self.rectangle_plot.setLimits(xMin=0, xMax=1, yMin=-2, yMax=2)

        self.signals_props1_widget = QWidget()
        signals_props1_layout = QVBoxLayout()
        self.signals_props1_widget.setLayout(signals_props1_layout)
        # signals_props1_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        # self.signals_props1_widget.setFixedSize(150,200)
        self.signals_props1_widget.setFixedWidth(190)
        self.signals_props1_widget.setStyleSheet("background-color:gray")

        self.signals_combobox1 = QComboBox()
        signals_props1_layout.addWidget(self.signals_combobox1)
        self.signals_combobox1.currentIndexChanged.connect(self.on_signal_selected)
        
        signal_options_widget = QWidget()
        signal_options_widget_layout = QVBoxLayout()
        signal_options_widget.setLayout(signal_options_widget_layout)
        signals_props1_layout.addWidget(signal_options_widget)

        signal_label_widget = QWidget()
        signal_label_widget_layout = QHBoxLayout()
        self.label_input_field = QLineEdit()
        signal_label_widget_layout.addWidget(self.label_input_field)
        signal_label_widget.setLayout(signal_label_widget_layout)
        signal_options_widget_layout.addWidget(signal_label_widget)
        self.change_signal_label_button = QPushButton("Change")
        self.change_signal_label_button.clicked.connect(self.change_label)
        self.change_signal_label_button.setFixedWidth(60)
        signal_label_widget_layout.addWidget(self.change_signal_label_button)


        signal_color_widget = QWidget()
        signal_color_widget_layout = QHBoxLayout()
        self.line_color = QWidget()
        self.line_color.setFixedSize(70,1)
        self.choose_color_button = QPushButton("Choose")
        # signal_color_widget_layout.addWidget(color_label)
        signal_color_widget_layout.addWidget(self.line_color)
        signal_color_widget_layout.addWidget(self.choose_color_button)
        # signal_color_widget_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        signal_color_widget.setLayout(signal_color_widget_layout)
        self.choose_color_button.clicked.connect(self.open_color_dialog)
        self.choose_color_button.setFixedWidth(60)
        signal_options_widget_layout.addWidget(signal_color_widget)

        signal_checkbox_widget = QWidget()
        signal_checkbox_widget_layout = QHBoxLayout()
        self.show_hide_checkbox = QCheckBox("Show")
        signal_checkbox_widget_layout.addWidget(self.show_hide_checkbox)
        signal_checkbox_widget.setLayout(signal_checkbox_widget_layout)
        self.show_hide_checkbox.stateChanged.connect(self.toggle_curve_show)
        signal_options_widget_layout.addWidget(signal_checkbox_widget)

        signal_buttons_widget = QWidget()
        signal_buttons_widget_layout = QHBoxLayout()
        signal_buttons_widget.setLayout(signal_buttons_widget_layout)
        # update_signal_props_button = QPushButton("Update")
        self.delete_signal_button = QPushButton("Delete")
        # signal_buttons_widget_layout.addWidget(update_signal_props_button)
        signal_buttons_widget_layout.addWidget(self.delete_signal_button)
        signal_options_widget_layout.addWidget(signal_buttons_widget)
        # signal_options_widget.setStyleSheet("background-color:red")
        # update_signal_props_button.clicked.connect(self.save_signals_props)
        self.delete_signal_button.clicked.connect(self.delete_signal)
        signal_buttons_widget.setFixedWidth(150)

        self.disable_props()


        





        # Create buttons
        self.insert_button1 = QPushButton("Insert")
        self.play_button1 = QPushButton("Play")
        self.pause_button1 = QPushButton("Pause")
        self.clear_button1 = QPushButton("Clear")
        self.rewind_button1 = QPushButton("Rewind")
        self.speed_up_button1 = QPushButton("Speed Up")
        self.speed_down_button1 = QPushButton("Speed Down")

        # Add buttons to the layout
        rectangle_plot1_controls.addWidget(self.insert_button1)
        rectangle_plot1_controls.addWidget(self.play_button1)
        rectangle_plot1_controls.addWidget(self.pause_button1)
        rectangle_plot1_controls.addWidget(self.rewind_button1)
        rectangle_plot1_controls.addWidget(self.clear_button1)
        rectangle_plot1_controls.addWidget(self.speed_up_button1)
        rectangle_plot1_controls.addWidget(self.speed_down_button1)


        # Add plot and controls to the container
        rectangle_and_controls_container.addWidget(self.rectangle_plot)
        rectangle_and_controls_container.addWidget(rectangle_signal_conntrols_widget)
        rectangle_and_controls_container.addWidget(self.signals_props1_widget)


        # Add the container to the main layout
        main_layout.addWidget(rectangle_signal_widget)
        self.setLayout(main_layout)

        # Connect insert button to file browser
        self.insert_button1.clicked.connect(self.browse_file)
        self.pause_button1.clicked.connect(self.pauseSignals)
        self.play_button1.clicked.connect(self.playSignals)
        self.speed_up_button1.clicked.connect(self.increaseSpeed)
        self.speed_down_button1.clicked.connect(self.decreaseSpeed)
        self.clear_button1.clicked.connect(self.clearSignals)
        self.rewind_button1.clicked.connect(self.rewindSignals)

    def add_signal(self, file_path):
        if not file_path:
            pass
        signal  = Signal(file_path,len(self.signals))
        if len(signal.x) > self.xLimit:
            self.xLimit = len(signal.x)
        signal.color = self.colors[len(self.signals)%len(self.colors)]
        self.signals.append(signal)
        self.isRunning = True
        self.timer.stop()
        self.signalSpeed = 20
        self.signals_combobox1.addItem(signal.label,userData=len(self.signals)-1)

        
        self.ptr = 0
        curve = self.rectangle_plot.plot(pen=pg.mkPen(color=signal.color))
        self.curves.append(curve)
        self.rectangle_plot.setLabel('bottom', 'Time', 's')
        self.rectangle_plot.setXRange(0, 1)  # Initial range
        self.rectangle_plot.setYRange(-1, 1)

        # Set up the QTimer
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(self.signalSpeed)  # 50 milliseconds
        

    def update_plot(self):
        if self.ptr < self.xLimit and self.isRunning:
            for i, curve in enumerate(self.curves):
                if self.signals[i].show:
                    if len(self.signals[i].x) >= self.ptr:
                        curve.setData(self.signals[i].x[:self.ptr], self.signals[i].y[:self.ptr])  # Update each curve
                        if self.ptr / 1000 > 1:
                            self.rectangle_plot.setLimits(xMin=0, xMax=((self.ptr / 1000)), yMin=-2, yMax=2)
            self.ptr += 1
            if self.ptr > 1000:
                self.rectangle_plot.setXRange((self.ptr / 1000) - 1, self.ptr / 1000)

    def browse_file(self):
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)")
        if file_path:
            self.add_signal(file_path)

    def plot(self):
        for signal in self.signals:
            self.rectangle_plot.plot(signal.y)

    def pauseSignals(self):
        print(self.rectangle_plot.getViewBox().viewRange()[1])

        self.isRunning = False

    def playSignals(self):
        self.isRunning = True

    def increaseSpeed(self):
        self.timer.stop()
        if (self.signalSpeed > 5):
            self.signalSpeed = int(self.signalSpeed / 2)
        self.timer.start(self.signalSpeed)

    def decreaseSpeed(self):
        self.timer.stop()
        if (self.signalSpeed < 40):
            self.signalSpeed = int(self.signalSpeed * 2)
        self.timer.start(self.signalSpeed)

    def clearSignals(self):
        self.signals.clear()
        self.curves.clear()
        self.rectangle_plot.clear() 
        self.rectangle_plot.setXRange(0, 1)  # Initial range
        self.rectangle_plot.setYRange(-1, 1)
        self.rectangle_plot.setLimits(xMin=0, xMax=1, yMin=-2, yMax=2)
        self.signals_combobox1.clear()
        self.timer.stop()

    def rewindSignals(self):
        self.ptr = 0
        self.signalSpeed = 20
        self.rectangle_plot.setXRange(0, 1)  # Initial range
        self.rectangle_plot.setYRange(-1, 1)
        self.rectangle_plot.setLimits(xMin=0, xMax=1, yMin=-2, yMax=2)
        self.isRunning = True
    def on_signal_selected(self):
        signal_index = self.signals_combobox1.currentIndex()
        if(signal_index < 0): 
            self.disable_props()
            return
        self.enable_props()
        selected_signal = self.signals[signal_index]
        self.label_input_field.setPlaceholderText(selected_signal.label)
        self.line_color.setStyleSheet(f"border: 2px solid {selected_signal.color};")
        self.selected_signal = signal_index
        self.show_hide_checkbox.blockSignals(True)
        self.show_hide_checkbox.setChecked(selected_signal.show)
        self.show_hide_checkbox.blockSignals(False)


    def open_color_dialog(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.line_color.setStyleSheet(f"border: 1px solid {color.name()};")
            self.curves[self.signals_combobox1.currentIndex()].setPen(pg.mkPen(color=color.name()))
            self.signals[self.signals_combobox1.currentIndex()].color = color
    
    def toggle_curve_show(self):
        self.signals[self.selected_signal].show = not self.signals[self.selected_signal].show
        if self.signals[self.selected_signal].show:
            self.rectangle_plot.addItem(self.curves[self.selected_signal])
        else:
            self.rectangle_plot.removeItem(self.curves[self.selected_signal]) 
        self.check_signals_states()

    def delete_signal(self):
        index = self.signals_combobox1.currentIndex()
        self.signals.pop(index)
        self.rectangle_plot.removeItem(self.curves[index])
        self.curves.pop(index) 
        self.signals_combobox1.removeItem(index)
        self.check_signals_states()
        

    def check_signals_states(self):
        max_ptr = -10
        for signal in self.signals:
            if signal.show:
                max_ptr = max(max_ptr,len(signal.x))
        if max_ptr < self.ptr:
            if max_ptr >= 0:
                self.ptr = max_ptr
                self.rectangle_plot.setXRange((self.ptr / 1000) - 1.1, self.ptr / 1000)
            self.timer.stop()
        else:
            self.timer.start()
            
    def change_label(self):
        new_label = self.label_input_field.text()
        if new_label == "":
            return
        index = self.signals_combobox1.currentIndex()
        self.signals[index].label = new_label
        self.signals_combobox1.setItemText(index, new_label)
        self.label_input_field.setText("")
        self.label_input_field.setPlaceholderText(new_label)

    def disable_props(self):
        self.label_input_field.setEnabled(False)
        self.delete_signal_button.setEnabled(False)
        self.change_signal_label_button.setEnabled(False)
        self.choose_color_button.setEnabled(False)
        self.show_hide_checkbox.blockSignals(True)
        self.show_hide_checkbox.setChecked(False)
        self.show_hide_checkbox.blockSignals(False)
        self.show_hide_checkbox.setEnabled(False)
        self.line_color.setStyleSheet("border: 2px dotted lightgray;")

    def enable_props(self):
        self.label_input_field.setEnabled(True)
        self.delete_signal_button.setEnabled(True)
        self.change_signal_label_button.setEnabled(True)
        self.choose_color_button.setEnabled(True)
        self.show_hide_checkbox.setEnabled(True)







