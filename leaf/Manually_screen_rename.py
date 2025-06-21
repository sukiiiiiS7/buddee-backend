import os
import shutil

dir_path = "leaf_cleaned_ai"

valid_exts = (".jpg", ".jpeg", ".png")
all_files = sorted([
    f for f in os.listdir(dir_path)
    if os.path.isfile(os.path.join(dir_path, f)) and f.lower().endswith(valid_exts)
])

temp_dir = os.path.join(dir_path, "temp_rename")
os.makedirs(temp_dir, exist_ok=True)

count = 1
for filename in all_files:
    new_name = f"leaf_{count:03}.jpg"
    try:
        src = os.path.join(dir_path, filename)
        dst = os.path.join(temp_dir, new_name)
        from PIL import Image
        img = Image.open(src).convert("RGB")
        img.save(dst, "JPEG")
        count += 1
    except Exception as e:
        print(f"Skipped: {filename}, reason: {e}")

for f in all_files:
    try:
        os.remove(os.path.join(dir_path, f))
    except Exception:
        pass

for f in os.listdir(temp_dir):
    shutil.move(os.path.join(temp_dir, f), os.path.join(dir_path, f))

os.rmdir(temp_dir)

print(f"Renamed {count - 1} files to leaf_001.jpg ~ leaf_{count - 1:03}.jpg")
