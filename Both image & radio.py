import os
import cv2 as cv
import time
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from tqdm import tqdm

from comms_lib.pluto import Pluto
from comms_lib.system import DigitalCommSystem

def digital_modulation(bits):
    return 2 * bits.astype(np.float32) - 1

def digital_demodulation(symbols):
    return (symbols > 0).astype(np.uint8)

# Flag image dictionary
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
    
}

# SDR setup
fs = int(10e6)
sps = 1

pluto = Pluto("usb:1.4.5")
pluto.tx_gain = 90
pluto.rx_gain = 90
pluto.sample_rate = fs

system = DigitalCommSystem()
system.set_transmitter(pluto)
system.set_receiver(pluto)

print("What country in Europe do you want to visit? (Even Number, click enter):")

while True:
    name = input("> ").strip().lower()
    if name == "":
        break
    
    if name in flags_dict:
        img_path = flags_dict[name]

        if not os.path.exists(img_path):
            print(f"⚠️ Image file not found for {name}")
            continue

        img = Image.open(img_path).convert("RGB")
        img = img.resize((32, 32), Image.Resampling.LANCZOS)
        img_array_rgb = np.array(img)
        H, W, _ = img_array_rgb.shape

        # Combine RGB channels
        flat_rgb = img_array_rgb.reshape(-1, 3).flatten()
        bits = np.unpackbits(flat_rgb, bitorder='big')
        symbols = digital_modulation(bits)

        chunk_size = 4000
        received_chunks = []

        print(f"Transmitting image of {name}...")
        print(f"Number of symbols: {symbols}")
        start_time = time.time()

        for i in tqdm(range(0, len(symbols), chunk_size), desc="Chunks"):
            chunk = symbols[i:i + chunk_size]
            system.transmit_signal(chunk)

            expected = len(chunk) * sps
            received = np.array([], dtype=np.complex64)
            attempts = 0
            while len(received) < expected and attempts < 50:
                received = np.concatenate((received, system.receive_signal()))
                attempts += 1

            rx_chunk = received[sps // 2 :: sps][:len(chunk)]
            received_chunks.append(rx_chunk)

        print(f"Transmission done in {time.time() - start_time:.2f} sec")

        received_symbols = np.concatenate(received_chunks)
        received_bits = digital_demodulation(received_symbols)[:len(bits)]
        received_bytes = np.packbits(received_bits, bitorder='big')
        if len(received_bytes) < flat_rgb.size:
            padded = np.zeros(flat_rgb.size, dtype=np.uint8)
            padded[:len(received_bytes)] = received_bytes
            received_bytes = padded

        received_rgb = received_bytes.reshape(H, W, 3)

        # Show both images
        plt.figure(figsize=(10, 5))
        plt.subplot(1, 2, 1)
        plt.title("Original Image", pad = 20)
        plt.imshow(img_array_rgb)
        plt.axis("off")

        plt.subplot(1, 2, 2)
        plt.title("Received Image", pad = 20)
        plt.imshow(received_rgb)
        plt.axis("off")

        plt.tight_layout()
        plt.show()
    else:
        print(f"No image found for {name}")
