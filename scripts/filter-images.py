import os
import random
import shutil

SRC_IMG = r"C:\Users\Nidhi\Downloads\guns_n_knives.yolov8\train\images"
SRC_LBL = r"C:\Users\Nidhi\Downloads\guns_n_knives.yolov8\train\labels"

DST_IMG = r"D:\AI_SURVELLIENCE\gun-knife dataset\images"
DST_LBL = r"D:\AI_SURVELLIENCE\gun-knife dataset\labels"

os.makedirs(DST_IMG, exist_ok=True)
os.makedirs(DST_LBL, exist_ok=True)

# ===== PARAMETERS =====
TARGET_PER_CLASS = 800  # 800 knife + 800 gun = 1600 total

knife_images = []
gun_images = []

# ===== STEP 1: CLASSIFY IMAGES =====
for file in os.listdir(SRC_IMG):
    if not file.endswith(".jpg"):
        continue

    label_path = os.path.join(SRC_LBL, file.replace(".jpg", ".txt"))

    if not os.path.exists(label_path):
        continue

    with open(label_path, "r") as f:
        labels = f.readlines()

    has_knife = False
    has_gun = False

    for line in labels:
        cls = int(line.split()[0])

        if cls == 1:   # knife
            has_knife = True
        elif cls == 0: # gun
            has_gun = True

    if has_knife:
        knife_images.append(file)

    if has_gun:
        gun_images.append(file)

print(f"Knife images: {len(knife_images)}")
print(f"Gun images: {len(gun_images)}")

# ===== STEP 2: SAMPLE BALANCED =====
selected_knife = random.sample(knife_images, min(TARGET_PER_CLASS, len(knife_images)))
selected_gun = random.sample(gun_images, min(TARGET_PER_CLASS, len(gun_images)))

selected = list(set(selected_knife + selected_gun))  # remove duplicates

print(f"Total selected images: {len(selected)}")

# ===== STEP 3: COPY FILES =====
for img in selected:
    lbl = img.replace(".jpg", ".txt")

    shutil.copy(os.path.join(SRC_IMG, img), os.path.join(DST_IMG, img))
    shutil.copy(os.path.join(SRC_LBL, lbl), os.path.join(DST_LBL, lbl))

print("Balanced dataset created!")