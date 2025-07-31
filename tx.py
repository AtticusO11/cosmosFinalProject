import os
from pathlib import Path
import numpy as np
from PIL import Image
from comms_lib.dsp import get_qam_constellation, qam_mapper
from comms_lib.pluto import Pluto
from comms_lib.system3 import DigitalTransmitter, SystemConfiguration

# Flags dictionary (your original one)
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

# System parameters
fs = 5e6
sps = 1
IMAGE_SIZE = (32, 32)
CHUNK_SIZE = 4000  # symbols per chunk

# Create system config and save to file
modulation_order = 16
config = SystemConfiguration(
    modulation_order=modulation_order,
    n_pilot_syms=1500,
    seed=123456,
)
config.sample_rate = fs
config.sps = sps
config.save_to_file(Path(__file__).parent / "tx_config.json")

# Setup SDR and transmitter
tx_sdr = Pluto("usb:0.4.5")
tx = DigitalTransmitter(config, tx_sdr)
tx.set_gain(100)

def transmit_in_chunks(tx_obj, symbols, chunk_size):
    num_symbols = len(symbols)
    for start_idx in range(0, num_symbols, chunk_size):
        end_idx = min(start_idx + chunk_size, num_symbols)
        chunk = symbols[start_idx:end_idx]
        print(f"Transmitting symbols {start_idx} to {end_idx-1}...")
        tx_obj.transmit_signal(chunk)
    print("Transmission complete.")

print("What country in Europe do you want to visit? (Press Enter to quit)")

while True:
    country = input("> ").strip().lower()
    if country == "":
        break

    if country not in flags_dict:
        print(f"No image found for '{country}'")
        continue

    img_path = flags_dict[country]
    if not os.path.exists(img_path):
        print(f"Image file not found for '{country}' at {img_path}")
        continue

    # Load image, resize and convert to bits
    img = Image.open(img_path).resize(IMAGE_SIZE)
    img = np.array(img)
    bits = np.unpackbits(img)

    # Modulate bits
    constellation = get_qam_constellation(modulation_order, Es=1)
    tx_syms, padding = qam_mapper(bits, constellation)
    print(f"Loaded '{country}', total symbols to transmit: {len(tx_syms)}")

    # Transmit in chunks
    transmit_in_chunks(tx, tx_syms, CHUNK_SIZE)

print("All done. Goodbye!")
