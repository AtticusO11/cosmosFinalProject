# transmitter.py
import os
import time
from pathlib import Path

import numpy as np
from PIL import Image
from comms_lib.dsp import get_qam_constellation, qam_mapper
from comms_lib.pluto import Pluto
from comms_lib.system3 import DigitalTransmitter, SystemConfiguration

# ---------------------------------------------------------------
# Country to Flag Path Dictionary
# ---------------------------------------------------------------
flags_dict = {
    'albania': 'Flags/Albania.png',
    'andorra': 'Flags/Andorra.png',
    'armenia': 'Flags/Armenia.png',
    'austria': 'Flags/Austria.png',
    'azerbaijan': 'Flags/Azerbaijan.png',
    'belarus': 'Flags/Belarus.png',
    'belgium': 'Flags/Belgium.png',
    'bosnia and herzegovina': 'Flags/Boznia_and_Herzegovina.png',
    'bulgaria': 'Flags/Bulgaria.png',
    'croatia': 'Flags/Croatia.png',
    'cyprus': 'Flags/Cyprus.png',
    'czech republic': 'Flags/Czech Republic.png',
    'denmark': 'Flags/Denmark.png',
    'estonia': 'Flags/Estonia.png',
    'finland': 'Flags/Finland.png',
    'france': 'Flags/France.png',
    'georgia': 'Flags/Georgia.png',
    'germany': 'Flags/Germany.png',
    'greece': 'Flags/greece.png',
    'hungary': 'Flags/Hungary.png',
    'iceland': 'Flags/Iceland.png',
    'ireland': 'Flags/Ireland.png',
    'italy': 'Flags/Italy.png',
    'kosovo': 'Flags/Kosovo.png',
    'north macedonia': 'Flags/North_Macedonia.png',
    'latvia': 'Flags/Latvia.jpg',
    'lithuania': 'Flags/lithuania.jpg',
    'malta': 'Flags/Malta.jpg',
    'moldova': 'Flags/Moldova.jpg',
    'monaco': 'Flags/Monaco.jpg',
    'montenegro': 'Flags/Montenegro.jpg',
    'netherlands': 'Flags/Netherlands.jpg',
    'poland': 'Flags/Polad.jpg',
    'portugal': 'Flags/Portugal.jpg',
    'romania': 'Flags/Romania.jpg',
    'russia': 'Flags/Russia.jpg',
    'san marino': 'Flags/San_Marino.jpg',
    'serbia': 'Flags/serbia.jpg',
    'slovakia': 'Flags/Slovakia.jpg',
    'slovenia': 'Flags/Slovenia.jpg',
    'spain': 'Flags/Spain.jpg',
    'sweden': 'Flags/Sweden.jpg',
    'switzerland': 'Flags/Switzerland.jpg',
    'turkey': 'Flags/turkey.jpg',
    'ukraine': 'Flags/Ukraine.jpg',
    'uk': 'Flags/United_Kingdom.jpg',
}

# ---------------------------------------------------------------
# Ask for country
# ---------------------------------------------------------------
print("What country in Europe do you want to transmit? (Press Enter to skip):")
country = input("> ").strip().lower()

if country not in flags_dict:
    print(f"Country '{country}' not found in dictionary.")
    exit()

img_path = flags_dict[country]
if not os.path.exists(img_path):
    print(f"Image path does not exist: {img_path}")
    exit()

print(f"Loading flag of {country} from {img_path}...")

# ---------------------------------------------------------------
# Load and prepare image
# ---------------------------------------------------------------
IMAGE_SIZE = (32, 32)
img = Image.open(img_path).convert("RGB").resize(IMAGE_SIZE)
img = np.array(img)
bits = np.unpackbits(img)

# ---------------------------------------------------------------
# Communication Parameters
# ---------------------------------------------------------------
carrier_freq = 2.4e9  # Hz
sample_rate = 5e6     # Hz
sps = 1               # samples per symbol
mod_order = 16        # QAM modulation order

# Prepare system config
config = SystemConfiguration.default()
config.sample_rate = sample_rate
config.sps = sps
config.modulation_order = mod_order
config.carrier_frequency = carrier_freq
config.save_to_file("tx_config.json")

# QAM Modulation
constellation = get_qam_constellation(mod_order, Es=1)
tx_syms, padding = qam_mapper(bits, constellation)

# ---------------------------------------------------------------
# Transmit
# ---------------------------------------------------------------
tx_sdr = Pluto("usb:1.4.5")  # Update with correct SDR ID
tx = DigitalTransmitter(config, tx_sdr)
tx.set_gain(100)

print(f"Transmitting {len(tx_syms)} symbols for {country.upper()}...")
tx.transmit_signal(tx_syms)
print("Done.")

# Cleanup
try: tx.close()
except: pass
try: tx_sdr.close()
except: pass

del tx
del tx_sdr
