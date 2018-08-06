import os
import sys

import PyPDF2

from tqdm import tqdm

from PIL import Image

def make_pdf(path,writer=None):

    images = []

    if(not writer):
        writer = PyPDF2.PdfFileWriter()

    for file in os.listdir(path):
        if is_image(path + "/" + file):
            images.append(path + "/" + file)

    for image in range(len(images)):

        img = Image.open(images[image])

        w,h = img.size

        img.save(images[image] + ".pdf","PDF",resolution = 100.0)

        page = PyPDF2.PdfFileReader(images[image] + ".pdf")

        writer.addPage(page.getPage(0))
        os.remove(images[image] + ".pdf")

    if writer.getNumPages() > 0:
        writer.write(open(path+".pdf","wb"))

def is_image(filename):

    if ".png" in filename:
        return True

    if ".jpg" in filename:
        return True

    if ".tiff" in filename:
        return True

    return False

def get_subfolders(path):

    paths = []
    images = []

    for file in os.listdir(path):

        if os.path.isdir(path + "/" + file):
            paths.append(path + "/" + file)

        elif is_image(path + "/" + file):
            images.append(path + "/" + file)

    for folder in paths:

        subpaths,subimages = get_subfolders(folder)

        for p in subpaths:
            paths.append(p)

        for i in subimages:
            images.append(i)

    return paths,images

if __name__ == '__main__':

    paths = []
    images = []

    if len(sys.argv) > 1:
        for directory in sys.argv[1:]:

            paths.append(directory)

            p,i = get_subfolders(directory)

            for x in p:
                paths.append(x)

            for x in i:
                images.append(i)

        print("Number of Directories: "+str(len(paths)))
        print("Number of Images: "+str(len(images)))

        for folder in tqdm(range(len(paths))):
            make_pdf(paths[folder])

    else:
        print("Please drag the folder containing the images to convert onto this file!")