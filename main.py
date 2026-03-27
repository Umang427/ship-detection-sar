import os
import shutil
import random
from ultralytics import YOLO

# ==============================
# BACKGROUND GENERATION
# ==============================
def generate_background(img_dir, label_dir, num_bg=200):
    print("Generating background images...")

    images = os.listdir(img_dir)

    created = 0
    for img in images:
        label_path = os.path.join(label_dir, img.replace(".jpg", ".txt"))

        # if no label OR empty label → background
        if not os.path.exists(label_path) or os.path.getsize(label_path) == 0:

            new_name = f"bg_{created}.jpg"

            shutil.copy(
                os.path.join(img_dir, img),
                os.path.join(img_dir, new_name)
            )

            open(os.path.join(label_dir, new_name.replace(".jpg", ".txt")), "w").close()

            created += 1

        if created >= num_bg:
            break

    print(f"Created {created} background images")


# ==============================
# TRAIN MODEL (WITH AUGMENTATION)
# ==============================
def train_model():
    print("Training started...")

    model = YOLO("yolov8s.pt")

    model.train(
        data="data.yaml",
        epochs=80,
        imgsz=768,
        batch=12,
        workers=2,

        optimizer="AdamW",
        lr0=0.003,
        patience=20,

        # 🔥 AUGMENTATION (SAR SAFE)
        fliplr=0.5,
        flipud=0.5,
        scale=0.3,
        translate=0.1,
        degrees=10,
        mosaic=0.5,
        close_mosaic=10,

        hsv_h=0.0,
        hsv_s=0.0,
        hsv_v=0.0,

        mixup=0.0,
        copy_paste=0.0,

        iou=0.6
    )

    print("Training finished!")


# ==============================
# SAVE BEST MODEL
# ==============================
def save_model():
    src = "runs/detect/train/weights/best.pt"
    dst = "model/best.pt"

    os.makedirs("model", exist_ok=True)

    if os.path.exists(src):
        shutil.copy(src, dst)
        print("Model saved to model/best.pt")
    else:
        print("ERROR: best.pt not found!")


# ==============================
# MAIN PIPELINE
# ==============================
if __name__ == "__main__":

    print("Pipeline started...")

    # Step 1: Generate background
    generate_background("dataset/images/train", "dataset/labels/train", 600)

    # Step 2: Train model
    train_model()

    # Step 3: Save model
    save_model()

    print("Pipeline complete!")