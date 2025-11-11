import os
import psutil
import time
import sys
from collections import defaultdict

# ===============================
# Utility Functions
# ===============================

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def pause():
    input("\nPress Enter to continue...")

def list_drives():
    drives = []
    for part in psutil.disk_partitions(all=False):
        if os.name == 'nt' and 'cdrom' not in part.opts and os.path.exists(part.device):
            drives.append(part.device)
    return drives

def progress_bar(current, total, bar_length=40):
    """Display a simple progress bar in the console."""
    percent = (current / total) * 100 if total > 0 else 100
    filled = int(bar_length * current // total) if total > 0 else bar_length
    bar = '█' * filled + '-' * (bar_length - filled)
    sys.stdout.write(f'\r|{bar}| {percent:6.2f}%')
    sys.stdout.flush()

# ===============================
# File Categorization
# ===============================

FILE_CATEGORIES = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".svg", ".webp"},
    "Videos": {".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv", ".webm"},
    "Audio": {".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"},
    "Documents": {".txt", ".doc", ".docx", ".pdf", ".xls", ".xlsx", ".ppt", ".pptx", ".csv"},
    "Scripts": {".py", ".js", ".ps1", ".sh", ".bat", ".cmd"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz"},
    "Applications": {".exe", ".msi", ".bat", ".cmd"},
}

def categorize_file(file_path):
    """Return a general category name based on file extension."""
    ext = os.path.splitext(file_path)[1].lower()
    for category, extensions in FILE_CATEGORIES.items():
        if ext in extensions:
            return category
    return "Other"

# ===============================
# File Counting with Progress
# ===============================

def count_files_with_details(path):
    """Count files, folders, and file types with a live progress bar."""
    total_files = 0
    folder_count = 0
    category_counts = defaultdict(int)

    # Step 1: Gather all directories for progress tracking
    print("Scanning folder structure...")
    all_dirs = []
    for root, dirs, files in os.walk(path):
        all_dirs.append(root)
    total_dirs = len(all_dirs)

    print(f"Found {total_dirs:,} folders. Counting files...\n")

    # Step 2: Walk again with progress and detailed counting
    for i, root in enumerate(all_dirs, start=1):
        try:
            entries = os.scandir(root)
            for entry in entries:
                if entry.is_file():
                    total_files += 1
                    category = categorize_file(entry.name)
                    category_counts[category] += 1
                elif entry.is_dir():
                    folder_count += 1
        except PermissionError:
            pass
        progress_bar(i, total_dirs)

    sys.stdout.write("\n")
    return total_files, folder_count, category_counts

# ===============================
# Menu System
# ===============================

def show_drive_menu():
    clear()
    drives = list_drives()
    print("=== File Counter Utility ===\n")
    if not drives:
        print("No drives found.")
        return None

    for i, drive in enumerate(drives, start=1):
        try:
            usage = psutil.disk_usage(drive)
            total_gb = usage.total / (1024 ** 3)
            used_gb = usage.used / (1024 ** 3)
            print(f"{i}: {drive} ({used_gb:.2f} GB used of {total_gb:.2f} GB)")
        except PermissionError:
            print(f"{i}: {drive} (Access Denied)")

    print(f"{len(drives) + 1}: Exit\n")
    choice = input("Select a drive number: ")

    if not choice.isdigit():
        return show_drive_menu()
    choice = int(choice)

    if 1 <= choice <= len(drives):
        return drives[choice - 1]
    elif choice == len(drives) + 1:
        print("Goodbye!")
        exit(0)
    else:
        return show_drive_menu()

def show_folder_menu(base_path):
    clear()
    print(f"Subfolders in {base_path}\n")

    try:
        folders = [f.path for f in os.scandir(base_path) if f.is_dir()]
    except PermissionError:
        print("Access denied to this folder.")
        pause()
        return

    if not folders:
        print("No subfolders found.")
        pause()
        return

    for i, folder in enumerate(folders, start=1):
        print(f"{i}: {os.path.basename(folder)}")
    print(f"{len(folders) + 1}: Go back\n")

    choice = input("Select a folder number: ")
    if not choice.isdigit():
        return show_folder_menu(base_path)
    choice = int(choice)

    if 1 <= choice <= len(folders):
        selected = folders[choice - 1]
        clear()
        print(f"Counting files in {selected} ... this may take a while.\n")
        start = time.time()
        total_files, folder_count, categories = count_files_with_details(selected)
        elapsed = time.time() - start

        print(f"\n📊 Results for {selected}")
        print(f"Total folders: {folder_count:,}")
        print(f"Total files: {total_files:,}")
        print("\nFile Type Breakdown:")
        for category, count in sorted(categories.items(), key=lambda x: -x[1]):
            print(f"  {category:<15}: {count:,}")
        print(f"\nCompleted in {elapsed:.2f} seconds.")
        pause()
        return show_folder_menu(base_path)
    elif choice == len(folders) + 1:
        return
    else:
        return show_folder_menu(base_path)

def main_menu(drive):
    while True:
        clear()
        print(f"You selected: {drive}\n")
        print("1: Count total files in this drive")
        print("2: Explore subfolders")
        print("3: Go back to drive selection")
        print("4: Exit\n")

        choice = input("Select an option: ")

        if choice == '1':
            clear()
            print(f"Counting all files in {drive} ... please wait.\n")
            start = time.time()
            total_files, folder_count, categories = count_files_with_details(drive)
            elapsed = time.time() - start

            print(f"\n📊 Results for {drive}")
            print(f"Total folders: {folder_count:,}")
            print(f"Total files: {total_files:,}")
            print("\nFile Type Breakdown:")
            for category, count in sorted(categories.items(), key=lambda x: -x[1]):
                print(f"  {category:<15}: {count:,}")
            print(f"\nCompleted in {elapsed:.2f} seconds.")
            pause()

        elif choice == '2':
            show_folder_menu(drive)

        elif choice == '3':
            return  # back to drive selection

        elif choice == '4':
            print("Goodbye!")
            exit(0)

        else:
            print("Invalid option.")
            time.sleep(1)

# ===============================
# Main Entry
# ===============================

def main():
    while True:
        drive = show_drive_menu()
        if drive:
            main_menu(drive)

if __name__ == "__main__":
    main()
