import os
import json
import shutil
import random

SRC_DIR = "SSDD_coco"
OUT_DIR = "dataset"

IMG_TRAIN = os.path.join(OUT_DIR, "images/train")
IMG_TEST = os.path.join(OUT_DIR, "images/test")
LBL_TRAIN = os.path.join(OUT_DIR, "labels/train")
LBL_TEST = os.path.join(OUT_DIR, "labels/test")

for p in [IMG_TRAIN, IMG_TEST, LBL_TRAIN, LBL_TEST]:
    os.makedirs(p, exist_ok=True)

files = [f for f in os.listdir(SRC_DIR) if f.endswith(".jpg")]
files.sort()

# split
random.shuffle(files)
split = int(0.8 * len(files))
train_files = files[:split]
test_files = files[split:]


def process(file_list, img_out, lbl_out):
    for file in file_list:
        img_path = os.path.join(SRC_DIR, file)
        json_path = img_path.replace(".jpg", ".json")

        # copy image
        shutil.copy(img_path, os.path.join(img_out, file))

        # read json
        with open(json_path) as f:
            data = json.load(f)

        # ⚠️ IMPORTANT PART — ADAPT BASED ON YOUR JSON
        # Try this structure first
        objects = data.get("objects", [])

        # fallback (if different)
        if not objects:
            objects = data.get("annotations", [])

        label_file = os.path.join(lbl_out, file.replace(".jpg", ".txt"))

        with open(label_file, "w") as f:
            for obj in objects:

                # POSSIBLE KEYS (depends on your JSON)
                bbox = obj.get("bbox") or obj.get("bndbox")

                if bbox is None:
                    continue

                # if bbox = [x, y, w, h]
                if len(bbox) == 4:
                    x, y, w, h = bbox

                # if bbox = {xmin, ymin, xmax, ymax}
                elif isinstance(bbox, dict):
                    x = bbox["xmin"]
                    y = bbox["ymin"]
                    w = bbox["xmax"] - bbox["xmin"]
                    h = bbox["ymax"] - bbox["ymin"]

                else:
                    continue

                # get image size
                img_w = data.get("width", 512)
                img_h = data.get("height", 512)

                xc = (x + w / 2) / img_w
                yc = (y + h / 2) / img_h
                w /= img_w
                h /= img_h

                f.write(f"0 {xc} {yc} {w} {h}\n")


process(train_files, IMG_TRAIN, LBL_TRAIN)
process(test_files, IMG_TEST, LBL_TEST)

print("✅ Dataset prepared successfully")