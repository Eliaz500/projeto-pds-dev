import sys
import numpy as np
import pyqtgraph as pg
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QComboBox, QFileDialog
from audio_player import AudioPlayer  # Importa o reprodutor de som
from audio_recorder import AudioRecorder  # Importa o gravador de som


class MediaPlayerUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.initAudio()

    def initUI(self):
        """Inicializa a interface gráfica"""
        main_layout = QVBoxLayout()
        button_layout = QHBoxLayout()

        # Botões principais com ícones e tooltips
        self.record_button = QPushButton()
        self.record_button.setIcon(QIcon('icons/record.png'))
        self.record_button.setToolTip('Gravar')
        self.record_button.clicked.connect(self.toggle_recording)

        self.play_button = QPushButton()
        self.play_button.setIcon(QIcon('icons/play.png'))
        self.play_button.setToolTip('Reproduzir')
        self.play_button.clicked.connect(self.play_audio)

        self.pause_button = QPushButton()
        self.pause_button.setIcon(QIcon('icons/pause.png'))
        self.pause_button.setToolTip('Pausar')
        self.pause_button.clicked.connect(self.toggle_pause)

        self.forward_button = QPushButton()
        self.forward_button.setIcon(QIcon('icons/forward.png'))
        self.forward_button.setToolTip('Avançar 2x')
        self.forward_button.clicked.connect(self.advance_audio)  # Lida com o avanço

        self.rewind_button = QPushButton()
        self.rewind_button.setIcon(QIcon('icons/rewind.png'))
        self.rewind_button.setToolTip('Retornar 2x')
        self.rewind_button.clicked.connect(self.rewind_audio)  # Lida com o retrocesso

        # Botões de filtros com ícones e tooltips
        self.low_pass_button = QPushButton()
        self.low_pass_button.setIcon(QIcon('icons/low_pass.png'))
        self.low_pass_button.setToolTip('Filtro Passa-Baixa')

        self.high_pass_button = QPushButton()
        self.high_pass_button.setIcon(QIcon('icons/high_pass.png'))
        self.high_pass_button.setToolTip('Filtro Passa-Alta')

        self.band_pass_button = QPushButton()
        self.band_pass_button.setIcon(QIcon('icons/band_pass.png'))
        self.band_pass_button.setToolTip('Filtro Passa-Faixa')

        # Adicionando botões ao layout
        for button in [self.record_button, self.play_button, self.pause_button,
                       self.forward_button, self.rewind_button, self.low_pass_button,
                       self.high_pass_button, self.band_pass_button]:
            button_layout.addWidget(button)

        # Lista de dispositivos de entrada (microfones)
        self.device_selector = QComboBox()
        self.device_selector.setToolTip("Selecione o dispositivo de gravação")
        main_layout.addWidget(self.device_selector)

        # Criando a área do gráfico de espectro
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setTitle("Frequências em Tempo Real")
        self.plot_widget.setLabel('left', 'Amplitude')
        self.plot_widget.setLabel('bottom', 'Frequência (Hz)')
        self.plot_widget.setYRange(0, 1, padding=0)
        main_layout.addWidget(self.plot_widget)

        self.fft_curve = self.plot_widget.plot(pen='c')  # Linha azul no gráfico

        # Adiciona os layouts à interface
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)
        self.setWindowTitle('Media Player')
        self.setGeometry(100, 100, 600, 300)

    def initAudio(self):
        """Inicializa a configuração de áudio e lista apenas dispositivos de entrada"""
        self.recorder = AudioRecorder()  # Instância do AudioRecorder
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)

        # Lista apenas dispositivos de ENTRADA (microfones)
        for i in range(self.recorder.audio.get_device_count()):
            device_info = self.recorder.audio.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:  # Filtra apenas microfones
                self.device_selector.addItem(device_info['name'], i)

        # Inicializa a variável que controla a reprodução
        self.is_playing = False

    def toggle_recording(self):
        """Inicia ou para a gravação"""
        if self.recorder.recording:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        """Inicia a gravação e atualização do gráfico"""
        selected_device_index = self.device_selector.currentData()
        if selected_device_index is None:
            return  # Nenhum dispositivo selecionado

        self.recorder.start_recording(selected_device_index)

        # Desativa a escolha de dispositivos
        self.device_selector.setDisabled(True)

        self.timer.start(50)  # Atualiza o gráfico a cada 50ms

    def stop_recording(self):
        """Para a gravação, fecha o stream e salva o arquivo"""
        self.recorder.stop_recording()

        # Reabilita a seleção de dispositivo
        self.device_selector.setEnabled(True)

    def update_plot(self):
        """Atualiza o gráfico de frequência durante a gravação"""
        data = self.recorder.update_recording()
        if data is None:
            return

        audio_data = np.frombuffer(data, dtype=np.int16)
        fft_data = np.abs(np.fft.rfft(audio_data))  # Aplica FFT
        fft_data = fft_data / np.max(fft_data)  # Normaliza os valores

        frequencies = np.fft.rfftfreq(len(audio_data), 1 / 44100)  # Eixo X (frequências)

        self.fft_curve.setData(frequencies, fft_data)  # Atualiza o gráfico

    def play_audio(self):
        """Permite ao usuário selecionar e reproduzir um arquivo de áudio"""
        if self.is_playing:
            return  # Não permite iniciar a reprodução se já estiver em andamento

        options = QFileDialog.Options()
        file, _ = QFileDialog.getOpenFileName(self, "Abrir Arquivo de Áudio", "", "Arquivos Raw (*.raw)",
                                              options=options)

        if file:
            self.play_audio_file(file)

    def play_audio_file(self, file):
        """Inicia a reprodução do áudio em um thread separado"""
        self.is_playing = True
        self.play_button.setEnabled(False)  # Desabilita o botão de reproduzir enquanto o áudio toca
        self.player_thread = AudioPlayer(file)
        self.player_thread.finished.connect(self.on_audio_finished)
        self.player_thread.start()

    def toggle_pause(self):
        """Pausa ou retoma a reprodução do áudio"""
        if self.is_playing:
            if self.player_thread.is_paused:
                self.player_thread.resume()  # Retoma a reprodução
                print("Reprodução despausada")
            else:
                self.player_thread.pause()  # Pausa a reprodução
                print("Reprodução pausada")

    def rewind_audio(self):
        """Retorna 2 segundos na reprodução"""
        if self.is_playing:
            self.player_thread.rewind(2)  # Retrocede 2 segundos
            print("Retrocedeu a reprodução em 2 segundos")

    def advance_audio(self):
        """Avança 2 segundos na reprodução"""
        if self.is_playing:
            self.player_thread.advance(2)  # Avança 2 segundos
            print("Avançou a reprodução em 2 segundos")

    def on_audio_finished(self):
        """Chama quando a reprodução do áudio for finalizada"""
        self.is_playing = False
        self.play_button.setEnabled(True)  # Reabilita o botão de reproduzir
        print("Reprodução finalizada")

    def closeEvent(self, event):
        """Garante que o áudio seja encerrado ao fechar a janela"""
        self.recorder.close()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = MediaPlayerUI()
    player.show()
    sys.exit(app.exec_())
