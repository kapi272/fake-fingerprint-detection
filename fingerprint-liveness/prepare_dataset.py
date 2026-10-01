import os
import shutil
import random
from pathlib import Path

def prepare_yolo_dataset(source_dir, target_dir, split_ratio=0.8):
    """
    Organizes the dataset into YOLOv8 classification format (train/val splits).
    'real' goes to Live, 'print' and 'replay' go to Fake.
    """
    source_path = Path(source_dir)
    target_path = Path(target_dir)

    # Categories we are mapping
    categories_map = {
        'real': 'Live',
        'print': 'Fake',
        'replay': 'Fake'
    }

    # Lists to hold all file paths
    live_images = []
    fake_images = []

    # 1. Gather all images from all phones
    for phone_folder in source_path.iterdir():
        if phone_folder.is_dir():
            print(f"Processing folder: {phone_folder.name}")
            
            for sub_folder in phone_folder.iterdir():
                if sub_folder.is_dir() and sub_folder.name.lower() in categories_map:
                    target_class = categories_map[sub_folder.name.lower()]
                    
                    # Get all valid images in this subfolder
                    for img_file in sub_folder.iterdir():
                        if img_file.is_file() and img_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp']:
                            if target_class == 'Live':
                                live_images.append(img_file)
                            else:
                                fake_images.append(img_file)

    print(f"Total Live images found: {len(live_images)}")
    print(f"Total Fake images found: {len(fake_images)}")

    # 2. Shuffle the data to ensure random distribution
    random.shuffle(live_images)
    random.shuffle(fake_images)

    # 3. Calculate split indices (80% train, 20% val)
    live_split_idx = int(len(live_images) * split_ratio)
    fake_split_idx = int(len(fake_images) * split_ratio)

    splits = {
        'train': {
            'Live': live_images[:live_split_idx],
            'Fake': fake_images[:fake_split_idx]
        },
        'val': {
            'Live': live_images[live_split_idx:],
            'Fake': fake_images[fake_split_idx:]
        }
    }

    # 4. Create directories and copy files
    for split_name, classes in splits.items():
        for class_name, files in classes.items():
            # Create target directory (e.g., yolo_dataset/train/Live)
            dest_dir = target_path / split_name / class_name
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            print(f"Copying {len(files)} files to {dest_dir}...")
            for idx, img_path in enumerate(files):
                # We rename the file slightly to ensure no name collisions between phones
                new_filename = f"{img_path.parent.parent.name}_{img_path.parent.name}_{idx}{img_path.suffix}"
                shutil.copy2(img_path, dest_dir / new_filename)

    print(f"\nDataset successfully prepared at: {target_dir}")
    print("Folder structure:")
    print(f"{target_dir}/")
    print("├── train/")
    print("│   ├── Live/")
    print("│   └── Fake/")
    print("└── val/")
    print("    ├── Live/")
    print("    └── Fake/")

def add_live_spoof_dataset(source_dir, target_dir, split_ratio=0.8):
    """
    Organizes live_spoof dataset into YOLOv8 classification format (80% train / 20% val).
    'live' -> Live, 'spoof' -> Fake
    """
    source_path = Path(source_dir)
    target_path = Path(target_dir)

    category_map = {'live': 'Live', 'spoof': 'Fake'}

    for src_folder, target_class in category_map.items():
        folder_path = source_path / src_folder
        if not folder_path.exists():
            continue

        images = [f for f in folder_path.iterdir() if f.is_file() and f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp']]
        random.shuffle(images)

        split_idx = int(len(images) * split_ratio)
        train_imgs = images[:split_idx]
        val_imgs = images[split_idx:]

        for split_name, file_list in [('train', train_imgs), ('val', val_imgs)]:
            dest_dir = target_path / split_name / target_class
            dest_dir.mkdir(parents=True, exist_ok=True)

            for img_path in file_list:
                new_name = f"live_spoof_{img_path.name}"
                shutil.copy2(img_path, dest_dir / new_name)

    print(f"Added images from {source_dir} to {target_dir}")

if __name__ == "__main__":
    SOURCE_DIRECTORY = "/Users/sam/Desktop/kk/archive_finger_prints"
    LIVE_SPOOF_DIRECTORY = "live_spoof"
    TARGET_DIRECTORY = "yolo_dataset" 
    
    if Path(SOURCE_DIRECTORY).exists():
        prepare_yolo_dataset(SOURCE_DIRECTORY, TARGET_DIRECTORY)
    if Path(LIVE_SPOOF_DIRECTORY).exists():
        add_live_spoof_dataset(LIVE_SPOOF_DIRECTORY, TARGET_DIRECTORY)

