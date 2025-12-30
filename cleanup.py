import os
import shutil

# Define the base directory
base_dir = "D:\\issue-tracker-api"

# Define the files and directories to remove
files_to_remove = [
    ".env.backup",
    ".env.fixed",
    ".example",
    "start.bat",
    "check_db.py",
    "check_fix_db.py",
    "create_clean_env.py",
    "debug_api.py",
    "debug_db.py",
    "fix_env.py",
]

# Define patterns for files to remove
patterns_to_remove = [
    "test_*.py",
]

# Remove specific files
for file in files_to_remove:
    file_path = os.path.join(base_dir, file)
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Removed: {file_path}")

# Remove files matching patterns
for pattern in patterns_to_remove:
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.startswith("test_") and file.endswith(".py"):
                file_path = os.path.join(root, file)
                os.remove(file_path)
                print(f"Removed: {file_path}")

print("Cleanup completed!")
