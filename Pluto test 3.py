import numpy as np
import cv2
import matplotlib.pyplot as plt
from adi import Pluto
import reedsolo

# Reed-Solomon codec with 64 parity symbols
rsc = reedsolo.RSCodec(64)

def digital_modulation(img_path, sdr_uri="usb:0"):
    # Load grayscale image
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"Could not load image at '{img_path}'")
    print(f"Loaded image shape: {img.shape}")

    img_bytes = img.flatten()
    print(f"Original image bytes length: {len(img_bytes)}")

    # Encode image bytes with Reed-Solomon
    print("Encoding image with Reed-Solomon...")
    encoded = rsc.encode(img_bytes.tobytes())
    print(f"Encoded length: {len(encoded)} bytes")

    # Prepare transmission samples (center around 0 and normalize)
    tx_data = np.frombuffer(encoded, dtype=np.uint8).astype(np.float32) - 127.5
    tx_data /= 127.5
    tx_samples = tx_data + 0j

    try:
        print("Initializing PlutoSDR for transmission...")
        sdr = Pluto(sdr_uri)
        sdr.sample_rate = int(2e6)
        sdr.tx_rf_bandwidth = int(2e6)
        sdr.tx_lo = int(915e6)
        sdr.tx_cyclic_buffer = False

        print("Transmitting...")
        sdr.tx(tx_samples)
        print("Transmission done.")
        return sdr, img, len(encoded)  # Return Pluto instance to keep alive, image, and encoded length

    except Exception as e:
        print(f"PlutoSDR not found or error: {e}")
        print("Falling back to simulated loopback...")
        sdr = None
        return sdr, img, len(encoded), tx_samples  # Return tx_samples for simulated RX


def digital_demodulation(sdr, img_shape, encoded_len, tx_samples=None):
    if sdr is not None:
        try:
            sdr.rx_lo = sdr.tx_lo
            sdr.rx_rf_bandwidth = int(2e6)
            sdr.rx_buffer_size = encoded_len
            print("Receiving...")
            rx_samples = sdr.rx()
            print("Reception done.")
            sdr.tx_destroy_buffer()
            del sdr

            received_real = np.real(rx_samples)
            received_bytes = np.clip((received_real * 127.5) + 127.5, 0, 255).astype(np.uint8)

        except Exception as e:
            print(f"Error during reception: {e}")
            return None

    else:
        # Use simulated loopback
        print("Simulated reception (loopback)...")
        received_bytes = np.clip((np.real(tx_samples) * 127.5) + 127.5, 0, 255).astype(np.uint8)

    print(f"Received bytes length: {len(received_bytes)}")

    # Decode with Reed-Solomon
    print("Decoding received bytes with Reed-Solomon...")
    try:
        decoded_bytes = rsc.decode(received_bytes.tobytes())
        if isinstance(decoded_bytes, tuple):
            decoded_bytes = decoded_bytes[0]
        print("Decoding successful.")
    except reedsolo.ReedSolomonError as e:
        print(f"Reed-Solomon decoding failed: {e}")
        # Show raw received bytes as fallback
        decoded_bytes = received_bytes[:img_shape[0] * img_shape[1]].tobytes()

    recovered_img = np.frombuffer(decoded_bytes, dtype=np.uint8).reshape(img_shape)
    return recovered_img


if __name__ == "__main__":
    image_path = "Teachers/Ethan_Ge.jpg"
    sdr_uri = "usb:0"  # Change as needed

    # Modulate and transmit
    sdr, img, encoded_len, *extra = digital_modulation(image_path, sdr_uri)
    tx_samples = extra[0] if extra else None

    # Receive and demodulate
    recovered_img = digital_demodulation(sdr, img.shape, encoded_len, tx_samples)

    # Display images
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    plt.imshow(img, cmap='gray')
    plt.title("Original Image")
    plt.axis('off')

    plt.subplot(1, 2, 2)
    if recovered_img is not None:
        plt.imshow(recovered_img, cmap='gray')
        plt.title("Recovered Image")
    else:
        plt.text(0.5, 0.5, 'No image received', ha='center', va='center')
        plt.title("Recovered Image")
    plt.axis('off')

    plt.tight_layout()
    plt.show()
