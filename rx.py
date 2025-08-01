import os
from pathlib import Path
import time

import matplotlib.pyplot as plt
import numpy as np
from IPython import get_ipython
from PIL import Image

from comms_lib.dsp import (
    get_qam_constellation,
    qam_mapper,
    qam_demapper,
)

from comms_lib.pluto import Pluto
from comms_lib.system3 import DigitalTransmitter, SystemConfiguration

if get_ipython() is not None:
    get_ipython().run_line_magic("reload_ext", "autoreload")
    get_ipython().run_line_magic("autoreload", "2")

os.chdir(Path(__file__).parent)

fs = 5e6  # baseband sampling rate (samples per second)
sps = 1

modulation_order = 16  # 4, 16, 64, 256, etc.
IMAGE_SIZE = (32, 32)

config = SystemConfiguration(
    modulation_order=modulation_order,
    n_pilot_syms=1500,
    seed=123456,
)
config.sample_rate = fs
config.sps = 10

config.save_to_file(Path(__file__).parent / "system_config.json")

tx_sdr = Pluto("usb:2.4.5")  # change to your Pluto device
tx = DigitalTransmitter(config, tx_sdr)
tx.set_gain(100)

constellation = get_qam_constellation(modulation_order, Es=1)

# Load and prepare image
img = Image.open("test.png")
img = img.resize(IMAGE_SIZE)
img = np.array(img)
bits = np.unpackbits(img)
print(img.shape)

tx_syms, padding = qam_mapper(bits, constellation)
num_transmit_symbols = len(tx_syms)
tx_syms_shuffled = tx_syms

print("Transmitting signal...")
tx.transmit_signal(tx_syms_shuffled)

tx.config.save_to_file(Path(__file__).parent / "tx_config.json")
print("Transmitter configuration saved to tx_config.json")

print("\nTransmitter configuration:")
print(f"  Sample rate: {tx.config.sample_rate/1e6:.1f} MHz")
print(f"  Samples per symbol: {tx.config.sps}")
print(f"  Carrier frequency: {tx.config.carrier_frequency/1e6:.0f} MHz")
print(f"  TX gain: {tx.config.tx_gain}")

time.sleep(100)
