"""
usage: resizer.py [-h] [-p DIR_PATH] [-s SCALE_FACTOR]

Resize images from the directory

optional arguments:
  -h, --help            show this help message and exit
  -p DIR_PATH, --dir_path DIR_PATH
                        path to the images directory
  -s SCALE_FACTOR, --scale_factor SCALE_FACTOR
                        scale factor to resize images
"""

import argparse
import cv2
import os
import uuid

dir_path = os.getcwd()

# Initiate argument parser
parser = argparse.ArgumentParser(
    description="Resize images from the directory")

parser.add_argument("-p",
                    "--dir_path",
                    help="path to the images directory")

parser.add_argument("-s",
                    "--scale_factor",
                    default=0.25,
                    help="scale factor to resize images")

args = parser.parse_args()


def resize_single_image(dir_path, folder, filename, scale_factor):
    # File name
    filename_resized = 'resized-' + str(uuid.uuid1()) + '.jpg'
    # Paths
    path_old = os.path.join(dir_path, folder,filename)
    path_new = os.path.join(dir_path, folder,filename_resized)
    # Read and resize image
    image = cv2.imread(path_old)
    resized = cv2.resize(image,None,fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_AREA)
    # Save image
    cv2.imwrite(path_new,resized)
    # Delete image old image
    os.remove(path_old)


def resize_images(dir_path, scale_factor):
    counter = 0
    for folder in os.listdir(dir_path):
        subfolder_path = os.path.join(dir_path, folder)
        for root, dirs, files in os.walk(subfolder_path, topdown=False):
            for filename in files:
                # resize if is jpg file 
                # the names doesnt contains resized (filename.find('resized') returns -1)
                # and the file is not smaller then 
                file_path = os.path.join(dir_path, folder, filename)
                if filename.endswith(".jpg") and filename.find('resized') and os.path.getsize(file_path) > 122880:
                    counter += 1
                    resize_single_image(dir_path, folder, filename, scale_factor)
    print(f'Successfully Completed \nResized imgaes: {counter}')

if __name__ == '__main__':
    resize_images(args.dir_path, args.scale_factor)

