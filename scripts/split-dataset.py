import os
import random
import shutil

# ===== PATHS =====
BASE_PATH = r"D:\AI_SURVELLIENCE\gun-knife dataset"

SRC_IMG = os.path.join(BASE_PATH, "images")
SRC_LBL = os.path.join(BASE_PATH, "labels")

TRAIN_IMG = os.path.join(BASE_PATH, "images", "train")
VAL_IMG = os.path.join(BASE_PATH, "images", "val")

TRAIN_LBL = os.path.join(BASE_PATH, "labels", "train")
VAL_LBL = os.path.join(BASE_PATH, "labels", "val")

# ===== CREATE FOLDERS =====
os.makedirs(TRAIN_IMG, exist_ok=True)
os.makedirs(VAL_IMG, exist_ok=True)
os.makedirs(TRAIN_LBL, exist_ok=True)
os.makedirs(VAL_LBL, exist_ok=True)

# ===== GET IMAGES =====
images = [f for f in os.listdir(SRC_IMG) if f.endswith(".jpg")]

random.shuffle(images)

# ===== SPLIT =====
split_index = int(0.8 * len(images))

train_images = images[:split_index]
val_images = images[split_index:]

print(f"Total images: {len(images)}")
print(f"Train: {len(train_images)}")
print(f"Validation: {len(val_images)}")

# ===== MOVE FILES =====
for img in train_images:
    lbl = img.replace(".jpg", ".txt")

    shutil.move(os.path.join(SRC_IMG, img), os.path.join(TRAIN_IMG, img))
    shutil.move(os.path.join(SRC_LBL, lbl), os.path.join(TRAIN_LBL, lbl))

for img in val_images:
    lbl = img.replace(".jpg", ".txt")

    shutil.move(os.path.join(SRC_IMG, img), os.path.join(VAL_IMG, img))
    shutil.move(os.path.join(SRC_LBL, lbl), os.path.join(VAL_LBL, lbl))

print("✅ Dataset successfully split into train and val!")  