import numpy as np
import pyaudio
from PyQt5.QtCore import pyqtSignal, QThread


class AudioPlayer(QThread):
    """Thread responsável pela reprodução do áudio"""
    finished = pyqtSignal()
    paused = pyqtSignal()

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        self.is_paused = False
        self.current_position = 0  # Posição atual de leitura do arquivo
        self.chunk_size = 1024  # Tamanho do bloco de áudio a ser reproduzido
        self.rate = 44100  # Taxa de amostragem
        self.audio_data = None  # Atributo para armazenar os dados de áudio

    def run(self):
        """Reproduz o arquivo de áudio em um thread separado"""
        with open(self.file_path, 'rb') as f:
            self.audio_data = np.frombuffer(f.read(), dtype=np.int16)

        # Configurações de áudio
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=self.rate,
                        output=True)

        # Reproduz o arquivo em blocos, respeitando o estado de pausa
        while self.current_position < len(self.audio_data):
            if self.is_paused:
                self.paused.emit()
                while self.is_paused:  # Aguardar até ser retomado
                    QThread.msleep(100)
                self.paused.emit()

            chunk = self.audio_data[self.current_position:self.current_position + self.chunk_size]
            stream.write(chunk.tobytes())
            self.current_position += self.chunk_size

        stream.stop_stream()
        stream.close()
        p.terminate()

        # Emite o sinal indicando que a reprodução terminou
        self.finished.emit()

    def pause(self):
        """Pausa a reprodução"""
        self.is_paused = True

    def resume(self):
        """Retoma a reprodução"""
        self.is_paused = False

    def rewind(self, seconds=2):
        """Retrocede a reprodução em segundos sem reiniciar"""
        rewind_samples = int(seconds * self.rate)
        self.current_position = max(self.current_position - rewind_samples, 0)  # Retrocede 2 segundos

    def advance(self, seconds=2):
        """Avança a reprodução em segundos sem reiniciar"""
        if self.audio_data is None:  # Verifica se os dados de áudio estão carregados
            return

        advance_samples = int(seconds * self.rate)
        self.current_position = min(self.current_position + advance_samples, len(self.audio_data))  # Avança 2 segundos

    def reset(self):
        """Reseta a posição de leitura para o começo"""
        self.current_position = 0