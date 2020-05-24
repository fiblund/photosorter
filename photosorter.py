from PIL import Image
from PIL.ExifTags import TAGS
from pprint import pprint
import datetime
import os

# image folder
folder = "./Example data/"

# only returns value data
def get_exif(filename):
    try:
        image = Image.open(filename)
    except Exception as e:
        print(f"File: {filename} {e.args}")
        return None
    image.verify()
    return image._getexif()

# returns key-value data
def get_labeled_exif(exif):
    labeled = {}
    for (key, val) in exif.items():
        labeled[TAGS.get(key)] = val

    return labeled

# retrieve all files in the specified folder
files = [file for file in os.listdir(folder) if os.path.isfile(os.path.join(folder, file))]

for file in files:
    print(f"File name: {file}")

    # get the file extension which is needed for when the file name is updated
    file_extension = file.split(".")[-1]

    file_exif = get_exif(f"{folder}/{file}")

    # if the file type is supported by exif continue
    if file_exif == None:
        print("File type not supported for this file... Skipping")
        continue

    labeled_file_exif = get_labeled_exif(file_exif)

    data = {}

    # check if the datetime field exist
    try:
        data["captureDate"] = labeled_file_exif["DateTime"]
    except Exception as e:
        print(e.args)

    formatted_date = data["captureDate"].replace(":", "-")
    formatted_date = formatted_date.replace(" ", "_")

    os.rename(f"{folder}/{file}", f"{folder}/{formatted_date}.{file_extension}")
