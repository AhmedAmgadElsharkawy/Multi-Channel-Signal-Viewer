from PyQt6.QtWidgets import QWidget,QHBoxLayout,QVBoxLayout,QPushButton,QRadioButton,QButtonGroup,QLabel
import pyqtgraph as pg
from scipy.interpolate import interp1d
from PyQt6.QtCore import Qt,QTimer
import requests
import numpy as np
import threading



def fetch_live_signal_async(callback):
    url = "https://rest.coinapi.io/v1/exchangerate/BTC/USD"
    headers = {
        'X-CoinAPI-Key': 'be094979-cff5-4872-b993-d9c360e39def',  # Replace with your CoinAPI Key
    }

    def run():
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                rate = float(data['rate'])  # Fetch the Bitcoin price in USD
                callback(rate)
            else:
                print(f"Error fetching data: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error during API call: {e}")

    threading.Thread(target=run, daemon=True).start()
 



class GlueAndLiveGraph(QWidget):
    def __init__(self):
        super().__init__()
        self.fetching_rate = 5000
        self.is_paused = False
        self.is_rewind = False
        self.signal_color = 'g'  # Default color
        self.signal_label = "Live Bitcoin Price Signal"
        self.show_signal = True
        self.auto_scroll_enabled = True  # To track if auto-scrolling is enabled

        # Initialize timer for updating the signal
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_signal)
        self.initUI()
        self.full_signal_data = []  # Store all historical data
        self.full_time_data = []    # Store all historical time data
        self.index = 0              # Index for the time axis
        self.window_size = 100      # Number of points to display in the sliding window

        # Start the timer to update every 1000 ms (1 second)
        self.timer.start(self.fetching_rate)
 

    def initUI(self):
        main_layout = QHBoxLayout()

        self.glue_and_live_plot = pg.PlotWidget()
        main_layout.addWidget(self.glue_and_live_plot)
        self.setFixedHeight(240)
        self.setFixedWidth(1200)

        self.controls_widget = QWidget()
        self.controls_widget_layout = QVBoxLayout()
        self.controls_widget.setLayout(self.controls_widget_layout)
        main_layout.addWidget(self.controls_widget)


        self.choose_signals_buttons_layout = QVBoxLayout()
        # self.live_signal_button = QPushButton("Live")
        # self.choose_signals_buttons_layout.addWidget(self.live_signal_button)
        self.choose_signal_label = QLabel("Choose Signal:")
        self.choose_signals_buttons_layout.addWidget(self.choose_signal_label)
        self.radio_buttons_group = QButtonGroup()
        self.live_radio_button = QRadioButton("Live")
        self.glue_radio_button = QRadioButton("Glue")
        self.radio_buttons_group.addButton(self.live_radio_button)
        self.radio_buttons_group.addButton(self.glue_radio_button)
        self.choose_signals_buttons_layout.addWidget(self.live_radio_button)
        self.choose_signals_buttons_layout.addWidget(self.glue_radio_button)
        self.live_radio_button.toggled.connect(self.run_live_signal)
        self.glue_radio_button.toggled.connect(self.open_glue_signal)
        
        

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
        self.pause_button.clicked.connect(self.pause_signal)
        self.play_button.clicked.connect(self.play_signal)



        # self.curve = self.glue_and_live_plot.plot(pen=pg.mkPen("#ff0000", width=5))

        # self.play_button.clicked.connect(self.play_live_signal)
        # self.pause_button.clicked.connect(self.pause_live_signal)

        self.cropped_signal_curve1 = self.glue_and_live_plot.plot(pen=pg.mkPen(color="#ff0000"))
        self.cropped_signal_curve2 = self.glue_and_live_plot.plot(pen=pg.mkPen(color="#00ff00"))  
        self.glue_output_curve = self.glue_and_live_plot.plot(pen=pg.mkPen(color="#00ff00"))  
        self.linear_region1 = pg.LinearRegionItem()  
        self.linear_region2 = pg.LinearRegionItem() 

        self.glue_and_live_plot.removeItem(self.cropped_signal_curve1)
        self.glue_and_live_plot.removeItem(self.cropped_signal_curve2)
        self.glue_and_live_plot.removeItem(self.glue_output_curve)


        self.live_curve = self.glue_and_live_plot.plot(pen=pg.mkPen(self.signal_color, width=2), name=self.signal_label)
        self.glue_and_live_plot.scene().sigMouseClicked.connect(self.on_manual_interaction)
        self.glue_and_live_plot.sigRangeChanged.connect(self.on_range_change)
        self.live_radio_button.setChecked(True)
        
        self.setLayout(main_layout)

        self.setStyleSheet("""
            QPushButton{
                padding:5px 20px
            }
        """)


    def update_signal(self):
        if not self.is_paused:
            # Fetch the data asynchronously and update when it arrives
            fetch_live_signal_async(self.process_new_price)

    def process_new_price(self, current_price):
        if current_price is not None:
            # Append new data to the full historical signal and time data
            self.full_signal_data.append(current_price)
            self.full_time_data.append(self.index)
            self.index += 1

            # Update the plot with all data
            self.live_curve.setData(self.full_time_data, self.full_signal_data)
            # Set X range to start from 0 and slide forward if auto-scrolling is enabled
            if self.auto_scroll_enabled:
                if self.index > self.window_size:
                    self.glue_and_live_plot.setXRange(self.index - self.window_size, self.index)
                else:
                    self.glue_and_live_plot.setXRange(0, self.window_size)


    def on_manual_interaction(self, event):
        """Disable auto-scrolling when the user manually interacts with the graph."""
        self.auto_scroll_enabled = False

    def on_range_change(self):
        """Re-enable auto-scrolling when the user is no longer manually interacting."""
        # This event gets triggered whenever the range of the view changes, e.g., when scrolling or panning.
        if not self.auto_scroll_enabled:
            self.timer.singleShot(5000, self.reset_auto_scroll)  # Allow manual interaction for 5 seconds

    def reset_auto_scroll(self):
        """Re-enable auto-scrolling after a delay, assuming the user is done interacting."""
        self.auto_scroll_enabled = True
        # After re-enabling auto-scroll, move the view to the latest data
        if self.index > self.window_size:
            self.glue_and_live_plot.setXRange(self.index - self.window_size, self.index)

    def play_signal(self):
        self.is_paused = False
        self.is_rewind = False

    def pause_signal(self):
        self.is_paused = True
        print(self.live_curve.getData()[0][0])
        

    def plot_cropped_signals(self,x1,y1,x2,y2,color1,color2):

         self.cropped_signal_curve1.setData(x1,y1)   
         self.cropped_signal_curve2.setData(x2,y2)
         self.cropped_signal_curve1.setPen(pg.mkPen(color=color1))
         self.cropped_signal_curve2.setPen(pg.mkPen(color=color2))
         self.fixed_width1 = x1[-1] - x1[0]
         self.fixed_width2 = x2[-1] - x2[0]
         self.linear_region1.setRegion([x1[0], x1[-1]])  
         self.linear_region2.setRegion([x2[0], x2[-1]])  

        #  self.linear_region1.setRegion([self.linear_region1.getRegion()[0], self.linear_region1.getRegion()[0] + self.fixed_width1])
        #  self.linear_region2.setRegion([self.linear_region2.getRegion()[0], self.linear_region2.getRegion()[0] + self.fixed_width2])
         self.glue_and_live_plot.clear()
         self.glue_and_live_plot.addItem(self.cropped_signal_curve1)
         self.glue_and_live_plot.addItem(self.cropped_signal_curve2)

         self.glue_and_live_plot.addItem(self.linear_region1)
         self.glue_and_live_plot.addItem(self.linear_region2)

         self.linear_region1.lines[0].setMovable(False)
         self.linear_region1.lines[1].setMovable(False)
         self.linear_region2.lines[0].setMovable(False)
         self.linear_region2.lines[1].setMovable(False)
         self.linear_region1.sigRegionChanged.connect(self.align_cropped_singals)
         self.linear_region2.sigRegionChanged.connect(self.align_cropped_singals)

         max_xrange = max(x1[-1],x2[-1])
         min_xrange = min(x1[0],x2[0])
         

         self.glue_and_live_plot.setXRange(min_xrange,max_xrange)
         self.glue_and_live_plot.setLimits(xMin=0)

         self.glue_radio_button.toggled.connect(self.open_glue_signal)
         self.live_radio_button.toggled.connect(self.run_live_signal)

         





    def open_glue_signal(self):
        self.timer.stop()
        self.glue_and_live_plot.removeItem(self.live_curve)
        self.glue_and_live_plot.removeItem(self.glue_output_curve)
        self.glue_and_live_plot.addItem(self.glue_output_curve)
        if (self.glue_output_curve.getData()[0]) is not None:
            self.glue_and_live_plot.setXRange(max(0,self.glue_output_curve.getData()[0][1]-1),self.glue_output_curve.getData()[0][-1])
            
        self.enable_controls()

    def run_live_signal(self):
        self.glue_and_live_plot.removeItem(self.glue_output_curve)
        self.glue_and_live_plot.removeItem(self.live_curve)
        self.glue_and_live_plot.addItem(self.live_curve)
        if (self.live_curve.getData()[0]) is not None:
            self.glue_and_live_plot.setXRange(max(0,self.live_curve.getData()[0][-1]-3),self.live_curve.getData()[0][-1])
            self.glue_and_live_plot.setYRange(-1,1)
        self.glue_and_live_plot.setLimits(xMin=0)

        self.timer.start(self.fetching_rate)
        self.enable_controls()


        
    # def update_signal(self): ##################################################3
    #     if not self.is_paused:
    #         if self.is_rewind:
    #             self.index = max(0, self.index - 1)
    #         else:
    #             self.index = (self.index + 1) % len(self.signal_data) #ensures that when self.index reaches the end of the signal data, it loops back to the beginning.
            
    #         # Simulate the cine mode by showing a slice of data
    #         start_idx = max(0, self.index - 100)
    #         end_idx = self.index
    #         self.curve.setData(self.signal_data[start_idx:end_idx])
        
    # def play_live_signal(self):
    #     self.is_paused = False
    #     self.is_rewind = False
    
    # def pause_live_signal(self):
    #     self.is_paused = True

    def align_cropped_singals(self):
         self.linear_region1.setRegion([self.linear_region1.getRegion()[0], self.linear_region1.getRegion()[0] + self.fixed_width1])
         self.linear_region2.setRegion([self.linear_region2.getRegion()[0], self.linear_region2.getRegion()[0] + self.fixed_width2])
         cropped_signal1_shift = self.linear_region1.getRegion()[0] - self.cropped_signal_curve1.getData()[0][0]
         cropped_signal2_shift = self.linear_region2.getRegion()[0] - self.cropped_signal_curve2.getData()[0][0]
         new_x1 = self.cropped_signal_curve1.getData()[0] + cropped_signal1_shift
         new_x2 = self.cropped_signal_curve2.getData()[0] + cropped_signal2_shift

         self.cropped_signal_curve1.setData(new_x1, self.cropped_signal_curve1.getData()[1])
         self.cropped_signal_curve2.setData(new_x2, self.cropped_signal_curve2.getData()[1])

    def disable_controls(self):
         self.live_radio_button.setEnabled(False)
         self.glue_radio_button.setEnabled(False)
         self.play_button.setEnabled(False)
         self.pause_button.setEnabled(False)
         self.export_button.setEnabled(False)

    def enable_controls(self):
         self.live_radio_button.setEnabled(True)
         self.glue_radio_button.setEnabled(True)
         if self.live_radio_button.isChecked():
            self.play_button.setEnabled(True)
            self.pause_button.setEnabled(True)
            self.export_button.setEnabled(False)
         else:
             self.play_button.setEnabled(False)
             self.pause_button.setEnabled(False)
             self.export_button.setEnabled(True)
             


         


    


        
        