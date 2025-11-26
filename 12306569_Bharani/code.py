import os
import shutil
from collections import namedtuple

# Define a named tuple to hold file details
FileRecord = namedtuple("FileRecord", ["name", "extension", "full_path"])

def scan_files(directory):
    """
    Return a list of FileRecord objects in the directory.
    """
    files = []
    for filename in os.listdir(directory):
        full_path = os.path.join(directory, filename)
        if os.path.isfile(full_path):
            extension = os.path.splitext(filename)[1][1:]  # remove dot
            files.append(FileRecord(name=filename, extension=extension, full_path=full_path))
    return files

def display_files(files):
    """
    Display all files with index numbers.
    """
    if not files:
        print("\nNo files found in this directory.\n")
        return
    print("\nFiles in directory:")
    print("---------------------")
    for idx, file in enumerate(files, 1):
        print(f"{idx}. {file.name}")
    print("---------------------")

def rename_file(directory, files, index, new_name):
    """
    Rename the selected file.
    """
    old_path = files[index].full_path
    new_path = os.path.join(directory, new_name)
    os.rename(old_path, new_path)
    print(f"\nRenamed '{files[index].name}' to '{new_name}'.")

def organize_files_by_extension(directory, files):
    """
    Move files into folders based on their extension.
    """
    for file in files:
        folder = os.path.join(directory, file.extension.upper() + "_Files")
        os.makedirs(folder, exist_ok=True)
        new_path = os.path.join(folder, file.name)
        shutil.move(file.full_path, new_path)
    print("\nFiles have been organized by extension.")

def show_menu():
    """
    Display the main menu.
    """
    print("\nAutomatic File Renamer and Organizer")
    print("---------------------------------------")
    print("1. Show files")
    print("2. Rename a file")
    print("3. Organize files by extension")
    print("4. Rescan directory")
    print("5. Exit")

# Main program execution
directory = input("Enter the directory path to organize: ").strip()
files = scan_files(directory)

while True:
    show_menu()
    choice = input("\nEnter your choice (1-5): ").strip()
    
    if choice == "1":
        files = scan_files(directory)
        display_files(files)
    elif choice == "2":
        files = scan_files(directory)
        display_files(files)
        if files:
            try:
                index = int(input("Enter file number to rename: ")) - 1
                if 0 <= index < len(files):
                    new_name = input("Enter new file name (with extension): ").strip()
                    rename_file(directory, files, index, new_name)
                else:
                    print("Invalid file number!")
            except ValueError:
                print("Invalid input. Please enter a number.")
    elif choice == "3":
        files = scan_files(directory)
        organize_files_by_extension(directory, files)
    elif choice == "4":
        files = scan_files(directory)
        print("\nDirectory rescanned.")
    elif choice == "5":
        print("\nThank you for using the File Organizer!")
        break
    else:
        print("Invalid choice. Please enter 1–5.")
