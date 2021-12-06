import os
import random
import uuid
from PIL import Image, ImageEnhance, ImageFilter
import xml.etree.cElementTree as ET
import numpy as np
from pathlib import Path
import itertools
import argparse

# Initiate argument parser
parser = argparse.ArgumentParser(
    description="Generate a labelmap")

parser.add_argument("-p",
                    "--path",
                    type=str,
                    help="patssssssssssh to directory of bg and mask up folder")

parser.add_argument("-n",
                    "--number_img",
                    help="number of random images generated")

args = parser.parse_args()


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

def get_random_bg(subfolder_path):
    """ Return random path file from the subfolder
    """
    return os.path.join(subfolder_path, random.choice(os.listdir(subfolder_path)))

def get_random_mask(subfolder_path, type):
    """ This function returns a random image file. The type 1 return Cola, the type 2 return Pepsi"""
    if type == 'Cola':
        img_list = [ x for x in os.listdir(subfolder_path) if x.startswith('Cola')]
    elif type == 'Pepsi':
        img_list = [ x for x in os.listdir(subfolder_path) if x.startswith('Pepsi')]
    return os.path.join(subfolder_path, random.choice(img_list))

def generate_random_image_name():
    """ Generate random name for the images
    """
    return 'random-' + str(uuid.uuid1()) + '.png'
   
def get_imgs_folder(random_images_path):
    """ Creates a new directory if doesnt exist and return path for image with random ID
    """
    random_images = random_images_path
    if not os.path.exists(random_images):
        os.mkdir(random_images)
    return os.path.join(os.getcwd(),random_images, generate_random_image_name())

def abs_position(x, y, bg, mask):
    """ This function returns the absolute value of the position
    """
    if (x < 0): x = 0
    if (y < 0): y = 0
    if (x > bg.width): x = bg.width
    if (y > bg.height): y = bg.height
    return x, y

def random_size(img):
    """ This function changes the brightness of image with random value
    """
    aspect = img.width/img.height
    img_size = random.randint(400,700)
    w = int(img_size*aspect)
    return img.resize((w,img_size),resample=Image.LANCZOS)

def random_brightness(img):
    """ This function changes the brightness of image with random value
    """
    en = ImageEnhance.Brightness(img)
    random_brightness = random.uniform(0.3,1)
    return en.enhance(random_brightness)

def random_blur(img):
    """ This function changes the blur of image with random value
    """
    random_blur = random.randint(1, 2)
    return img.filter(ImageFilter.GaussianBlur(radius = random_blur))

def random_rotation(img):
    """ This function changes the rotation of image with random value
    """
    random_roation = random.randint(-5, 5)
    return Image.Image.rotate(img,random_roation,resample=Image.BICUBIC,expand=True)

def transform_image(mask):
    """  This function modifies the size, Brightnes, Blur and rotation of the image
    """
    mask = random_size(mask)
    mask = random_brightness(mask)
    mask = random_blur(mask)
    mask = random_rotation(mask)
    
    return mask

def generate_random_image(folders_path, type):    

    # Generate image name
    img_name = generate_random_image_name()
    image_path = os.path.join(folders_path, 'random_images', img_name)

    # Paths
    path_mask = os.path.join(folders_path, 'mask')
    path_bg = os.path.join(folders_path, 'bg')   

    # Get and resize background
    bg = get_random_bg(path_bg)
    bg = Image.open(bg)
    bg = bg.resize((700,900),resample=Image.LANCZOS)

    # Random bg brightness
    bg = random_brightness(bg)
    
    # Get random mask image
    random_mask = get_random_mask(path_mask, type)
    mask_name = os.path.basename(random_mask).split('-')[0]
    mask = Image.open(random_mask)    

    # Position of mask
    x = random.randint(-int(mask.width/3),bg.width - int(3*mask.width/2))
    y = random.randint(-int(mask.height/3),bg.height - int(3*mask.height/2))

    # Transform mask and save
    render_img = bg.copy()
    mask = transform_image(mask)
    render_img.paste(mask,(x,y),mask)

    # Save image
    render_img.save(image_path)
     

    # Make sure the anotation will in the range
    anotation_list = []
    xmin, ymin = abs_position(x, y, bg, mask)
    xmax, ymax = abs_position(x + mask.width, y + mask.height, bg, mask)

    anotation_str = ','.join(map(str, [xmin, ymin, xmax, ymax, mask_name]))            
    anotation_list.append(anotation_str)
    return image_path, anotation_list    

if __name__ == '__main__': 
    PATH = args.path
    NUMBER_IMAGES = int(args.number_img)
    print(f"Generating {NUMBER_IMAGES} images ...")

    toggle = itertools.cycle(['Cola', 'Pepsi'])
    for i in range(NUMBER_IMAGES):
        image_path, anotation_list = generate_random_image(PATH, type=next(toggle))
        create_labimg_xml(image_path, anotation_list)