from PIL import Image
import piexif
import os
import shutil

# Input and output paths
input_path = "input/20241124_150728.jpg"
output_path = "output/20241124_150728.jpg"

# Resize image
with Image.open(input_path) as img:
    exif_data = piexif.load(img.info.get("exif", b""))
    
    new_size = (1920, 1080)  # Set desired width and height
    resized_img = img.resize(new_size, resample=Image.LANCZOS)  # Set desired width and height
    # Embed the original EXIF data, including GPS metadata, into the resized image
    exif_bytes = piexif.dump(exif_data)
    resized_img.save(output_path, exif=exif_bytes, qualtiy=100)

# Preserve timestamps
shutil.copystat(input_path, output_path)