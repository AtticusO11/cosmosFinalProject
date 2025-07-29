# %% Import necessary libraries
import matplotlib.pyplot as plt
import numpy as np

from comms_lib.pluto import Pluto

# %% Initialize Pluto SDR
sample_rate = 1e6  # baseband sampling rate (samples per second)

sdr = Pluto("usb:0.9.5")
sdr.carrier_frequency = 815e6  # Set carrier frequency for transmission and reception
sdr.sample_rate = int(sample_rate)  # Set baseband sampling rate of Pluto

# %% Generate a signal to transmit
N = 10000  # number of samples to transmit
t = np.arange(N) / sample_rate  # time vector

# TODO: generate a complex signal at 10kHz. Hint: use `np.exp`
tx_signal = np.zeros(N, dtype=np.complex64)  # Change this line

# %% Transmit and receive signal
# sdr.tx_gain = 0
sdr.tx(tx_signal)

rx_signal = sdr.rx()  # Capture raw samples from Pluto

# plot the received signal
plt.figure()
plt.plot(np.real(rx_signal), np.imag(rx_signal), ".")
plt.xlabel("In-Phase (I)")
plt.ylabel("Quadrature (Q)")
plt.title("Received Signal in IQ Plane")
plt.grid(True)
plt.axis("equal")
plt.show()

# TODO: plot the fft of the received signal
rx_fft = np.zeros(len(rx_signal), dtype=np.complex64)  # Change this line!!

# Get the actual frequency of the FFT: from -sample_rate/2 to sample_rate/2
f = np.linspace(sample_rate / -2, sample_rate / 2, len(rx_fft))

plt.figure()
plt.plot(f / 1e3, rx_fft, color="black")
plt.xlabel("Frequency (kHz)")
plt.ylabel("Magnitude")
plt.title("Oversampled FFT of Received Signal")
plt.grid(True)
plt.show()
# %% Find the antenna resonance frequency by transmitting the same signal across dif
# ferent frequencies
frequencies = np.linspace(2000e6, 3000e6, 100)
rx_powers = []

for f in frequencies:
    # TODO: complete this `for` loop to transmit and receive at each frequency
    pass

rx_powers = np.array(rx_powers) / np.max(rx_powers)  # Normalize the received powers
rx_powers_db = 10 * np.log10(rx_powers)  # Convert to dB scale

# TODO: plot the received powers against frequencies