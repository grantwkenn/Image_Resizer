from PIL import Image
import piexif
import os
import shutil
from pathlib import Path
from datetime import datetime
import filetype



# Input and output paths
input_path = "12 December 2024"
output_path = "12 December 2024_resized2"





def walk(input_dir, output_dir):
    # Walk through the folder and subfolders
    for root, dirs, files in os.walk(input_dir):
        # Get the relative path of the current directory
        relative_path = os.path.relpath(root, input_dir)
        
        # Create the corresponding directory structure in the output directory
        output_folder = os.path.join(output_dir, relative_path)
        os.makedirs(output_folder, exist_ok=True)
        
        # Copy each file to the corresponding directory
        for file in files:
            input_file_path = os.path.join(root, file)
            output_file_path = os.path.join(output_folder, file)
            if filetype.is_image(input_file_path):  # Check if the file is an image
                print(input_file_path)
                resize(input_file_path, output_file_path)




# for file_path in folder_path.rglob('*'):  # '*' matches all files and subfolders
#     if file_path.is_file():
#         modify_time = file_path.stat().st_mtime  # Get modification time
#         modify_date = datetime.fromtimestamp(modify_time)  # Convert to readable format
#         print(str(file_path))  # Do something with the file path

def sanitize_exif(exif_data):
    try:
        # Iterate through all IFDs (Image File Directories)
        for ifd_name in exif_data.keys():
            if isinstance(exif_data[ifd_name], dict):
                for tag, value in list(exif_data[ifd_name].items()):
                    # Remove tags with unexpected types
                    if not isinstance(value, (bytes, int, str, list, tuple)):
                        print(f"Removing invalid EXIF tag: {tag} in {ifd_name} (type: {type(value)})")
                        del exif_data[ifd_name][tag]
    except Exception as e:
        print(f"Error sanitizing EXIF data: {e}")
    return exif_data

def sanitize_exif_2(exif_data):
    # Check and clean improper EXIF types
    for ifd in exif_data:
        for tag in list(exif_data[ifd].keys()):
            # Remove EXIF tags with unsupported data types
            if isinstance(exif_data[ifd][tag], int):
                del exif_data[ifd][tag]    


def resize(input_path, output_path):
    # Resize image
    with Image.open(input_path) as img:

            # Load EXIF data safely
        exif_bytes = img.info.get("exif", None)
        
        if exif_bytes:
            try:
                exif_data = piexif.load(exif_bytes)  # Attempt to load EXIF
                # Search for tag 41729 in all IFD sections
                for ifd_name, ifd_data in exif_data.items():
                    if isinstance(ifd_data, dict) and 41729 in ifd_data:
                        ifd_data[41729] = b"\x01"
                        # print(f"Tag 41729 found in '{ifd_name}' section: {ifd_data[41729]}")
            except Exception:
                exif_data = None  # Handle invalid EXIF cases  
        else:
            exif_data = None  # No EXIF data present  





        
        new_size = (1920, 1080)  # Set desired width and height
        resized_img = img.resize(new_size, resample=Image.LANCZOS)  # Set desired width and height

        if exif_data:
            # Embed the original EXIF data, including GPS metadata, into the resized image
            exif_bytes = piexif.dump(exif_data)
        
            resized_img.save(output_path, exif=exif_bytes, quality=85)
            print("Preserving EXIF data: {}".format(img.filename))
        else:
            # Save the resized image without EXIF data
            resized_img.save(output_path, quality=85)
            print("No EXIF data found: {}".format(img.filename))

        # Preserve timestamps
        shutil.copystat(input_path, output_path)

        


walk(input_path, output_path)





# PS C:\Users\grant\Documents\GitHub\Image_Resizer> py resize.py
# input\20240809_151346.jpg
# Tag 41729 found in 'Exif' section: 1.0
# 2992 is <class 'int'>
# 2992 is <class 'int'>
# b'samsung' is <class 'bytes'>
# b'Galaxy S23' is <class 'bytes'>
# 6 is <class 'int'>
# (72, 1) is <class 'tuple'>
# (72, 1) is <class 'tuple'>
# 2 is <class 'int'>
# b'S911USQS4CXE9' is <class 'bytes'>
# b'2024:08:09 15:13:47' is <class 'bytes'>
# 1 is <class 'int'>
# (2911407, 50000000) is <class 'tuple'>
# (180, 100) is <class 'tuple'>
# 2 is <class 'int'>
# 1600 is <class 'int'>
# b'0220' is <class 'bytes'>
# b'2024:08:09 15:13:47' is <class 'bytes'>
# b'2024:08:09 15:13:47' is <class 'bytes'>
# b'-07:00' is <class 'bytes'>
# b'-07:00' is <class 'bytes'>
# b'\x01\x02\x03\x00' is <class 'bytes'>
# (4102, 1000) is <class 'tuple'>
# (169, 100) is <class 'tuple'>
# (-317, 100) is <class 'tuple'>
# (0, 10) is <class 'tuple'>
# (169, 100) is <class 'tuple'>
# 2 is <class 'int'>
# 0 is <class 'int'>
# (5400, 1000) is <class 'tuple'>
# b'136928' is <class 'bytes'>
# b'136928' is <class 'bytes'>
# b'136928' is <class 'bytes'>
# b'0100' is <class 'bytes'>
# 65535 is <class 'int'>
# 1 is <class 'int'>
# 1.0 is <class 'float'>