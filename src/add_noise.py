import numpy as np
from pydub import AudioSegment

def read_mp3(file_path):
    audio = AudioSegment.from_file(file_path, format="mp3")
    signal = np.array(audio.get_array_of_samples())
    return signal, audio.frame_rate

def write_mp3(file_path, signal, frame_rate):
    audio = AudioSegment(signal.tobytes(), frame_rate=frame_rate, sample_width=2, channels=1)
    audio.export(file_path, format="mp3")

def add_noise_to_audio(input_file, output_file, SNR_dB):
    # Read the input audio file
    input_signal, frame_rate = read_mp3(input_file)

    # Convert SNR from dB to linear scale
    SNR = 10**(SNR_dB / 10)

    # Generate random numbers u and v
    u = np.random.randn(len(input_signal))
    v = np.random.randn(len(input_signal))

    # Calculate r
    r = u**2 + v**2

    # Calculate s, ensuring that the values are not negative or zero
    s = np.sqrt(np.maximum(0, -2 * np.log(r) / r))

    # Generate normally distributed noise
    x = u * s
    y = v * s

    # Adjust noise power to achieve the desired SNR
    noise_power = np.sqrt(np.maximum(0, np.var(input_signal) / SNR))
    x *= noise_power
    y *= noise_power

    # Add noise to the input audio signal
    noisy_signal = input_signal + x + 1j * y

    # Ensure that the values are finite before casting to int16
    noisy_signal = np.real(noisy_signal)
    noisy_signal[np.isnan(noisy_signal)] = 0  # Replace NaN with 0
    noisy_signal[np.isinf(noisy_signal)] = 0  # Replace Inf with 0

    # Write the noisy audio as a new MP3 file
    write_mp3(output_file, noisy_signal.astype(np.int16), frame_rate)

if __name__ == "__main__":
    input_file = "input_audio.mp3"
    output_file = "noisy_output_audio.mp3"
    SNR_dB = 5.0

    add_noise_to_audio(input_file, output_file, SNR_dB)
