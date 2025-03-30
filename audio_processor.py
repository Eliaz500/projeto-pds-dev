import numpy as np
import scipy.io.wavfile as wav
import torchaudio

class AudioProcessor:
    """Classe para processar áudio e aplicar a FFT com filtro passa-baixa"""

    @staticmethod
    def low_pass_filter(file_path, cutoff_freq):
        """Aplica um filtro passa-baixa a um arquivo de áudio (WAV ou MP3) e retorna a FFT antes e depois"""
        # Verifica se o arquivo é WAV ou MP3
        if file_path.endswith(".wav"):
            sample_rate, audio_data = wav.read(file_path)
        elif file_path.endswith(".mp3"):
            waveform, sample_rate = torchaudio.load(file_path)
            audio_data = waveform.numpy().flatten()  # Torna o áudio em 1D
        else:
            raise ValueError("Formato de arquivo não suportado. Use WAV ou MP3.")

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

        # Corrige o problema de audio duplicado em arquivos .mp3
        if file_path.endswith(".mp3"):
            filtered_audio = filtered_audio[:len(filtered_audio) // 2]

        # Define o nome do arquivo de saída
        output_file = file_path.replace(".wav", f"_{cutoff_freq}_LP.wav").replace(".mp3", f"_{cutoff_freq}_LP.wav")

        # Salva o novo arquivo
        wav.write(output_file, sample_rate, filtered_audio)

        return output_file, freqs, original_fft, filtered_fft

    @staticmethod
    def high_pass_filter(file_path, cutoff_freq):
        """Aplica um filtro passa-alta a um arquivo de áudio (WAV ou MP3) e retorna a FFT antes e depois"""
        # Verifica se o arquivo é WAV ou MP3
        if file_path.endswith(".wav"):
            sample_rate, audio_data = wav.read(file_path)
        elif file_path.endswith(".mp3"):
            waveform, sample_rate = torchaudio.load(file_path)
            audio_data = waveform.numpy().flatten()  # Torna o áudio em 1D
        else:
            raise ValueError("Formato de arquivo não suportado. Use WAV ou MP3.")

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

        # Aplica o filtro passa-alta
        fft_data[freqs < cutoff_freq] = 0  # Remove as frequências abaixo do corte

        # Obtém a magnitude depois do filtro
        filtered_fft = np.abs(fft_data)

        # Converte de volta para o domínio do tempo
        filtered_audio = np.fft.irfft(fft_data)

        # Normaliza novamente para o intervalo original
        filtered_audio = np.int16(filtered_audio / np.max(np.abs(filtered_audio)) * 32767)

        # Corrige o problema de audio duplicado em arquivos .mp3
        if file_path.endswith(".mp3"):
            filtered_audio = filtered_audio[:len(filtered_audio) // 2]

        # Define o nome do arquivo de saída
        output_file = file_path.replace(".wav", f"_{cutoff_freq}_HP.wav").replace(".mp3", f"_{cutoff_freq}_HP.wav")

        # Salva o novo arquivo
        wav.write(output_file, sample_rate, filtered_audio)

        return output_file, freqs, original_fft, filtered_fft

    @staticmethod
    def band_pass_filter(file_path, lowcut_freq, highcut_freq):
        """Aplica um filtro passa-faixa a um arquivo de áudio (WAV ou MP3) e retorna a FFT antes e depois"""
        # Verifica se o arquivo é WAV ou MP3
        if file_path.endswith(".wav"):
            sample_rate, audio_data = wav.read(file_path)
        elif file_path.endswith(".mp3"):
            waveform, sample_rate = torchaudio.load(file_path)
            audio_data = waveform.numpy().flatten()  # Torna o áudio em 1D
        else:
            raise ValueError("Formato de arquivo não suportado. Use WAV ou MP3.")

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

        # Aplica o filtro passa-faixa: mantém frequências entre lowcut_freq e highcut_freq
        fft_data[(freqs < lowcut_freq) | (freqs > highcut_freq)] = 0  # Zera frequências fora do intervalo

        # Obtém a magnitude depois do filtro
        filtered_fft = np.abs(fft_data)

        # Converte de volta para o domínio do tempo
        filtered_audio = np.fft.irfft(fft_data)

        # Normaliza novamente para o intervalo original
        filtered_audio = np.int16(filtered_audio / np.max(np.abs(filtered_audio)) * 32767)

        # Corrige o problema de audio duplicado em arquivos .mp3
        if file_path.endswith(".mp3"):
            filtered_audio = filtered_audio[:len(filtered_audio) // 2]

        # Define o nome do arquivo de saída
        output_file = file_path.replace(".wav", f"_{lowcut_freq}-{highcut_freq}_BP.wav").replace(".mp3", f"_{lowcut_freq}-{highcut_freq}_BP.wav")

        # Salva o novo arquivo
        wav.write(output_file, sample_rate, filtered_audio)

        return output_file, freqs, original_fft, filtered_fft
