import sys
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer, pyqtSlot
import wave


class WaveformWindow(QMainWindow):
    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.initUI()
        self.load_waveform()
        self.current_position = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_position)

    def initUI(self):
        self.setWindowTitle(self.file_path)
        self.setGeometry(150, 150, 800, 400)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout()
        self.plot_widget = pg.PlotWidget()
        layout.addWidget(self.plot_widget)
        self.central_widget.setLayout(layout)

        self.waveform_curve = self.plot_widget.plot(pen='b')
        self.position_marker = self.plot_widget.plot(pen='r', symbol='o', symbolBrush='r')

    def load_waveform(self):
        with wave.open(self.file_path, 'rb') as wf:
            self.rate = wf.getframerate()
            self.audio_data = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
            self.audio_data = self.audio_data / np.max(np.abs(self.audio_data))  # Normaliza

        duration = len(self.audio_data) / self.rate
        self.time_axis = np.linspace(0, duration, num=len(self.audio_data))
        self.waveform_curve.setData(self.time_axis, self.audio_data)

        self.plot_widget.setLabel('bottom', 'Time (s)')
        self.plot_widget.setLabel('left', 'Amplitude')
        self.plot_widget.setXRange(0, duration)
        self.plot_widget.setYRange(-1, 1)

    def start_tracking(self):
        self.current_position = 0
        self.timer.start(1000)

    def update_position(self):
        if self.current_position < len(self.time_axis):
            self.position_marker.setData([self.time_axis[self.current_position]],
                                         [self.audio_data[self.current_position]])
            self.current_position += self.rate  # Atualiza a cada segundo
        else:
            self.timer.stop()

    @pyqtSlot(float)
    def update_pointer(self, current_time):
        """Atualiza o ponteiro na waveform de acordo com o tempo de reprodução"""
        if current_time <= self.time_axis[-1]:
            self.position_marker.setData([current_time], [0])  # Atualiza a posição do marcador

    def closeEvent(self, event):
        self.timer.stop()
        event.accept()