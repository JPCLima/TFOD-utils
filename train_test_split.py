import argparse
import os
import math
import shutil

# Initiate argument parser
parser = argparse.ArgumentParser(
    description="Generate a labelmap")

parser.add_argument("-c",
                    "--collected_path",
                    help="path of the collectd images")

parser.add_argument("-t",
                    "--train_path",
                    help="path of train folder")

parser.add_argument("-e",
                    "--test_path",
                    help="path of test folder")

parser.add_argument("-s",
                    "--test_size",
                    default=0.2,
                    help="path of test folder")


args = parser.parse_args()


def train_test_split(images_collected_path,
                     train_path,
                     test_path,
                     split_test_size):
    """
    This function is going to move the file into the test and train folders according with the split_size
    """

    def round_up_to_even(f):
        return math.ceil(f / 2.) * 2

    for i in os.listdir(images_collected_path):
        
        counter = 0
        subfolder_path = os.path.join(images_collected_path, i)
        collected_image_size = len([name for name in os.listdir(subfolder_path)])
        
        train_number = round_up_to_even(collected_image_size * split_test_size)

        for root, dirs, files in os.walk(subfolder_path, topdown=False):
            for file in files:
                counter += 1

                # Define new paths
                old_path = os.path.join(root, file)
                new_path_train = os.path.join(train_path, file)
                new_path_test = os.path.join(test_path, file)

                if counter <= train_number:
                    shutil.move(old_path, new_path_train)
                else:
                    shutil.move(old_path, new_path_test)

        print(f'Folder: {i}\n\
        Train number: {train_number}\n\
        Test number: {collected_image_size - train_number}\n\
        Number of files {counter}', end='\n\n')



if __name__ == '__main__':
    train_test_split(args.collected_path,
                     args.train_path,
                     args.test_path,
                     args.test_size)
