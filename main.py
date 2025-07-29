import cv2 as cv
import matplotlib.pyplot as plt
import os
import digital_modulation
import create_message
import digital_demodulation
import plot_m_t

# teachers = {
#     'ethan ge': 'Teachers/Ethan_Ge.jpg',
#     'lev tauz': 'Teachers/Lev_Tauz.jpg',
#     'professor dolecek': 'Teachers/Professor_Dolecek.jpg',
#     'professor roberts': 'Teachers/Professor_Roberts.jpg',
#     'samuel li': 'Teachers/Samuel_Li.jpg'
# }

# name_input = input("Enter the teacher's name: ").strip().lower()

# if name_input in teachers:
#     path = teachers[name_input]

#     if not os.path.exists(path):
#         print(f"File not found: {path}")
#     else:
#         img = cv.imread(path)
#         if img is None:
#             print(f"⚠️ Failed to load image data for {name_input}")
#         else:
#             print(f"Showing an image of {name_input.title()}")
#             img_rgb = cv.cvtColor(img, cv.COLOR_BGR2RGB)  # Convert BGR to RGB
#             plt.imshow(img_rgb)
#             plt.axis('off')
#             plt.title(name_input.title())
#             plt.show()
# else:
#     print("Name not recognized. Try one of these:")
#     for key in teachers:
#         print(f" - {key.title()}")

message = [0,0,0,1,1,1,0,1,0,0,0,1,1,1,0,1,0,0,0,1,1,1,0,1,0,0,0,1,1,1,]
M = 16
sps = 100
symbols = digital_modulation.digital_modulation(message, M)

original_bit_length = len(message)

t, m_t = create_message.create_message(symbols, sps)

final = digital_demodulation.demodulation(m_t, M, sps, original_bit_length)


if ''.join(str(b) for b in message) == final:
    print("✅ Success!")

plot_m_t.plot_m_t(t, m_t)
