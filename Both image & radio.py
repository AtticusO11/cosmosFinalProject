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
    return 2 * bits.astype(np.float32) - 1 #Maps bits {0, 1} to BPSK symbols {-1, 1}

def digital_demodulation(symbols):
    return (symbols > 0).astype(np.uint8) #Demodulates bits into integer range {0, 255}

# Flag image dictionary: Accurately maps each flag to the country name for input ease
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
fs = int(10e6) # Sampling frequency - 10 million samples per second(integer value)
sps = 1 #Each sample is represented by exactly 1 symbol(Basic transmission unit)

pluto = Pluto("usb:1.4.5") #Accurately identifies the Pluto SDR we will use by usb id
pluto.tx_gain = 90 #Controls how much the signal is amplified before being sent over-air
pluto.rx_gain = 90 #Does the same as above, but for the image being received by the computer from the SDR
pluto.sample_rate = fs #Sets the rate of sampling of the pluto SDR equal to the predetermined sampling frequency
pluto.tx_lo = int(850e6) #Set carrier frequency to 850 MHz
pluto.rx_lo = int(850e6)

system = DigitalCommSystem()

#Sets the transmitter and receiver of the system as the Pluto SDR
system.set_transmitter(pluto) 
system.set_receiver(pluto)

print("What country in Europe do you want to visit? click enter: ") #Fundamental input

while True:
    name = input("> ").strip().lower() #Converts to lowercase
    if name == "": #End code if enter button pressed
        break
    
    if name in flags_dict:
        img_path = flags_dict[name] #Set the image path to the associated country in the image dictionary

        if not os.path.exists(img_path):
            print(f"Image file not found for {name}")
            continue

        img = Image.open(img_path).convert("RGB") #Opens the image and ensures full color
        img = img.resize((16, 16), Image.Resampling.LANCZOS) #Resizes the image to 16x16 to ensure speed
        img_array_rgb = np.array(img) #Converts the image into an array of usable data
        H, W, _ = img_array_rgb.shape #Extracts the height(pixels), width(pixels), and number of color channels in the image

        # Combine RGB channels
        flat_rgb = img_array_rgb.reshape(-1, 3).flatten() #Turns image data into a 1d array of 
        bits = np.unpackbits(flat_rgb, bitorder='big')#Converts each byte into its 8-bit binary representation
        symbols = digital_modulation(bits) #Performs digital modulation to convert bits to symbols

        chunk_size = 4000 #Sets a chunk size
        received_chunks = []#Creates an empty list of received chunks

        print(f"Transmitting image of {name}...")
        print(f"Number of symbols: {symbols}")
        start_time = time.time()

        for i in tqdm(range(0, len(symbols), chunk_size), desc="Chunks"): #For loop to send over all chunks
            chunk = symbols[i:i + chunk_size]#Divides the image(represented in symbols) in chunks to send over one-by-one
            system.transmit_signal(chunk) #Transmits a signal in the form of a chunk

            expected = len(chunk) * sps #Calculates how many symbols expected to receive
            received = np.array([], dtype=np.complex64) #Creates numpy array of received data
            attempts = 0 #Calculates how many times you've tried to send enough signals to SDR
            while len(received) < expected and attempts < 50: #A loop that combines all signals
                received = np.concatenate((received, system.receive_signal()))
                attempts += 1 #Gradually adds an attempt

            rx_chunk = received[sps // 2 :: sps][:len(chunk)] #Extracts chunks from signal
            received_chunks.append(rx_chunk) #Cmobines all chunk sizes

        print(f"Transmission done in {time.time() - start_time:.2f} sec")

        received_symbols = np.concatenate(received_chunks)
        # Plot symbol levels vs. time (before and after transmission)
        plt.figure(figsize=(12, 5))

        plt.plot(symbols[:1000], label="Original Symbols", alpha=0.7)
        plt.plot(received_symbols[:1000].real, label="Received Symbols (Real)", alpha=0.7)
        plt.title("Symbol Levels vs. Time (First 1000 Symbols)")
        plt.xlabel("Symbol Index")
        plt.ylabel("Amplitude")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show() #Prints graph of transmitted vs. received symbols

        received_bits = digital_demodulation(received_symbols)[:len(bits)] #Demodulate bits within the chunks
        received_bytes = np.packbits(received_bits, bitorder='big') 
        if len(received_bytes) < flat_rgb.size: #Math logic to ensure that enough bits are sent per chunk using padding
            padded = np.zeros(flat_rgb.size, dtype=np.uint8)
            padded[:len(received_bytes)] = received_bytes
            received_bytes = padded

        received_rgb = received_bytes.reshape(H, W, 3) #Reshape bits to image

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
