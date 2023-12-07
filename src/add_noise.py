import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from functools import partial
import os
import numpy as np
from pydub import AudioSegment

def read_mp3(file_path):
    audio = AudioSegment.from_file(file_path, format="mp3")
    signal = np.array(audio.get_array_of_samples())
    return signal, audio.frame_rate

def write_mp3(file_path, signal, frame_rate):
    audio = AudioSegment(signal.tobytes(), frame_rate=frame_rate, sample_width=2, channels=1)
    audio.export(file_path, format="mp3")

def open_file_entry(entry):
    file_path = filedialog.askopenfilename()
    entry.delete(0, tk.END)
    entry.insert(0, file_path)

def add_noise_to_audio(input_file, SNR_dB):
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

    # Generate the output file name based on input file and SNR
    input_filename, input_extension = os.path.splitext(os.path.basename(input_file))
    output_file = f"{input_filename}_noisy_SNR_{SNR_dB}dB{input_extension}"

    # Write the noisy audio as a new MP3 file
    write_mp3(output_file, noisy_signal.astype(np.int16), frame_rate)
    messagebox.showinfo("Success", f"Noisy audio generated successfully!\nSaved as: {output_file}")

def generate_noisy_audio(input_entry, snr_slider):
    input_file = input_entry.get()
    snr_dB = snr_slider.get()
    
    if not input_file:
        messagebox.showerror("Error", "Please select an input file.")
        return
    
    try:
        add_noise_to_audio(input_file, snr_dB)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# GUI setup
app = tk.Tk()
app.title("Noisy Audio Generator")

# Input File Entry
input_label = tk.Label(app, text="Input File:")
input_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)
input_entry = tk.Entry(app, width=40)
input_entry.grid(row=0, column=1, columnspan=2, pady=5)
input_button = tk.Button(app, text="Browse", command=partial(open_file_entry, input_entry))
input_button.grid(row=0, column=3, pady=5)

# SNR Slider
snr_label = tk.Label(app, text="SNR (dB):")
snr_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)
snr_slider = tk.Scale(app, from_=0, to=30, orient="horizontal", length=200)
snr_slider.grid(row=1, column=1, columnspan=2, pady=5)

# Generate Noisy Audio Button
generate_button = tk.Button(app, text="Generate Noisy Audio", command=partial(generate_noisy_audio, input_entry, snr_slider))
generate_button.grid(row=2, column=0, columnspan=4, pady=10)

app.mainloop()
