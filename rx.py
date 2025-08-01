# %%
# ruff: noqa: F405
import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from comms_lib.dsp import (
    calc_symbol_error_rate,
    demod_nearest,
    get_qam_constellation,
    qam_demapper,
    qam_mapper,
)
from comms_lib.pluto import Pluto
from comms_lib.system3 import DigitalReceiver, SystemConfiguration
from comms_lib.system3 import DigitalTransmitter, SystemConfiguration



os.chdir(Path(__file__).parent)


# ---------------------------------------------------------------
# Digital communication system parameters.
# ---------------------------------------------------------------
fs = 5e6  # baseband sampling rate (samples per second)
sps = 1

# ---------------------------------------------------------------
# Create shared system configuration
# ---------------------------------------------------------------
modulation_order = 16  # 4, 16, 64, 256, etc.
# Size of the image to transmit, need to be the same for both TX and RX
IMAGE_SIZE = (32, 32)

config = SystemConfiguration(
    modulation_order=modulation_order,
    n_pilot_syms=1500,
    seed=123456,
)
config.sample_rate = fs
config.sps = 10

config.save_to_file(Path(__file__).parent / "system_config.json")

# ---------------------------------------------------------------
# Initialize separate transmitter and receiver with SDR devices
# ---------------------------------------------------------------
tx_sdr = Pluto("usb:1.4.5")  # change to your Pluto device
# Create transmitter and receiver with shared configuration
tx = DigitalTransmitter(config, tx_sdr)
# Set gains
tx.set_gain(100)
carrier_frequency = 850e6
# transmitter.sdr.tx_hardwaregain_chan0 = 0

# ---------------------------------------------------------------
# Prepare data to transmit
# ---------------------------------------------------------------
# Digital modulation parameters

constellation = get_qam_constellation(modulation_order, Es=1)

# Load and prepare image
img = Image.open(Path(__file__).parent / "test.png")
img = img.resize(IMAGE_SIZE)
img = np.array(img)
bits = np.unpackbits(img)

# Map bits to symbols
tx_syms, padding = qam_mapper(bits, constellation)
num_transmit_symbols = len(tx_syms)
print("Number of transmit symbols: ", num_transmit_symbols)

# Shuffle symbols if desired
# shuffler = np.random.default_rng().permutation(num_transmit_symbols)
# transmit_symbols_shuffled = transmit_symbols[shuffler]

tx_syms_shuffled = tx_syms

# ---------------------------------------------------------------
# Transmit and receive
# ---------------------------------------------------------------
# Transmit signal (let the transmitter handle pulse shaping internally)
print("Transmitting signal...")
tx.transmit_signal(tx_syms_shuffled)

# export configuration to for receiver
tx.config.save_to_file(Path(__file__).parent / "tx_config.json")
print("Transmitter configuration saved to tx_config.json")

print("\nTransmitter configuration:")
print(f"  Sample rate: {tx.config.sample_rate/1e6:.1f} MHz")
print(f"  Samples per symbol: {tx.config.sps}")
print(f"  Carrier frequency: {tx.config.carrier_frequency/1e6:.0f} MHz")
print(f"  TX gain: {tx.config.tx_gain}")
# ---------------------------------------------------------------
# Digital communication system parameters.
# ---------------------------------------------------------------
fs = 5e6  # baseband sampling rate (samples per second)
sps = 1
# Size of the image to transmit, need to be the same for both TX and RX
IMAGE_SIZE = (32, 32)

# ---------------------------------------------------------------
# Create shared system configuration
# ---------------------------------------------------------------
config = SystemConfiguration.from_file(Path(__file__).parent / "tx_config.json")
modulation_order = config.modulation_order
carrier_frequency = 850e6


rx_sdr = tx_sdr  # Uncomment to use different device
rx = DigitalReceiver(config, rx_sdr)
rx.set_gain(30)

# Set RF bandwidth
# tx.tx_rf_bandwidth = rx.rx_rf_bandwidth = int(tx.sample_rate / config.sps) * 2

# ---------------------------------------------------------------
# Prepare data to transmit
# ---------------------------------------------------------------
# Digital modulation parameters

constellation = get_qam_constellation(modulation_order, Es=1)

# Load and prepare image
img = Image.open(Path(__file__).parent / "test.png")
img = img.resize(IMAGE_SIZE)
img = np.array(img)
bits = np.unpackbits(img)

# Map bits to symbols
tx_syms, padding = qam_mapper(bits, constellation)
num_transmit_symbols = len(tx_syms)
print("Number of transmit symbols: ", num_transmit_symbols)

# Shuffle symbols if desired
# shuffler = np.random.default_rng().permutation(num_transmit_symbols)
# transmit_symbols_shuffled = transmit_symbols[shuffler]

tx_syms_shuffled = tx_syms


# Receive signal
print("Receiving signal...")
receive_signal = rx.receive_signal()

print("=" * 60)
# ---------------------------------------------------------------
# Process received signal
# ---------------------------------------------------------------
# The receiver already handles pulse shaping, timing sync, frequency sync, and channel equalization
# So receive_signal contains the equalized symbols ready for demodulation
rx_syms = receive_signal
print("Number of receive symbols: ", len(rx_syms))

# Associate received symbols with nearest in constellation
det_rx_syms_shuffled = demod_nearest(rx_syms, constellation)

# Unshuffle received symbols
# detected_receive_symbols = detected_receive_symbols_shuffled[np.argsort(shuffler)]
det_rx_syms = det_rx_syms_shuffled

# Demap symbols to bits
rx_bits = qam_demapper(det_rx_syms, padding, constellation)

print("")

# Calculate error rates
ser = calc_symbol_error_rate(tx_syms, det_rx_syms)
print("Symbol error rate: ", ser)

ber = calc_symbol_error_rate(bits, rx_bits)
print("Bit error rate: ", ber)

# ---------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------
# Plot transmitted and received signals and symbols
fig = plt.figure(figsize=(12, 6))

# Top subplot for real symbols
ax1 = plt.subplot2grid((2, 2), (0, 0), colspan=1)
ax1.plot(
    np.real(tx_syms_shuffled), color="blue", marker="o", label="Real Transmit Symbols"
)
ax1.plot(np.real(rx_syms), color="red", label="Real Receive Symbols")
ax1.set_title("Transmit and Receive Symbols (Real)")
ax1.set_xlabel("Symbol Index")
ax1.set_ylabel("Amplitude")
ax1.grid(True)
ax1.legend()

# Bottom subplot for imaginary symbols
ax2 = plt.subplot2grid((2, 2), (1, 0), colspan=1)
ax2.plot(
    np.imag(tx_syms_shuffled),
    color="blue",
    marker="o",
    label="Imaginary Transmit Symbols",
)
ax2.plot(np.imag(rx_syms), color="red", label="Imaginary Receive Symbols")
ax2.set_title("Transmit and Receive Symbols (Imaginary)")
ax2.set_xlabel("Symbol Index")
ax2.set_ylabel("Amplitude")
ax2.grid(True)
ax2.legend()

# Right side square subplot for symbols
ax3 = plt.subplot2grid((2, 2), (0, 1), rowspan=2, aspect="equal")
ax3.scatter(
    np.real(rx_syms),
    np.imag(rx_syms),
    color="red",
    label="Received Symbols",
)
ax3.scatter(
    np.real(tx_syms),
    np.imag(tx_syms),
    color="blue",
    label="Transmitted Symbols",
)
ax3.set_title("Transmitted and Received Symbols")
ax3.set_xlabel("Real Component")
ax3.set_ylabel("Imaginary Component")
ax3.grid(True)
ax3.legend()
plt.tight_layout()
plt.show()

# Plot the received image
rx_img = np.packbits(rx_bits[: rx_bits.shape[0] - padding]).reshape(img.shape)
fig, ax = plt.subplots(1, 2, figsize=(12, 6))
ax[0].imshow(img)
ax[0].set_title("Original Image")
ax[0].axis("off")
ax[1].imshow(rx_img)
ax[1].set_title("Received Image")
ax[1].axis("off")
plt.tight_layout()
plt.show()

# ---------------------------------------------------------------
# Demonstrate separate TX/RX usage
# ---------------------------------------------------------------
print("\n" + "=" * 60)
print("DEMONSTRATING SEPARATE TX/RX OPERATION")
print("=" * 60)

# Example: Using transmitter and receiver independently


print("\nReceiver configuration:")
print(f"  Sample rate: {rx.config.sample_rate/1e6:.1f} MHz")
print(f"  Samples per symbol: {rx.config.sps}")
print(f"  Carrier frequency: {rx.config.carrier_frequency/1e6:.0f} MHz")
print(f"  RX gain: {rx.config.rx_gain}")

print("\nShared configuration ensures compatibility:")
print(f"  Preamble length: {len(config.preamble_symbols)} symbols")
print(f"  STF symbols: {config.num_stf_symbols}")
print(f"  LTF symbols: {config.num_ltf_symbols}")
print(f"  Pilot symbols: {config.n_pilot_syms}")

# %%
