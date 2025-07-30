# %%
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from comms_lib.pluto import Pluto
from comms_lib.system import DigitalCommSystem

# ---------------------------------------------------------------
# Digital communication system parameters.
# ---------------------------------------------------------------
fs = 10e6
ts = 1 / fs
sps = 3
T = ts * sps

# ---------------------------------------------------------------
# Initialize transmitter and receiver.
# ---------------------------------------------------------------
tx = Pluto("usb:7.5.5")
tx.tx_gain = 90

rx = Pluto("usb:7.6.5")
rx.rx_gain = 90

# ---------------------------------------------------------------
# Initialize digital communication system.
# ---------------------------------------------------------------
system = DigitalCommSystem()
system.set_transmitter(tx)
system.set_receiver(rx)

# ---------------------------------------------------------------
# Load image and convert to bitstream
# ---------------------------------------------------------------
img = Image.open("Teachers/Ethan_Ge.jpg").convert("L")  # grayscale
img_array = np.array(img)
original_shape = img_array.shape

# Convert to bits
flat_img = img_array.flatten()
bits = np.unpackbits(flat_img.astype(np.uint8))

# Modulate bits to BPSK: 0 -> -1, 1 -> +1
symbols = 2 * bits - 1

# ---------------------------------------------------------------
# Chunked transmission
# ---------------------------------------------------------------
chunk_size = 8000  # max ~10,000 samples
received_symbols = []

for i in range(0, len(symbols), chunk_size):
    chunk = symbols[i:i + chunk_size].astype(np.float32)
    system.transmit_signal(chunk)
    rx_chunk = system.receive_signal()
    rx_chunk = rx_chunk[sps // 2 :: sps]  # symbol sampling
    received_symbols.append(rx_chunk[:len(chunk)])  # trim to match

received_symbols = np.concatenate(received_symbols)

# Demodulate: real > 0 → 1, else 0
received_bits = (np.real(received_symbols) > 0).astype(np.uint8)

# Convert back to image
received_bytes = np.packbits(received_bits[: len(flat_img) * 8])
received_img_array = received_bytes.reshape(original_shape)

# ---------------------------------------------------------------
# Plot original and received image
# ---------------------------------------------------------------
plt.figure(figsize=(10, 5))
plt.subplot(1, 2, 1)
plt.imshow(img_array, cmap="gray")
plt.title("Original Image")
plt.axis("off")

plt.subplot(1, 2, 2)
plt.imshow(received_img_array, cmap="gray")
plt.title("Received Image")
plt.axis("off")

plt.tight_layout()
plt.show()
