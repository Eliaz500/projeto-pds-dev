import wave
import pyaudio
import os
from PyQt5.QtCore import QThread, pyqtSignal


class AudioRecorder(QThread):
    """Classe de gravação de áudio em um thread separado"""
    update_signal = pyqtSignal(bytes)  # Signal para enviar dados gravados para o GUI
    finished_signal = pyqtSignal()  # Signal quando a gravação terminar

    def __init__(self, filename="output.wav"):
        super().__init__()
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.recording = False
        self.filename = filename
        self.frames = []  # Lista para armazenar os frames de áudio

        # Parâmetros de gravação
        self.chunk = 1024  # Tamanho do bloco de áudio (1024 amostras por vez)
        self.sample_format = pyaudio.paInt16  # Formato de amostra (16 bits por amostra)
        self.channels = 1  # Número de canais (mono)
        self.fs = 44100  # Taxa de amostragem (44100 Hz)

    def start_recording(self, device_index=None):
        """Inicia a gravação em um thread separado"""
        if self.recording:
            return  # Já está gravando

        # Inicia o stream de áudio
        self.stream = self.audio.open(format=self.sample_format,
                                      channels=self.channels,
                                      rate=self.fs,
                                      frames_per_buffer=self.chunk,
                                      input=True,
                                      input_device_index=device_index)

        self.recording = True
        self.frames = []  # Limpa os frames anteriores

        print("Recording started...")
        self.start()  # Inicia o thread de gravação

    def run(self):
        """Método do thread que realiza a gravação"""
        while self.recording:
            data = self.stream.read(self.chunk, exception_on_overflow=False)
            self.frames.append(data)
            self.update_signal.emit(data)  # Envia os dados para o GUI, se necessário

        self.stop_recording()  # Para a gravação ao terminar

    def stop_recording(self):
        """Para a gravação e salva os dados"""
        if not self.recording:
            return  # Não está gravando

        self.recording = False

        # Para o stream de áudio
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()

        # Salva os dados gravados em um arquivo WAV
        if not os.path.exists("records"):
            os.makedirs("records")

        filename = f"records/recorded_{len(os.listdir('records')) + 1}.wav"
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.audio.get_sample_size(self.sample_format))
            wf.setframerate(self.fs)
            wf.writeframes(b''.join(self.frames))

        print(f"Gravação salva em {filename}")
        self.finished_signal.emit()  # Emite o sinal indicando que a gravação terminou

    def close(self):
        """Fecha o stream e termina a instância"""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.audio.terminate()
