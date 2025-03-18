import numpy as np
import scipy.io.wavfile as wav


class AudioProcessor:
    """Classe para processar áudio e aplicar a FFT com filtro passa-baixa"""

    @staticmethod
    def low_pass_filter(file_path, cutoff_freq):
        """Aplica um filtro passa-baixa a um arquivo WAV e retorna a FFT antes e depois"""
        # Lê o arquivo de áudio
        sample_rate, audio_data = wav.read(file_path)

        # Se for estéreo, converte para mono pegando apenas um canal
        if len(audio_data.shape) > 1:
            audio_data = audio_data[:, 0]

        # Normaliza o áudio para o intervalo [-1, 1]
        audio_data = audio_data / np.max(np.abs(audio_data))

        # Aplica a FFT para converter para o domínio da frequência
        fft_data = np.fft.rfft(audio_data)
        freqs = np.fft.rfftfreq(len(audio_data), d=1 / sample_rate)

        # Obtém a magnitude antes do filtro
        original_fft = np.abs(fft_data)

        # Aplica o filtro passa-baixa
        fft_data[freqs > cutoff_freq] = 0  # Remove as frequências acima do corte

        # Obtém a magnitude depois do filtro
        filtered_fft = np.abs(fft_data)

        # Converte de volta para o domínio do tempo
        filtered_audio = np.fft.irfft(fft_data)

        # Normaliza novamente para o intervalo original
        filtered_audio = np.int16(filtered_audio / np.max(np.abs(filtered_audio)) * 32767)

        # Define o nome do arquivo de saída
        output_file = file_path.replace(".wav", "_LP.wav")

        # Salva o novo arquivo
        wav.write(output_file, sample_rate, filtered_audio)

        return output_file, freqs, original_fft, filtered_fft
