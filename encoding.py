import cv2 as cv
import numpy as np

def encrypt_pixels(filename):
    img = cv.imread(filename, cv.IMREAD_COLOR)

    if img is None:
        print("Error: image not found")
        exit()

    shape = img.shape
    pixels = img.flatten()

    # not encrypted pixels
    #print(pixels)

    # Convert to a larger integer type to avoid overflow on addition
    pixels_int = pixels.astype(np.uint16)

    # Caesar cipher +7 encryption with no overflow
    cipherpixels = (pixels_int + 7) % 256

    # Cast back to uint8
    cipherpixels = cipherpixels.astype(np.uint8)

    #print(cipherpixels)
    return cipherpixels, shape


filename = "Teachers/Lev_Tauz.jpg"
pixels, original_shape = encrypt_pixels("Teachers/Lev_Tauz.jpg")


def convert_to_bits(pixels):
    bitstream = ''.join(np.binary_repr(pixel, width = 8) for pixel in pixels)

    total_bit_list = [] # list of 8-bit values
    current_bit_list = []
    for bit in bitstream:
        current_bit_list.append(bit)
        if len(current_bit_list) == 8:
            total_bit_list.append(''.join(current_bit_list))
            current_bit_list = []

    return total_bit_list

bit_list = convert_to_bits(pixels)

def chunk(bit_list):
    pixels = []
    for i in range(0, len(bit_list), 3):
        pixel_chunk = bit_list[i: i + 3]
        if len(pixel_chunk) == 3:
            pixels.append(pixel_chunk)

    return pixels

# test: chunked RGB pixels sent pixel by pixel, truncated to first 32 values
chunked_values = chunk(bit_list)
