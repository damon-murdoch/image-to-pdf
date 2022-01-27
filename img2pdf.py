# Operating System libraries
import sys, os

# Python PDF library
import PyPDF2

# For waiting for the file to create
import time

# Python progress bar library
from tqdm import tqdm

# Python image library
from PIL import Image

# make_pdf(path: String, writer: PdfFileWriter): Void
# Given a folder path string and an (optional) PdfFileWriter
# object, builds a pdf using all of the image files in the folder
# (Sorted by file name) and writes it.
def make_pdf(path,writer=None):

    # List of images in the folder
    images = []

    # If no writer object is provided
    if(not writer):
        # Create a new PdfFileWriter object
        writer = PyPDF2.PdfFileWriter()

    # Loop over all of the files in the directory
    for file in os.listdir(path):

        # Get the path for the specific file
        file_path = os.path.join(path, file)

        # If the file is an image
        if is_image(file_path):

            # Add the image to the image list
            images.append(file_path)

    # Loop over all of the images
    for image in tqdm(range(len(images))):

        # Open the image file
        img = Image.open(images[image])

        # Get the width and height of the image
        # w,h = img.size

        img_name = images[image] + ".pdf"

        # Save the image in a temporary pdf at maximum resolution
        img.save(img_name, "PDF", resolution = 100.0)

        wait = 10 # Time to wait (seconds)
        counter = 0 # Time Counter (seconds)

        # While the file has not been created
        while not os.path.exists(img_name):

            # Wait 1 second
            time.sleep(1)

            # Add one to the counter
            counter += 1

            # If we have exceeded the wait limit
            if counter > wait: 

                # Exit the loop
                break

        # Verify the file has been created 
        if os.path.exists(img_name):

            # Create a pdf file reader for the temporary pdf
            page = PyPDF2.PdfFileReader(images[image] + ".pdf")

            # Add the page from the temporary pdf to the main pdf
            writer.addPage(page.getPage(0))
            
            # Remove the temporary pdf
            os.remove(images[image] + ".pdf")

        else: # No file created

            print("File not opened: File '" + img_name + "' not created! Skipping ...")

    # If there is at LEAST one page created in the main pdf
    if writer.getNumPages() > 0:
        
        # Save the main pdf
        writer.write(open(path + ".pdf", "wb"))

    else: # Filename not present

        print("Not processing folder:", path, "...")

        

# Check if the file is an image
def is_image(filename):

    # Valid image file extensions
    EXTENSIONS = [
        '.png', '.jpg', '.jpeg', '.tiff'
    ]

    # Loop over all of the extensions
    for extension in EXTENSIONS:

        # If the filename contains the extension
        if extension in filename:

            # File is image, return true
            return True

    return False

# get_subfolders(path: String): [List, List]
# Given a folder path, returns all of the sub 
# folders and image files in the directory and
# returns them as a tuple.
def get_subfolders(path):

    # Path subpaths
    paths = []

    # Path images
    images = []

    # Loop over all of the files in the directory
    for file in os.listdir(path):

        # Create the full file path for the given file
        file_path = os.path.join(path, file)

        # If the file path is a directory
        if os.path.isdir(file_path):

            # Add the path to the paths list
            paths.append(file_path)

        # If the file path is an image
        elif is_image(file_path):

            # Add the path to the images list
            images.append(file_path)

    # Loop over the paths
    for folder in paths:

        # Loop over all of the subfolders (again)
        subpaths,subimages = get_subfolders(folder)

        # Loop over all of the paths
        for p in subpaths:

            # Add the paths to the list
            paths.append(p)

        # Loop over all of the images
        for i in subimages:

            # Add the images to the list
            images.append(i)

    # Return the paths list and images list as a tuple
    return paths,images

# Main Function
if __name__ == '__main__':

    # List of paths
    paths = []

    # List of images
    images = []

    # If more than one argument is provided
    if len(sys.argv) > 1:

        # Loop over all of the ar guments
        for directory in sys.argv[1:]:

            # Add the directory to the list
            paths.append(directory)

            # Get all of the subfolders in the directory
            p,i = get_subfolders(directory)

            # Add all of the subfolders to the paths list
            for x in p:
                paths.append(x)

            # Add all of the images to the images list
            for x in i:
                images.append(i)

        print("Number of Directories: "+str(len(paths)))
        print("Number of Images: "+str(len(images)))

        # Loop over all of the paths, printing the progress bar
        for folder in tqdm(range(len(paths))):

            # Make the pdf for the folder
            make_pdf(paths[folder])

    else: # No arguments provided
        print("Please drag the folder containing the images to convert onto this file!")