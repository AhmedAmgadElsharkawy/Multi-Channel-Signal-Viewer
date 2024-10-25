from PyQt6.QtWidgets import QWidget,QHBoxLayout,QVBoxLayout,QPushButton,QRadioButton,QButtonGroup,QLabel,QComboBox
from PyQt6.QtGui import QIcon, QPixmap
import pyqtgraph as pg
from PyQt6.QtCore import QTimer
import requests
import numpy as np
import threading

import pyqtgraph.exporters as exporters
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Table, TableStyle
from reportlab.pdfgen import canvas
import os

from scipy.interpolate import interp1d, splrep, splev, BarycentricInterpolator
from numpy.polynomial import Polynomial
import math



def fetch_live_signal_async(callback):
    url = "https://rest.coinapi.io/v1/exchangerate/BTC/USD"
    headers = {
        'X-CoinAPI-Key': '34003F68-BA58-4C50-9D10-94C68C64FD5F',  
    }

    def run():
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                rate = float(data['rate'])  
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
        self.signal_color = 'g'  
        self.signal_label = "Live Bitcoin Price Signal"
        self.show_signal = True
        self.auto_scroll_enabled = True  
        self.snapshots_array = []
        self.snapshots_statistics_array = []

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_signal)
        self.full_signal_data = []  
        self.full_time_data = []   
        self.index = 0             
        self.window_size = 100      
        self.signals_overlap = False
        self.initUI()

        self.timer.start(self.fetching_rate)
 

    def initUI(self):
        main_layout = QHBoxLayout()

        self.glue_and_live_plot = pg.PlotWidget()
        self.glue_and_live_plot.showGrid(x = True,y = True)
        main_layout.addWidget(self.glue_and_live_plot)
        self.setFixedHeight(240)
        self.setFixedWidth(1200)

        self.controls_widget = QWidget()
        self.controls_widget_layout = QVBoxLayout()
        self.controls_widget.setLayout(self.controls_widget_layout)
        main_layout.addWidget(self.controls_widget)


        self.choose_signals_buttons_layout = QVBoxLayout()
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

        self.pause_icon = QIcon()
        self.play_icon = QIcon()
        export_icon = QIcon()
        self.pause_icon.addPixmap(QPixmap("Images/pause.png"))
        self.play_icon.addPixmap(QPixmap("Images/play.png"))
        export_icon.addPixmap(QPixmap("Images/export.png"))
        

        self.graph_controls_buttons_layout = QVBoxLayout()
        self.play_and_pause_button = QPushButton()
        self.play_and_pause_button.setFixedSize(77, 30)
        self.play_and_pause_button.setIcon(self.pause_icon)
        self.interpolation_order_combobox = QComboBox()
        self.interpolation_orders = [
            "Nearest",
            "Linear",
            "Polynomial",
            "Cubic",
            # "Barycentric"
        ]
        self.interpolation_order_combobox.setFixedWidth(77)
        self.interpolation_order_combobox.addItems(self.interpolation_orders)
        self.interpolation_order_combobox.setVisible(False)
        self.interpolation_order_combobox.currentIndexChanged.connect(self.interpolate_cropped_signals)
        self.lock_button = QPushButton("Lock")
        self.unlock_button = QPushButton("Unlock")
        self.snapshot_button = QPushButton("Snapshot")
        self.lock_button.clicked.connect(self.interpolate_cropped_signals)
        self.unlock_button.clicked.connect(self.unlock_cropped_signals)
        self.unlock_button.setVisible(False)
        self.lock_button.setVisible(False)
        self.snapshot_button.setVisible(False)
        self.export_button = QPushButton()
        self.export_button.setIcon(export_icon)
        self.graph_controls_buttons_layout.addWidget(self.play_and_pause_button)
        self.graph_controls_buttons_layout.addWidget(self.interpolation_order_combobox)
        self.graph_controls_buttons_layout.addWidget(self.lock_button)
        self.graph_controls_buttons_layout.addWidget(self.unlock_button)
        self.graph_controls_buttons_layout.addWidget(self.snapshot_button)
        self.graph_controls_buttons_layout.addWidget(self.export_button)
        self.controls_widget_layout.addLayout(self.graph_controls_buttons_layout)
        self.play_and_pause_button.clicked.connect(self.pause_signal)
        self.snapshot_button.clicked.connect(self.take_snapshot)
        self.export_button.clicked.connect(self.export_pdf)


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
            fetch_live_signal_async(self.process_new_price)

    def process_new_price(self, current_price):
        if current_price is not None:
            self.full_signal_data.append(current_price)
            self.full_time_data.append(self.index)
            self.index += 1
            self.live_curve.setData(self.full_time_data, self.full_signal_data)
            min_value = min(self.full_signal_data)
            max_value = max(self.full_signal_data)
            self.glue_and_live_plot.setLimits(yMin=min_value - 1, yMax=max_value + 1)
            self.glue_and_live_plot.setYRange(min_value-1,max_value+1)
            if(self.full_time_data[-1] < self.window_size):
                self.glue_and_live_plot.setLimits(xMax = self.window_size)
            else:
                self.glue_and_live_plot.setLimits(xMax = self.full_time_data[-1])
            if self.auto_scroll_enabled:
                if self.index > self.window_size:
                    self.glue_and_live_plot.setXRange(self.index - self.window_size, self.index)
                else:
                    self.glue_and_live_plot.setXRange(0, self.window_size)


    def on_manual_interaction(self, event):
        self.auto_scroll_enabled = False

    def on_range_change(self):
        if not self.auto_scroll_enabled:
            self.timer.singleShot(5000, self.reset_auto_scroll)  

    def reset_auto_scroll(self):
        self.auto_scroll_enabled = True
        if self.index > self.window_size:
            self.glue_and_live_plot.setXRange(self.index - self.window_size, self.index)

    def play_signal(self):
        self.play_and_pause_button.setIcon(self.pause_icon)
        self.play_and_pause_button.clicked.connect(self.pause_signal)
        self.is_paused = False
        self.is_rewind = False
        self.timer.start(self.fetching_rate)

    def pause_signal(self):
        self.play_and_pause_button.setIcon(self.play_icon)
        self.play_and_pause_button.clicked.connect(self.play_signal)
        self.is_paused = True
        self.timer.stop()

        

    def plot_cropped_signals(self,x1,y1,x2,y2,color1,color2):
         self.lock_button.setVisible(True)
         self.interpolation_order_combobox.setVisible(False)
         self.unlock_button.setVisible(False)
         self.play_and_pause_button.setVisible(False)
         self.export_button.setVisible(False)
         self.pause_signal()
         self.cropped_signal_curve1.setData(x1,y1)   
         self.cropped_signal_curve2.setData(x2,y2)
         self.cropped_signal_curve1.setPen(pg.mkPen(color=color1))
         self.cropped_signal_curve2.setPen(pg.mkPen(color=color2))
         self.fixed_width1 = x1[-1] - x1[0]
         self.fixed_width2 = x2[-1] - x2[0]
         self.linear_region1.setRegion([x1[0], x1[-1]])  
         self.linear_region2.setRegion([x2[0], x2[-1]])  

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
         

         self.glue_and_live_plot.setLimits(xMin=0,xMax = None)
         self.glue_and_live_plot.setLimits(yMin = -2 , yMax = 2)
         self.glue_and_live_plot.setXRange(min_xrange,max_xrange)
         self.glue_and_live_plot.setYRange(-1,1)


    def open_glue_signal(self):
        self.timer.stop()
        self.glue_and_live_plot.removeItem(self.live_curve)
        self.glue_and_live_plot.removeItem(self.glue_output_curve)
        self.glue_and_live_plot.addItem(self.glue_output_curve)
        if (self.glue_output_curve.getData()[0]) is not None:
            self.glue_and_live_plot.setXRange(self.glue_output_curve.getData()[0][0],self.glue_output_curve.getData()[0][-1])
            self.glue_and_live_plot.setLimits(xMin = max(0,self.glue_output_curve.getData()[0][0]),xMax = self.glue_output_curve.getData()[0][-1])
            self.glue_and_live_plot.setYRange(min(self.glue_output_curve.getData()[1]),max(self.glue_output_curve.getData()[1]))
            self.glue_and_live_plot.setLimits(yMin = min(self.glue_output_curve.getData()[1]),yMax = max(self.glue_output_curve.getData()[1]))
        else:
            self.glue_and_live_plot.setXRange(0,1)
            self.glue_and_live_plot.setLimits(xMin = 0,xMax = 1)
            self.glue_and_live_plot.setYRange(-1,1)
            self.glue_and_live_plot.setLimits(yMin = -2,yMax = 2)
        self.enable_controls()

    def run_live_signal(self):
        self.play_signal()
        self.glue_and_live_plot.removeItem(self.glue_output_curve)
        self.glue_and_live_plot.removeItem(self.live_curve)
        self.glue_and_live_plot.addItem(self.live_curve)
        if len(self.full_time_data) != 0:
            self.glue_and_live_plot.setLimits(xMin = 0,xMax = max(self.full_time_data[-1],self.window_size),yMin = min(self.full_signal_data)-1,yMax= max(self.full_signal_data)+1)
            self.glue_and_live_plot.setYRange(min(self.full_signal_data)-1,max(self.full_signal_data)+1)
            if self.full_time_data[-1] >= self.window_size:
                self.glue_and_live_plot.setXRange(self.full_time_data[-1] - self.window_size ,self.full_time_data[-1])
            else:
                self.glue_and_live_plot.setXRange(0,self.window_size)
        else:
            self.glue_and_live_plot.setLimits(xMin = 0,xMax = self.window_size,yMin = -2,yMax= 2)
            self.glue_and_live_plot.setYRange(-1,1)
            self.glue_and_live_plot.setXRange(0,self.window_size)   
        self.glue_and_live_plot.setLimits(xMin=0)
        self.play_signal()
        self.enable_controls()


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

    def enable_controls(self):
         self.live_radio_button.setEnabled(True)
         self.glue_radio_button.setEnabled(True)
         if self.live_radio_button.isChecked():
            self.export_button.setVisible(False)
            self.interpolation_order_combobox.setVisible(False)
            self.unlock_button.setVisible(False)
            self.lock_button.setVisible(False)
            self.snapshot_button.setVisible(False)
            self.play_and_pause_button.setVisible(True)
         else:
             self.lock_button.setVisible(False)
             self.play_and_pause_button.setVisible(False) 
             if(self.glue_output_curve.getData()[0] is not None):
                self.export_button.setVisible(True)
                self.snapshot_button.setVisible(True)

                self.unlock_button.setVisible(True)
                if(not self.signals_overlap):
                    self.interpolation_order_combobox.setVisible(True)

    def interpolate_cropped_signals(self):
        interpolate_order = self.interpolation_orders[self.interpolation_order_combobox.currentIndex()]
        self.cropped_signal1_data = self.cropped_signal_curve1.getData()
        self.cropped_signal2_data = self.cropped_signal_curve2.getData()

        signal1_x = np.array(self.cropped_signal1_data[0])
        signal1_y = np.array(self.cropped_signal1_data[1])
        signal2_x = np.array(self.cropped_signal2_data[0])
        signal2_y = np.array(self.cropped_signal2_data[1])

        gap1 = signal2_x[0] - signal1_x[-1]
        gap2 = signal1_x[0] - signal2_x[-1]

        if gap1 == 0:
            self.signals_overlap = True
            interpolate_x = np.concatenate([signal1_x, signal2_x])
            interpolate_y = np.concatenate([signal1_y, signal2_y])
        elif gap1 < 0 and gap2 < 0:
            self.signals_overlap = True
            intersection_start = max(signal1_x[0], signal2_x[0])
            intersection_end = min(signal1_x[-1], signal2_x[-1])

            intersection_mask1 = (np.ceil(signal1_x*1000)/1000 >= intersection_start) & (np.ceil(signal1_x*1000)/1000 <= intersection_end)
            intersection_mask2 = (np.ceil(signal2_x*1000)/1000 >= intersection_start) & (np.ceil(signal2_x*1000)/1000 <= intersection_end)
            
            intersection_signal1_x = np.ceil(signal1_x[intersection_mask1]*1000)/1000
            intersection_signal1_y = signal1_y[intersection_mask1]
            intersection_signal2_x = np.ceil(signal2_x[intersection_mask2]*1000)/1000
            intersection_signal2_y = signal2_y[intersection_mask2]

            unique_signal1_x = np.setdiff1d(intersection_signal1_x, intersection_signal2_x)
            unique_signal2_x = np.setdiff1d(intersection_signal2_x, intersection_signal1_x)

            unique_signal1_y = intersection_signal1_y[np.isin(intersection_signal1_x, unique_signal1_x)]
            unique_signal2_y = intersection_signal2_y[np.isin(intersection_signal2_x, unique_signal2_x)]

            common_x = np.intersect1d(intersection_signal1_x, intersection_signal2_x)

            sum_y_values = []
            for x in common_x:
                y1 = intersection_signal1_y[intersection_signal1_x == x][0]
                y2 = intersection_signal2_y[intersection_signal2_x == x][0]
                sum_y = (y1 + y2)/2
                sum_y_values.append([x, sum_y])

            interpolate_x = np.array([pair[0] for pair in sum_y_values])
            interpolate_y = np.array([pair[1] for pair in sum_y_values])

            signal1_outside_mask = (signal1_x < intersection_start) | (signal1_x > intersection_end)
            interpolate_x = np.concatenate([interpolate_x, signal1_x[signal1_outside_mask], unique_signal1_x])
            interpolate_y = np.concatenate([interpolate_y, signal1_y[signal1_outside_mask], unique_signal1_y])

            signal2_outside_mask = (signal2_x < intersection_start) | (signal2_x > intersection_end)
            interpolate_x = np.concatenate([interpolate_x, signal2_x[signal2_outside_mask], unique_signal2_x])
            interpolate_y = np.concatenate([interpolate_y, signal2_y[signal2_outside_mask], unique_signal2_y])

            sorted_indices = np.argsort(interpolate_x)
            interpolate_x = interpolate_x[sorted_indices]
            interpolate_y = interpolate_y[sorted_indices]
        else:
            self.signals_overlap = False
            if gap1 > 0:
                combined_x = np.concatenate([signal1_x, signal2_x])
                combined_y = np.concatenate([signal1_y, signal2_y])
                gap_x = np.linspace(signal1_x[-1], signal2_x[0], num=math.ceil(gap1*1000))  
            else:
                combined_x = np.concatenate([signal2_x, signal1_x])
                combined_y = np.concatenate([signal2_y, signal1_y])
                gap_x = np.linspace(signal2_x[-1], signal1_x[0], num=math.ceil(gap2*1000))  

                

            if interpolate_order == 'Linear':
                f = interp1d(combined_x, combined_y, kind='linear', fill_value="extrapolate")
            elif interpolate_order == 'Cubic':
                f = interp1d(combined_x, combined_y, kind='cubic', fill_value="extrapolate")
            # elif interpolate_order == 'Barycentric':
            #     f = BarycentricInterpolator(combined_x, combined_y)
            elif interpolate_order == 'Nearest':
                f = interp1d(combined_x, combined_y, kind='nearest', fill_value="extrapolate")
            elif interpolate_order == 'Polynomial':
                degree = min(len(combined_x) - 1, 3) 
                coefficients = Polynomial.fit(combined_x, combined_y, degree)
                f = lambda x: coefficients(x)
            gap_y = f(gap_x)
            if(gap1>0):
                interpolate_x = np.concatenate([signal1_x, gap_x, signal2_x])
                interpolate_y = np.concatenate([signal1_y, gap_y, signal2_y])
            else:
                interpolate_x = np.concatenate([signal2_x, gap_x, signal1_x])
                interpolate_y = np.concatenate([signal2_y, gap_y, signal1_y])
            

        self.glue_and_live_plot.clear()
        self.glue_output_curve.setData(interpolate_x, interpolate_y)
        self.glue_radio_button.blockSignals(True)
        self.glue_radio_button.setChecked(True)
        self.glue_radio_button.blockSignals(False)
        self.open_glue_signal()
             

    def unlock_cropped_signals(self):
        x1 = self.cropped_signal_curve1.getData()[0]
        y1 = self.cropped_signal_curve1.getData()[1]
        x2 = self.cropped_signal_curve2.getData()[0]
        y2 = self.cropped_signal_curve2.getData()[1]
        pen1 = self.cropped_signal_curve1.opts['pen']
        pen2 = self.cropped_signal_curve2.opts['pen']
        color1 = pen1.color().name()
        color2 = pen2.color().name()
        self.plot_cropped_signals(x1,y1,x2,y2,color1,color2)
        self.disable_controls()
        self.lock_button.setVisible(True)

    def take_snapshot(self):
        left_x_pos, right_x_pos = self.glue_and_live_plot.getViewBox().viewRange()[0]   
        glue_x_data, glue_y_data = self.glue_output_curve.getData()
        snapshot_data = [[], []]

        for i in range(len(glue_x_data)):
            if glue_x_data[i] >= left_x_pos and glue_x_data[i] <= right_x_pos:
                snapshot_data[1].append(glue_y_data[i])
        
        snapshot_statistics = self.calculate_signal_statistics(snapshot_data)
        self.snapshots_statistics_array.append(snapshot_statistics)

        snapshot = exporters.ImageExporter(self.glue_and_live_plot.scene())
        snapshot.params.fileSuffix = 'png'
        curr_image_num = str(len(self.snapshots_array) + 1)
        snapshot_filename = "snapshot" + curr_image_num + ".png"
        self.snapshots_array.append(snapshot_filename)
        snapshot.export(snapshot_filename)

    def export_pdf(self):
        # Create a PDF
        file_name = "report.pdf"
        pdf = canvas.Canvas(file_name, pagesize=letter)
        pdf.setFont("Helvetica", 24)

        # Add header text
        pdf.drawCentredString(320, 670, "Cairo University")
        pdf.drawCentredString(320, 620, "Multi-Channel-Viewer Report")

        majorLogoPath = './Images/logo-major.png'
        collegeLogoPath = './Images/collegeLogo.jpg'
        
        major_logo = ImageReader(majorLogoPath)
        college_logo = ImageReader(collegeLogoPath)
          
        # Add logos to the PDF
        pdf.drawImage(major_logo, 10, 725, width=112, height=45)
        pdf.drawImage(college_logo, 525, 705, width=70, height=70)

        curr_pos = 360

        for i in range(len(self.snapshots_array)):
            curr_img_file = Image.open(self.snapshots_array[i])
            curr_img = ImageReader(curr_img_file)
            pdf.drawImage(curr_img, 10, curr_pos, width=590, height=150)
            os.remove(self.snapshots_array[i])
            if i == 0:
                curr_pos -= 200
            else :
                curr_pos -= 250
            data = [['Statistic', 'Value']]
            stats_items = list(self.snapshots_statistics_array[i].items())
            for i in range(0, len(stats_items)):
                pdf.setFont("Helvetica", 24)
                pdf.drawCentredString(320, curr_pos + 120, "Graph Statistics")
                row = []
                for j in range(1):
                    if i + j < len(stats_items):
                        row.append(stats_items[i + j][0])
                        row.append(str(stats_items[i + j][1]))
                    else:
                        row.append('') 
                        row.append('')
                data.append(row)
                col_widths = [200, 200]
                table = Table(data, colWidths=col_widths)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12), 
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige), 
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
            table.wrapOn(pdf, 400, 400)
            table.drawOn(pdf, 120, curr_pos)
            if i + 1 != len(self.snapshots_array):
                pdf.showPage()
                curr_pos = 400


        pdf.save()
        self.snapshots_array.clear()



    def calculate_signal_statistics(self, signal):
        """Calculate mean, std, duration, min, and max values for the signal."""
        mean_value = np.mean(signal[1])
        std_value = np.std(signal[1])
        min_value = np.min(signal[1])
        max_value = np.max(signal[1])
        
        return {
            "mean": mean_value,
            "std": std_value,
            "min": min_value,
            "max": max_value
        }
