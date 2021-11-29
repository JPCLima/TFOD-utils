from PIL import Image, ImageEnhance, ImageFilter
from random import randint
import os
import random
import uuid
import numpy as np
import xml.etree.cElementTree as ET
from pathlib import Path
import argparse

# Initiate argument parser
parser = argparse.ArgumentParser(
    description="Generate a labelmap")

parser.add_argument("-p",
                    "--path",
                    type=str,
                    help="path to directory of bg and mask up folder")

parser.add_argument("-n",
                    "--number_img",
                    help="number of random images generated")

args = parser.parse_args()


def get_random_img(subfolder_path):
    """ Return random path file from the subfolder"""
    return os.path.join(subfolder_path, random.choice(os.listdir(subfolder_path)))

def generate_random_image_name():
    """ Generate random name for the images"""
    return 'random-' + str(uuid.uuid1()) + '.png'
   
def get_imgs_folder(random_images_path):
    """ Creates a new directory if doesnt exist and return path for image with random ID """
    random_images = random_images_path
    if not os.path.exists(random_images):
        os.mkdir(random_images)
    return os.path.join(os.getcwd(),random_images, generate_random_image_name())

def generate_random_image(bg_path, mask_path, random_images_path):  
    """ Generate an image with random images as random mask on the top of random background, 
        as well create the anotations of the masks"""

    # Generate image name
    img_name = get_imgs_folder(random_images_path)
    # Load background
    background = Image.open(bg_path)
    # Resize the background
    background = background.resize((700,900),resample=Image.LANCZOS)
    # Copy the background
    render_img = background.copy()
    # Get ranndom background random Brightnes
    en = ImageEnhance.Brightness(render_img)
    random_brightness = random.uniform(0.8,1.0)
    render_img = en.enhance(random_brightness)
    anotation_list = []

    # Get the coordinates of the drink
    for y in range(0, render_img.height, render_img.height//2):
        for x in range(0, render_img.width, (render_img.width +100 )//5):
            # Load random position of drink
            random_mask = get_random_img(mask_path)        
            # Load mask
            mask = Image.open(random_mask)
            # Keep the apsect ratio of the object when they are scaled
            aspect = mask.width/mask.height
            # Get random size
            drink_size = randint(200,400)
            # Get dimension
            w = int(drink_size*aspect)
            # Resize image
            mask_2 = mask.resize((w,drink_size),resample=Image.LANCZOS)
            # Change Brightnes mask
            en = ImageEnhance.Brightness(mask_2)
            random_brightness = random.uniform(0.5,1)
            mask_2 = en.enhance(random_brightness)
            # Change blur
            random_blur = random.randint(0, 2)
            mask_2 = mask_2.filter(ImageFilter.GaussianBlur(radius = random_blur))
            # Rotation mask
            random_roation = random.randint(-5, 5)
            mask_2 = Image.Image.rotate(mask_2,random_roation,resample=Image.BICUBIC,expand=True)
            # Paste random image on the bg
            render_img.paste(mask_2,(x,y),mask_2)
            # anotations string          
            xmin, ymin, xmax, ymax = x, y, x + mask_2.width, y + mask_2.height
            # If the mask is out of the mask, get the width of the mask
            if xmax > render_img.width:
                xmax = render_img.width
            # Create the anotation string & append to anotation_list
            mask_name = os.path.basename(random_mask).split('-')[0]
            anotation_str = ','.join(map(str, [xmin, ymin, xmax, ymax, mask_name]))            
            anotation_list.append(anotation_str)
    # Save the fiile on the folder
    render_img.save(img_name)
    # Create anotation file
    create_labimg_xml(img_name, anotation_list)

def generate_mutiple_random_img(number_imgs, bg_path, mask_path, random_images_path):
    """ This function returns n number of random images"""
    for img in range(number_imgs):
        generate_random_image(get_random_img(bg_path), mask_path, random_images_path)

def create_labimg_xml(image_path, annotation_list):
    """ Returns an xml file with the annotations"""

    image_path = Path(image_path)
    img = np.array(Image.open(image_path).convert('RGB'))

    annotation = ET.Element('annotation')
    ET.SubElement(annotation, 'folder').text = str(image_path.parent.name)
    ET.SubElement(annotation, 'filename').text = str(image_path.name)
    ET.SubElement(annotation, 'path').text = str(image_path)

    source = ET.SubElement(annotation, 'source')
    ET.SubElement(source, 'database').text = 'Unknown'

    size = ET.SubElement(annotation, 'size')
    ET.SubElement(size, 'width').text = str (img.shape[1])
    ET.SubElement(size, 'height').text = str(img.shape[0])
    ET.SubElement(size, 'depth').text = str(img.shape[2])

    ET.SubElement(annotation, 'segmented').text = '0'

    for annot in annotation_list:
        tmp_annot = annot.split(',')
        cords, label = tmp_annot[0:-1], tmp_annot[-1]
        xmin, ymin, xmax, ymax = cords[0], cords[1], cords[2], cords[3]

        object = ET.SubElement(annotation, 'object')
        ET.SubElement(object, 'name').text = label
        ET.SubElement(object, 'pose').text = 'Unspecified'
        ET.SubElement(object, 'truncated').text = '0'
        ET.SubElement(object, 'difficult').text = '0'

        bndbox = ET.SubElement(object, 'bndbox')
        ET.SubElement(bndbox, 'xmin').text = str(xmin)
        ET.SubElement(bndbox, 'ymin').text = str(ymin)
        ET.SubElement(bndbox, 'xmax').text = str(xmax)
        ET.SubElement(bndbox, 'ymax').text = str(ymax)

    tree = ET.ElementTree(annotation)
    xml_file_name = image_path.parent / (image_path.name.split('.')[0]+'.xml')
    tree.write(xml_file_name)

if __name__ == '__main__':    
    PATH = args.path
    NUMBER_IMAGES = int(args.number_img)

    BG_PATH = os.path.join(PATH, 'bg')
    MASK_PATH = os.path.join(PATH, 'mask')
    RANDOM_IMG_PATH = os.path.join(PATH, 'random_images')
    generate_mutiple_random_img(NUMBER_IMAGES, BG_PATH, MASK_PATH, RANDOM_IMG_PATH)
    