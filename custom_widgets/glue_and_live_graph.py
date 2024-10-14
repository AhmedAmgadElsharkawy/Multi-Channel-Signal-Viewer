from PyQt6.QtWidgets import QWidget,QHBoxLayout,QVBoxLayout,QPushButton,QRadioButton,QButtonGroup,QLabel
import pyqtgraph as pg
from scipy.interpolate import interp1d
from PyQt6.QtCore import Qt,QTimer
import requests
import numpy as np
import pyqtgraph.exporters as exporters
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Table, TableStyle
from reportlab.pdfgen import canvas
import os


def fetch_live_signal():
        url = "https://quantifycrypto.com/api/v1/general/currencies"
        headers = {
            'QC-Access-Key': 'DWD5OZ2AT831T18DHXOM',
            'QC-Secret-Key': 'aXhLbgAROtwAXZZ9UyUFNaKHDGVcClR2YNCDwa9rE0YiDCmv',
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            values = [float(currency['conv_rate']) for currency in data['data']] 
            return values
        else:
            print("Error fetching data:", response.status_code, response.text)
            return np.random.normal(size=100)  



class GlueAndLiveGraph(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        # self.is_paused = False
        # self.is_rewind = False
        # self.signal_color = 'g'  # the Default color i used (there are other 4 colors)
        # self.signal_label = "Live Signal"
        # self.show_signal = True
        # self.timer = QTimer(self) ######################################################
        # self.timer.timeout.connect(self.update_signal) 
        # self.signal_data = fetch_live_signal()
        # self.index = 0
        # self.update_signal()
        # self.timer.start(200)  # Set the update rate (u can use higher number for slower update)
 

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
        self.export_button.clicked.connect(self.export_pdf)

        self.live_radio_button.setChecked(True)


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


        
        
        self.setLayout(main_layout)

        self.setStyleSheet("""
            QPushButton{
                padding:5px 20px
            }
        """)


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
        self.glue_and_live_plot.clear()
        self.glue_and_live_plot.addItem(self.glue_output_curve)
        
        if (self.glue_output_curve.getData()[0]) is not None:
            self.glue_and_live_plot.setXRange(self.glue_output_curve.getData()[0][0],self.glue_output_curve.getData()[0][-1])
        self.export_button.setEnabled(True)
        self.play_button.setEnabled(False)
        self.pause_button.setEnabled(False)

    def run_live_signal(self):
        self.glue_and_live_plot.clear()
        self.export_button.setEnabled(False)
        self.play_button.setEnabled(True)
        self.pause_button.setEnabled(True)


        
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
         self.play_button.setEnabled(True)
         self.pause_button.setEnabled(True)
         self.export_button.setEnabled(True)

         
#     from reportlab.lib.pagesizes import letter
# from reportlab.pdfgen import canvas
# from reportlab.lib.utils import ImageReader
# from PyQt5.QtGui import QImage
# from PIL import Image
# import exporters  # Assuming this is a valid module or PyQtGraph exporter

    def export_pdf(self):
        # Export graph as image
        exporter = exporters.ImageExporter(self.glue_and_live_plot.scene())
        exporter.params.fileSuffix = 'png'
        export_filename = "img.png"
        exporter.export(export_filename)

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

        glue_img_name = Image.open(export_filename)
        glue_img = ImageReader(glue_img_name) 
        pdf.drawImage(glue_img, 10, 350, width=590, height=150) 

        signal_stats = self.calculate_signal_statistics(self.glue_output_curve.getData())

        data = [['Statistic', 'Value']]
        stats_items = list(signal_stats.items())

        for i in range(0, len(stats_items)):
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

        pdf.drawCentredString(320, 530, "Glue graph")

        pdf.drawCentredString(320, 220, "Statistics for the glue graph")

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
        table.drawOn(pdf, 120, 100) 

        pdf.save()

        os.remove(export_filename)

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
        
        