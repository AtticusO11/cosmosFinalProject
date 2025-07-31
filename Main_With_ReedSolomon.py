import os
import time
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from tqdm import tqdm
from reedsolo import RSCodec

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

# SDR setup
fs = int(10e6)
sps = 1

pluto = Pluto("usb:0.4.5")
pluto.tx_gain = 90
pluto.rx_gain = 90
pluto.sample_rate = fs

system = DigitalCommSystem()
system.set_transmitter(pluto)
system.set_receiver(pluto)

print("What country in Europe do you want to visit? click enter: ")

while True:
    name = input("> ").strip().lower()
    if name == "":
        break

    if name in flags_dict:
        img_path = flags_dict[name]

        if not os.path.exists(img_path):
            print(f"Image file not found for {name}")
            continue

        img = Image.open(img_path).convert("RGB")
        img = img.resize((32, 32), Image.Resampling.LANCZOS)
        img_array_rgb = np.array(img)
        H, W, _ = img_array_rgb.shape

        rs = RSCodec(20)
        chunk_size_bytes = 235
        chunk_size_bits = chunk_size_bytes * 8

        flat_rgb = img_array_rgb.reshape(-1, 3).flatten().astype(np.uint8)

        encoded_chunks = []
        for i in range(0, len(flat_rgb), chunk_size_bytes):
            chunk = flat_rgb[i:i+chunk_size_bytes]
            encoded = rs.encode(chunk.tobytes())
            encoded_chunks.append(np.frombuffer(encoded, dtype=np.uint8))
        encoded_bytes = np.concatenate(encoded_chunks)

        bits = np.unpackbits(encoded_bytes, bitorder='big')
        symbols = digital_modulation(bits)

        chunk_size = 4000
        received_chunks = []

        print(f"Transmitting image of {name}...")
        print(f"Number of symbols: {len(symbols)}")
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
        plt.figure(figsize=(12, 5))
        plt.plot(symbols[:1000], label="Original Symbols", alpha=0.7)
        plt.plot(received_symbols[:1000].real, label="Received Symbols (Real)", alpha=0.7)
        plt.title("Symbol Levels vs. Time (First 1000 Symbols)")
        plt.xlabel("Symbol Index")
        plt.ylabel("Amplitude")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

        received_bits = digital_demodulation(received_symbols)[:len(bits)]
        received_bytes = np.packbits(received_bits, bitorder='big')

        decoded_chunks = []
        chunk_len = chunk_size_bytes + rs.nsym
        for i in range(0, len(received_bytes), chunk_len):
            rs_chunk = received_bytes[i:i+chunk_len]
            try:
                decoded_chunk, _, errata_pos = rs.decode(rs_chunk.tobytes())
                print(f"Chunk {i//chunk_len}: RS decode success, corrected errors: {len(errata_pos)}")
            except Exception as e:
                print(f"Chunk {i//chunk_len}: RS decode FAILED: {e}")
                decoded_chunk = bytes([0]*chunk_size_bytes)
            decoded_chunks.append(np.frombuffer(decoded_chunk, dtype=np.uint8))

        decoded_array = np.concatenate(decoded_chunks)[:len(flat_rgb)]
        received_rgb = decoded_array.reshape(H, W, 3)

        plt.figure(figsize=(10, 5))
        plt.subplot(1, 2, 1)
        plt.title("Original Image", pad=20)
        plt.imshow(img_array_rgb)
        plt.axis("off")

        plt.subplot(1, 2, 2)
        plt.title("Received Image", pad=20)
        plt.imshow(received_rgb)
        plt.axis("off")

        plt.tight_layout()
        plt.show()
    else:
        print(f"No image found for {name}")
