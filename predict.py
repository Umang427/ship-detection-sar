import os
from ultralytics import YOLO

model = YOLO("model/best.pt")

# use sample_images folder by default
image_folder = "sample_images"

images = [os.path.join(image_folder, img) for img in os.listdir(image_folder)]

for img in images:
    print(f"Processing {img}")
    model.predict(img, conf=0.5, save=True)

print("Prediction done! Check runs/detect/predict/")