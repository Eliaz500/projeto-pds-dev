import pyaudio
import os


class AudioRecorder:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.recording = False
        self.recorded_data = []

    def start_recording(self, device_index):
        """Inicia a gravação e armazena os dados"""
        if device_index is None:
            return  # Nenhum dispositivo selecionado

        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1, # Utilizando um canal de áudio
            rate=44100, # Taxa de amostragem de 44.1Khz
            input=True,
            frames_per_buffer=1024,
            input_device_index=device_index
        )

        self.recording = True
        self.recorded_data = []  # Limpa dados gravados anteriores

    def stop_recording(self):
        """Para a gravação e salva os dados"""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()

        self.recording = False

        # Salva a gravação em um arquivo na pasta "records"
        if not os.path.exists("records"):
            os.makedirs("records")

        filename = f"records/recorded_{len(os.listdir('records')) + 1}.raw"
        with open(filename, 'wb') as f:
            for chunk in self.recorded_data:
                f.write(chunk)

    def update_recording(self):
        """Captura dados e os armazena durante a gravação"""
        if not self.recording or not self.stream:
            return None

        data = self.stream.read(1024, exception_on_overflow=False)
        self.recorded_data.append(data)

        return data

    def close(self):
        """Fecha o stream e termina a instância"""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.audio.terminate()
