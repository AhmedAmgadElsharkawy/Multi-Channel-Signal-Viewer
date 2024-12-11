# Multi-Channel Signal Viewer

## Table of Contents

- [Introduction](#introduction)
- [Live Demo](#live-demo)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)

---

## Introduction

A desktop app that provides real-time visualization and allows users to load and visualize signal files (e.g., ECG, EEG), built with PyQt.

## Live Demo

## Features

- **Multi Channel**: You can browse your PC to open multiple signal files in more than one port.

- **Linking Graphs**: The application contains two main identical graphs, where you can control each one of them by his controls, you can also link the two graphs with one controller.

- **Cine Mode**: Signals are displayed in cine mode, similar to ICU monitors. You can rewind a signal if it ends.

- **Signal Controls**: The user can change color, add labels, show/hide, customize cine speed, zoom in/out, pause/play/rewind, and scroll/pan the signal in any direction.

- **Signal Transfer**: You can move signals from one graph to the other.

- **Glue Signals**: Where you can crop important parts of the two signals, and glut them with different interpolation methods, for better understanding of the signals.

- **Radar Viewer**: you can upload any signal and show it on the radar viewer where you can get a better view of the signal features that can't be seen in the normal graph.

- **Radar Controllers**: The user can pause/play/rewind, and customize cine speed of the radar.

- **Exporting & Reporting**: You can generate a report with snapshots of the  two graphs, and the Glue graph, with showing of the data statistics on the displayed signals, exported to a PDF file. The report includes mean, standard deviation, duration, minimum, and maximum values for each signal.
## Prerequisites

- Python 3.6 or higher

## Installation

1. **Clone the repository:**

   ``````
   git clone https://github.com/AhmedAmgadElsharkawy/Multi-Channel-Signal-Viewer.git
   ``````
2. **Navigate into the project directory:**  

    ``````
    cd Multi-Channel-Signal-Viewer
    ``````
3. **Create Virtual Environment:**  

    ``````
    python -m venv signal_viewer_venv
    ``````

4. **Activate The Virtual Environment:**
    ``````
    signal_viewer_venv\Scripts\activate
    ``````

5. **Install The Dependincies:**
    ``````
    pip install -r requirements.txt
    ``````

6. **Run The App:**

    ``````
    python main.py
## Contributors

<table>
  <tr>
    <td align="center">
    <a href="https://github.com/AbdullahMahmoudHanafy" target="_black">
    <img src="https://avatars.githubusercontent.com/u/116839669?v=4" width="150px;" alt="Youssef Ashraf"/>
    <br />
    <sub><b>ِAbdullah Mahmoud</b></sub></a>
    </td>
    <td align="center">
    <a href="https://github.com/AhmedAmgadElsharkawy" target="_black">
    <img src="https://avatars.githubusercontent.com/u/110942407?v=4" width="150px;" alt="Mourad Magdy"/>
    <br />
    <sub><b>Ahmed Amgad</b></sub></a>
    <td align="center">
    <a href="https://github.com/MohamadAhmedAli" target="_black">
    <img src="https://avatars.githubusercontent.com/u/112741669?v=4" width="150px;" alt="Ziad Meligy"/>
    <br />
    <sub><b>Mohamed Ahmed</b></sub></a>
    </td>
    </td>
      </tr>
 </table>