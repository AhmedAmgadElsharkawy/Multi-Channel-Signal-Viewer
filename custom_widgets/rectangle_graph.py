from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QVBoxLayout, QFileDialog,QScrollArea,QComboBox,QLabel,QLineEdit,QColorDialog,QCheckBox
from PyQt6.QtGui import QPainter, QPen ,QColor, QIcon, QPixmap
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
        self.yMinLimit = 0
        self.yMaxLimit = 0
        self.isRunning = False
        self.signalSpeed = 20
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.curves = []
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

        rectangle_and_controls_container = QHBoxLayout()
        self.setFixedHeight(240)

        # Create the plot widget
        self.rectangle_plot = pg.PlotWidget(name='Plot1')
        self.rectangle_plot.showGrid(x=True, y=True)
        self.rectangle_plot.resize(600, 240)

        # Create layout for controls and align to the top
        self.rectangle_signal_controls_widget = QWidget()
        self.rectangle_signal_controls_widget.setObjectName("controls_widget")
        rectangle_plot_controls = QVBoxLayout()
        self.rectangle_signal_controls_widget.setLayout(rectangle_plot_controls)
        rectangle_plot_controls.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.rectangle_plot.setLimits(xMin=0, xMax=1, yMin=-1, yMax=1)

        self.signals_props_widget = QWidget()
        self.signals_props_widget.setObjectName("signal_props_widget")
        signals_props1_layout = QVBoxLayout()
        self.signals_props_widget.setLayout(signals_props1_layout)
        # signals_props1_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        # self.signals_props1_widget.setFixedSize(150,200)
        self.signals_props_widget.setFixedWidth(300)
        # self.signals_props_widget.setStyleSheet("background-color:gray")

        self.signals_combobox = QComboBox()
        self.signals_combobox.setObjectName("signals-commbobox")
        signals_props1_layout.addWidget(self.signals_combobox)
        self.signals_combobox.currentIndexChanged.connect(self.on_signal_selected)
        
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
        self.line_color.setFixedSize(170,1)
        self.choose_color_button = QPushButton("Choose")
        # signal_color_widget_layout.addWidget(color_label)
        signal_color_widget_layout.addStretch()
        signal_color_widget_layout.addWidget(self.line_color)
        signal_color_widget_layout.addStretch()
        signal_color_widget_layout.addWidget(self.choose_color_button)
        # signal_color_widget_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        signal_color_widget.setLayout(signal_color_widget_layout)
        self.choose_color_button.clicked.connect(self.open_color_dialog)
        self.choose_color_button.setFixedWidth(60)
        signal_options_widget_layout.addWidget(signal_color_widget)

        signal_checkbox_widget = QWidget()
        signal_checkbox_widget_layout = QHBoxLayout()
        self.show_hide_checkbox = QCheckBox("Visible")
        signal_checkbox_widget_layout.addWidget(self.show_hide_checkbox)
        signal_checkbox_widget.setLayout(signal_checkbox_widget_layout)
        self.show_hide_checkbox.stateChanged.connect(self.toggle_curve_show)
        signal_options_widget_layout.addWidget(signal_checkbox_widget)

        signal_buttons_widget = QWidget()
        signal_buttons_widget_layout = QHBoxLayout()
        signal_buttons_widget.setLayout(signal_buttons_widget_layout)
        # update_signal_props_button = QPushButton("Update")
        self.delete_signal_button = QPushButton("Delete")
        self.move_button = QPushButton("Move")
        self.move_button.setFixedHeight(20)
        self.delete_signal_button.setFixedHeight(20)
        # signal_buttons_widget_layout.addWidget(update_signal_props_button)
        signal_buttons_widget_layout.addWidget(self.move_button)
        signal_buttons_widget_layout.addWidget(self.delete_signal_button)
        signal_options_widget_layout.addWidget(signal_buttons_widget)
        # signal_options_widget.setStyleSheet("background-color:red")
        # update_signal_props_button.clicked.connect(self.save_signals_props)
        self.delete_signal_button.clicked.connect(self.delete_signal)
        

        self.disable_props()
        self.linear_region_item = pg.LinearRegionItem(movable=True)
        self.linear_region_item.setVisible(False)
        self.rectangle_plot.addItem(self.linear_region_item)

        # Create buttons
        self.insert_button = QPushButton()
        self.play_and_pause_button = QPushButton()
        self.clear_button = QPushButton()
        self.rewind_button = QPushButton()
        self.speed_up_button = QPushButton()
        self.speed_down_button = QPushButton()
        self.disable_controls_buttons()
        self.insert_button.setEnabled(True)

        # Add buttons to the layout
        self.pause_icon = QIcon(); self.play_icon = QIcon(); add_signal_icon = QIcon(); 
        rewind_button_icon = QIcon(); clear_icon = QIcon(); speed_up_icon = QIcon(); speed_down_icon = QIcon()
        add_signal_icon.addPixmap(QPixmap("Images/plus.png"))
        self.pause_icon.addPixmap(QPixmap("Images/pause.png"))
        self.play_icon.addPixmap(QPixmap("Images/play.png"))
        rewind_button_icon.addPixmap(QPixmap("Images/rewind.png"))
        clear_icon.addPixmap(QPixmap("Images/clean.png"))
        speed_up_icon.addPixmap(QPixmap("Images/forward-button.png"))
        speed_down_icon.addPixmap(QPixmap("Images/rewind-button.png"))
        self.insert_button.setFixedSize(60, 25)
        self.play_and_pause_button.setFixedSize(60, 25)
        self.clear_button.setFixedSize(60, 25)
        self.rewind_button.setFixedSize(60, 25)
        self.speed_up_button.setFixedSize(60, 25)
        self.speed_down_button.setFixedSize(60, 25)
        self.insert_button.setIcon(add_signal_icon)
        self.play_and_pause_button.setIcon(self.pause_icon)
        self.rewind_button.setIcon(rewind_button_icon)
        self.clear_button.setIcon(clear_icon)
        self.speed_up_button.setIcon(speed_up_icon)
        self.speed_down_button.setIcon(speed_down_icon)
        rectangle_plot_controls.addWidget(self.insert_button)
        rectangle_plot_controls.addWidget(self.play_and_pause_button)
        rectangle_plot_controls.addWidget(self.rewind_button)
        rectangle_plot_controls.addWidget(self.clear_button)
        rectangle_plot_controls.addWidget(self.speed_up_button)
        rectangle_plot_controls.addWidget(self.speed_down_button)

        # Add plot and controls to the container
        controls_and_plot = QWidget()
        controls_and_plot_layout = QHBoxLayout()
        controls_and_plot.setLayout(controls_and_plot_layout)
        controls_and_plot_layout.addWidget(self.rectangle_plot)
        controls_and_plot_layout.addWidget(self.rectangle_signal_controls_widget)
        rectangle_and_controls_container.addWidget(controls_and_plot)
        rectangle_and_controls_container.addWidget(self.signals_props_widget)

        # rectangle_signal_controls_widget.setStyleSheet("""
        # # QWidget {
        # #     border: 2px solid black;  /* Define border thickness and color */
        # #     border-radius: 10px;  /* Optional: Add rounded corners */
        # #     padding: 10px;  /* Optional: Add padding inside the border */
        # # }
        # # """)   

        # # self.signals_props_widget.setStyleSheet("""
        # # QWidget {
        # #     border: 1px solid black;  /* Define border thickness and color */
        # #     border-radius: 10px;  /* Optional: Add rounded corners */
        # #     padding: 0px;  /* Optional: Add padding inside the border */
        # # }
        # # """)   

        # Add the container to the main layout
        self.setLayout(rectangle_and_controls_container)

        # Connect insert button to file browser
        self.insert_button.clicked.connect(self.browse_file)
        self.play_and_pause_button.clicked.connect(self.pauseSignals)
        self.speed_up_button.clicked.connect(self.increaseSpeed)
        self.speed_down_button.clicked.connect(self.decreaseSpeed)
        self.clear_button.clicked.connect(self.clearSignals)
        self.rewind_button.clicked.connect(self.rewindSignals)
        self.setStyleSheet(
            """
            *{
                padding:0px;
                margin:0px;
            }
            #signal_props_widget{
                border:1px solid gray;
                border-radius:20px
            }
            #controls_widget QPushButton{
                padding:5px 20px;
            }
    """
        )
        self.signals_props_widget.setStyleSheet("""
            QPushButton{
                        border:none;
                        background-color:white;
                        padding:3px;
                        border-radius:4px;
                        color:black;

            }   
            QPushButton:hover{
                    border:1px solid black 
                            }
            QPushButton:disabled{
                    background-color:gray;
                    color:white
                }
            QLineEdit{
                    background-color:white;
                    color:black;
                    padding:0px 5px
            } 
            QLineEdit:disabled{
                    background-color:gray;
                    color:white;
            } 
            QComboBox {
                    background-color:white;
                    color:black;
                                                }    
            QComboBox:disabled {
                background-color: gray;
                color: white;
            }
            PlotWidget{
            background-color:white}                                

            #signals-commbobox{
                    padding:0px 8px
                                                }
""")
        






        

    def add_signal(self, file_path):
        if not file_path:
            pass
        signal = Signal(file_path,len(self.signals))
        if len(signal.x) > self.xLimit:
            self.xLimit = len(signal.x)
        signal.color = self.colors[len(self.signals)%len(self.colors)]
        self.signals.append(signal)
        self.timer.stop()
        self.signalSpeed = 20
        self.isRunning = True
        self.play_and_pause_button.setIcon(self.pause_icon)
        self.play_and_pause_button.clicked.connect(self.pauseSignals)
        self.signals_combobox.addItem(signal.label,userData=len(self.signals)-1)

        
        self.ptr = 0
        curve = self.rectangle_plot.plot(pen=pg.mkPen(color=signal.color))
        self.curves.append(curve)
        self.rectangle_plot.setLabel('bottom', 'Time', 's')
        self.rectangle_plot.setXRange(0, 1)  # Initial range
        self.rectangle_plot.setYRange(self.yMinLimit, self.yMaxLimit)
        self.rectangle_plot.setLimits(yMin=self.yMinLimit, yMax=self.yMaxLimit)

        # Set up the QTimer
        self.timer.start(self.signalSpeed)  # 20 milliseconds
        

    def update_plot(self):
        if self.ptr < self.xLimit and self.isRunning:
            for i, curve in enumerate(self.curves):
                if self.signals[i].show:
                    if len(self.signals[i].x) >= self.ptr:
                        curve.setData(self.signals[i].x[:self.ptr], self.signals[i].y[:self.ptr])  # Update each curve
                        if self.ptr < len(self.signals[i].x):
                            self.yMinLimit = min(self.yMinLimit, self.signals[i].y[self.ptr])
                            self.yMaxLimit = max(self.yMaxLimit, self.signals[i].y[self.ptr])
                        self.rectangle_plot.setLimits(yMin = self.yMinLimit, yMax = self.yMaxLimit)
                        if self.ptr / 1000 > 1:
                            self.rectangle_plot.setLimits(xMin=0, xMax=((self.ptr / 1000)))
            self.ptr += 1
            self.rectangle_plot.setXRange((self.ptr / 1000), (self.ptr / 1000))
            self.rectangle_plot.setYRange(self.yMinLimit, self.yMaxLimit)

    def browse_file(self):
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)")
        if file_path:
            self.add_signal(file_path)

    def plot(self):
        for signal in self.signals:
            self.rectangle_plot.plot(signal.y)

    def pauseSignals(self):
        self.isRunning = False
        self.play_and_pause_button.setIcon(self.play_icon)
        self.play_and_pause_button.clicked.connect(self.playSignals)

    def playSignals(self):
        self.isRunning = True
        self.play_and_pause_button.setIcon(self.pause_icon)
        self.play_and_pause_button.clicked.connect(self.pauseSignals)

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
        self.rectangle_plot.addItem(self.linear_region_item)
        self.rectangle_plot.setXRange(0, 1)  # Initial range
        self.rectangle_plot.setYRange(-1, 1)
        self.yMinLimit = 0
        self.yMaxLimit = 0
        self.xLimit = 0
        self.rectangle_plot.setLimits(xMin=0, xMax=1, yMin = -1, yMax = 1)
        self.signals_combobox.clear()
        self.timer.stop()

    def rewindSignals(self):
        self.timer.stop()
        self.ptr = 0
        self.yMinLimit = 0
        self.yMaxLimit = 0
        self.signalSpeed = 20
        self.rectangle_plot.setXRange(0, 1)  # Initial range
        self.rectangle_plot.setYRange(self.yMinLimit, self.yMaxLimit)
        self.rectangle_plot.setLimits(xMin=0, xMax=1)
        self.isRunning = True
        self.play_and_pause_button.setIcon(self.pause_icon)
        self.play_and_pause_button.clicked.connect(self.pauseSignals)
        self.timer.start(self.signalSpeed)
        
    def on_signal_selected(self):
        signal_index = self.signals_combobox.currentIndex()
        if(signal_index < 0): 
            self.disable_props()
            self.disable_controls_buttons()
            self.insert_button.setEnabled(True)
            return
        self.enable_props()
        self.enable_controls_buttons()
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
            color = color.name()
            self.line_color.setStyleSheet(f"border: 1px solid {color};")
            self.curves[self.signals_combobox.currentIndex()].setPen(pg.mkPen(color=color))
            self.signals[self.signals_combobox.currentIndex()].color = color
    
    def toggle_curve_show(self):
        self.signals[self.selected_signal].show = not self.signals[self.selected_signal].show
        if self.signals[self.selected_signal].show:
            self.rectangle_plot.addItem(self.curves[self.selected_signal])
        else:
            self.rectangle_plot.removeItem(self.curves[self.selected_signal]) 
        self.check_signals_states()

    def delete_signal(self):
        index = self.signals_combobox.currentIndex()
        self.signals.pop(index)
        self.rectangle_plot.removeItem(self.curves[index])
        self.curves.pop(index) 
        self.signals_combobox.removeItem(index)
        self.check_signals_states()
        

    def check_signals_states(self):
        max_ptr = -10
        miny = 1000
        maxy = -1000
        for signal in self.signals:
            if signal.show:
                max_ptr = max(max_ptr,len(signal.x))
                miny = min(miny, min(signal.y))
                maxy = max(maxy, max(signal.y))
        self.yMinLimit = miny
        self.yMaxLimit = maxy
        self.rectangle_plot.setLimits(yMin = self.yMinLimit, yMax = self.yMaxLimit)
        self.rectangle_plot.setYRange(self.yMinLimit, self.yMaxLimit)
        if max_ptr < self.ptr:
            if max_ptr >= 0:
                self.ptr = max_ptr
                self.rectangle_plot.setXRange((self.ptr / 1000) - 1.1, self.ptr / 1000)
                self.rectangle_plot.setLimits(xMin = 0, xMax = self.ptr / 1000)
            self.timer.stop()
        else:
            self.timer.start(self.signalSpeed)
            
    def change_label(self):
        new_label = self.label_input_field.text()
        if new_label == "":
            return
        index = self.signals_combobox.currentIndex()
        self.signals[index].label = new_label
        self.signals_combobox.setItemText(index, new_label)
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
        self.move_button.setEnabled(False)
        self.line_color.setStyleSheet("border: 2px dotted lightgray;")

    def enable_props(self):
        if len(self.signals) > 0:
            self.label_input_field.setEnabled(True)
            self.delete_signal_button.setEnabled(True)
            self.change_signal_label_button.setEnabled(True)
            self.choose_color_button.setEnabled(True)
            self.show_hide_checkbox.setEnabled(True)
            self.move_button.setEnabled(True)
            self.line_color.setStyleSheet(f"border: 1px solid {self.signals[self.signals_combobox.currentIndex()].color}")
            self.show_hide_checkbox.blockSignals(True)
            self.show_hide_checkbox.setChecked(self.signals[self.signals_combobox.currentIndex()].show)
            self.show_hide_checkbox.blockSignals(False)

    def enable_controls_buttons(self):
        self.insert_button.setEnabled(True)
        self.play_and_pause_button.setEnabled(True)
        self.clear_button.setEnabled(True) 
        self.rewind_button.setEnabled(True)
        self.speed_up_button.setEnabled(True)
        self.speed_down_button.setEnabled(True)
    
    def disable_controls_buttons(self):
        self.insert_button.setEnabled(False)
        self.play_and_pause_button.setEnabled(False)
        self.clear_button.setEnabled(False) 
        self.rewind_button.setEnabled(False)
        self.speed_up_button.setEnabled(False)
        self.speed_down_button.setEnabled(False)

    
        
        







