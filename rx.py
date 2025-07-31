import numpy as np
import matplotlib.pyplot as plt
from comms_lib.pluto import Pluto
from comms_lib.system3 import DigitalReceiver, SystemConfiguration
from comms_lib.dsp import get_qam_constellation
import time

# ---------------------------------------------------------------
# Load system config
# ---------------------------------------------------------------
config = SystemConfiguration.load_from_file("tx_config.json")
mod_order = config.modulation_order
constellation = get_qam_constellation(mod_order, Es=1)

# ---------------------------------------------------------------
# Create receiver
# ---------------------------------------------------------------
rx_sdr = Pluto("usb:0.4.5")  # Adjust for your receiver SDR
rx = DigitalReceiver(config, rx_sdr)

print("Receiving symbols...")
rx_syms = rx.receive_signal()
print(f"Received {len(rx_syms)} symbols")

# ---------------------------------------------------------------
# Demodulate
# ---------------------------------------------------------------
rx_bits, _ = rx.demodulate(rx_syms, constellation)

# ---------------------------------------------------------------
# Reconstruct image
# ---------------------------------------------------------------
# Expecting 32×32 RGB = 32*32*3 = 3072 pixels = 3072*8 = 24576 bits
expected_bits = 32 * 32 * 3 * 8

if len(rx_bits) < expected_bits:
    print(f"WARNING: Only received {len(rx_bits)} bits (need {expected_bits})")
    rx_bits = np.pad(rx_bits, (0, expected_bits - len(rx_bits)), constant_values=0)
else:
    rx_bits = rx_bits[:expected_bits]

rx_bytes = np.packbits(rx_bits)
img = rx_bytes.reshape((32, 32, 3))

# ---------------------------------------------------------------
# Display image
# ---------------------------------------------------------------
plt.imshow(img)
plt.title("Received Flag")
plt.axis("off")
plt.show()

# Cleanup
try: rx.close()
except: pass
try: rx_sdr.close()
except: pass

del rx
del rx_sdr
