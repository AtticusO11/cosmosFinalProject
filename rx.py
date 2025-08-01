import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from IPython import get_ipython
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

if get_ipython() is not None:
    get_ipython().run_line_magic("reload_ext", "autoreload")
    get_ipython().run_line_magic("autoreload", "2")

os.chdir(Path(__file__).parent)

fs = 5e6  # baseband sampling rate (samples per second)
sps = 1

IMAGE_SIZE = (32, 32)

config = SystemConfiguration.from_file(Path(__file__).parent / "tx_config.json")
modulation_order = config.modulation_order

rx_sdr = Pluto("usb:1.4.5")  # Uncomment to use different device
rx = DigitalReceiver(config, rx_sdr)
rx.set_gain(30)

constellation = get_qam_constellation(modulation_order, Es=1)

img_shape = (*IMAGE_SIZE, 3)
num_bits = np.prod(img_shape) * 8

print("Receiving signal...")
receive_signal = rx.receive_signal()

print("=" * 60)

rx_syms = receive_signal
print("Number of receive symbols: ", len(rx_syms))

det_rx_syms_shuffled = demod_nearest(rx_syms, constellation)
det_rx_syms = det_rx_syms_shuffled

padding = 0

rx_bits = qam_demapper(det_rx_syms, padding, constellation)

print("")

fig = plt.figure(figsize=(12, 6))

# Top subplot for real symbols
ax1 = plt.subplot2grid((2, 2), (0, 0), colspan=1)

ax1.plot(np.real(rx_syms), color="red", label="Real Receive Symbols")
ax1.set_title("Transmit and Receive Symbols (Real)")
ax1.set_xlabel("Symbol Index")
ax1.set_ylabel("Amplitude")
ax1.grid(True)
ax1.legend()

# Bottom subplot for imaginary symbols
ax2 = plt.subplot2grid((2, 2), (1, 0), colspan=1)

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

ax3.set_title("Received Symbols")
ax3.set_xlabel("Real Component")
ax3.set_ylabel("Imaginary Component")
ax3.grid(True)
ax3.legend()
plt.tight_layout()
plt.show()

# Plot the received image
rx_img = np.packbits(rx_bits[: rx_bits.shape[0] - padding]).reshape((32, 32, 4))
fig, ax = plt.subplots(1, 2, figsize=(12, 6))
ax[0].imshow(rx_img)
ax[0].set_title("Original Image")
ax[0].axis("off")
plt.show()
