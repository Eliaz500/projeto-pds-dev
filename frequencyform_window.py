from PyQt5.QtWidgets import QDialog, QVBoxLayout
import pyqtgraph as pg

class FrequencyPlotWindow(QDialog):
    """Janela para exibir os gráficos da FFT antes e depois do filtro"""
    def __init__(self, freqs, original_fft, filtered_fft):
        super().__init__()
        self.setWindowTitle("Espectro de Frequência - Filtro Passa-Baixa")
        self.setGeometry(200, 200, 800, 600)

        layout = QVBoxLayout()

        # Criando os gráficos
        self.plot_widget_before = pg.PlotWidget()
        self.plot_widget_before.setTitle("Frequências Originais")
        self.plot_widget_before.setLabel('left', 'Magnitude')
        self.plot_widget_before.setLabel('bottom', 'Frequência (Hz)')
        self.plot_widget_before.plot(freqs, original_fft, pen='r')

        self.plot_widget_after = pg.PlotWidget()
        self.plot_widget_after.setTitle("Frequências Após Passa-Baixa")
        self.plot_widget_after.setLabel('left', 'Magnitude')
        self.plot_widget_after.setLabel('bottom', 'Frequência (Hz)')
        self.plot_widget_after.plot(freqs, filtered_fft, pen='b')

        # Adiciona os gráficos à interface
        layout.addWidget(self.plot_widget_before)
        layout.addWidget(self.plot_widget_after)

        self.setLayout(layout)
