from PIL import Image
from PIL.ExifTags import TAGS
from pprint import pprint
import datetime
import os
import subprocess as sub
import re

# exif tool path
exif_tool_path = "C:\projects\exiftool-11.99\exiftool.exe"

# image folder
folder = "P:\Madeira\\"
# folder = "C:\projects\photosorter\Example data\\"

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

# mp4 exif
def mp4_exif(fpath):
    p = sub.Popen(
        [exif_tool_path, '-h',fpath],
        stdout=sub.PIPE,
        encoding='utf8')
    res, err = p.communicate()
    pattern = re.compile(r'Media Create Date\</td\>\<td\>(\d{4}:\d{2}:\d{2}\s\d{2}:\d{2}:\d{2})')
    match = re.findall(pattern, res)
    if match:
        return match[0]

# retrieve all files in the specified folder
files = [file for file in os.listdir(folder) if os.path.isfile(os.path.join(folder, file))]

for file in files:
    print(f"File name: {file}")
    data = {}

    # get the file extension which is needed for when the file name is updated
    file_extension = file.split(".")[-1]

    # if file type is .MOV, then skip
    if file_extension == "MOV":
        continue

    if file_extension == "mp4" or file_extension == "MP4":
        file_path = f"{folder}\\{file}"
        data["captureDate"] = mp4_exif(file_path)
    else:
        file_exif = get_exif(f"{folder}/{file}")
        labeled_file_exif = get_labeled_exif(file_exif)

        # check if the "DateTime" field exist
        try:
            data["captureDate"] = labeled_file_exif["DateTime"]
        except Exception as e:
            pass
            # print(e)

        # if the field "DateTime" doesn't exist, use the field "DateTimeOriginal" instead
        if not bool(data):
            try:
                data["captureDate"] = labeled_file_exif["DateTimeOriginal"]
            except Exception as e:
                print(e)

    # try to correct wrong picture date stamps
    if "2015" in data["captureDate"]:
        date_year = data["captureDate"][0:4]
        date_month = data["captureDate"][5:7]
        date_day = data["captureDate"][8:10]
        date_hour = data["captureDate"][11:13]
        date_minute = data["captureDate"][14:16]
        date_second = data["captureDate"][17:19]

        minutes_to_add = 3
        hours_to_add = 17
        days_to_add = 13
        months_to_add = 7
        years_to_add = 3

        # add 3 minutes to minute field
        date_minute = int(date_minute) + minutes_to_add
        minutes_removed = 0
        if date_minute > 60:
            while date_minute > 60:
                date_minute -= 1
                minutes_removed += 1
            date_minute = minutes_removed
            hours_to_add += 1
        if len(str(date_minute)) == 1:
            date_minute = f"0{date_minute}"

        # add 17 hours to hour field
        date_hour = int(date_hour) + hours_to_add
        hours_removed = 0
        if date_hour > 24:
            while date_hour > 24:
                date_hour -= 1
                hours_removed += 1
            date_hour = hours_removed
            days_to_add += 1
        if len(str(date_hour)) == 1:
            date_hour = f"0{date_hour}"

        # add 13 days to day field
        date_day = int(date_day) + days_to_add
        if len(str(date_day)) == 1:
            date_day = f"0{date_day}"

        # add 7 months to month field
        date_month = int(date_month) + months_to_add
        if len(str(date_month)) == 1:
            date_month = f"0{date_month}"

        # add 3 years to year field
        date_year = int(date_year) + years_to_add
        if len(str(date_year)) == 1:
            date_year = f"0{date_year}"

        data["captureDate"] = f"{date_year}:{date_month}:{date_day} {date_hour}:{date_minute}:{date_second}"

    # replace any ":" with "-" and replace any " " with "_"
    formatted_date = data["captureDate"].replace(":", "-")
    formatted_date = formatted_date.replace(" ", "_")

    # write new file name to console
    try:
        pprint(f"{folder}/{formatted_date}.{file_extension}")
    except Exception as e:
        print(e)

    # rename the file
    try:
        os.rename(f"{folder}/{file}", f"{folder}/{formatted_date}.{file_extension}")
    except Exception as e:
        print(e)
