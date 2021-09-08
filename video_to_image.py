import argparse
import cv2 
import numpy as np
import os


# Initiate argument parser

parser = argparse.ArgumentParser(
    description="Generate images from video")

parser.add_argument("-s",
                    "--source_path",
                    type = str,
                    help="Path to the video file")

parser.add_argument("-d",
                    "--destination_path",
                    type = str,
                    help="Path to the folder that will be saved")

args = parser.parse_args()



def generate_images(source_path, destination_path):

    list_videos = os.listdir(source_path)
    runnig_counter = 1

    for video in list_videos:
        # Path of video
        path = os.path.join(str(source_path), video)
        # Read the video
        cap = cv2.VideoCapture(path)

        # Intialize the counter
        counter_frame = 1

        # Loop through each frame
        while (cap.isOpened()):
            ret, frame = cap.read()
            counter_frame += 1

            if ret==True:
                # Create a counter
                if (counter_frame%30 == 0):
                    # Save the Image               
                    image_path = os.path.join(destination_path, str(runnig_counter) + '.jpg')
                    cv2.imwrite(image_path, frame)
                    runnig_counter += 1
            else:
                cap.release()

if __name__ == '__main__':
    # Save Destination
    generate_images(args.source_path, args.destination_path)
    
