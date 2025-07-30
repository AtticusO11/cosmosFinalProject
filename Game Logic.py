import cv2 as cv
import os
import time

# Dictionary of teacher names (lowercase) mapped to image paths
teachers_dict = {
    'ethan ge': 'Teachers/Ethan_Ge.jpg',
    'lev tauz': 'Teachers/Lev_Tauz.jpg',
    'professor dolecek': 'Teachers/Professor_Dolecek.jpg',
    'professor roberts': 'Teachers/Professor_Roberts.jpg',
}

print("Type teacher names one by one (leave blank to finish):")
teachers = []
while True:
    name = input("> ").strip()
    if name == "":
        break
    key = name.lower()
    if key in teachers_dict:
        img_path = teachers_dict[key]
        if os.path.exists(img_path):
            img = cv.imread(img_path)
            if img is not None:
                cv.imshow(name, img)
                cv.waitKey(2000)  # display for 2 seconds
                cv.destroyAllWindows()
                time.sleep(0.2)
                print(f"Displayed image for {name}")
            else:
                print(f"⚠️ Failed to load image for {name}")
        else:
            print(f"⚠️ Image file not found for {name}")
    else:
        print(f"No image found for {name}")
