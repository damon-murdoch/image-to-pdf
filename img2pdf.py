import os, time

import argparse
import tempfile

# Zip File Library
import zipfile

# Python PDF library
import PyPDF2

# Python image library
from PIL import Image

parser = argparse.ArgumentParser(description="Image to Pdf Converter")
parser.add_argument(
    "path",
    type=str,
    nargs="+",
    help="Path (or list of paths) to convert into pdf files",
)
parser.add_argument(
    "-a",
    "--archive",
    action="store_true",
    required=False,
    help="If this switch is set, archive files (e.g. cbz) will be extracted and processed",
)
parser.add_argument(
    "-o",
    "--output",
    type=str, 
    required=False,
    help="temp",
)


# make_pdf(path: String, writer: PdfWriter): Void
# Given a folder path string and an (optional) PdfWriter
# object, builds a pdf using all of the image files in the folder
# (Sorted by file name) and writes it.
def make_pdf(path, output, writer=None):

    filename = f"{os.path.basename(path)}.pdf"

    # Generate the output filepath
    outpath = os.path.join(output, filename)

    if not os.path.exists(outpath):

        # List of images in the folder
        images = []

        # If no writer object is provided
        if not writer:
            # Create a new PdfWriter object
            writer = PyPDF2.PdfWriter()

        # Loop over all of the files in the directory
        for file in os.listdir(path):

            # Get the path for the specific file
            file_path = os.path.join(path, file)

            # If the file is an image
            if is_image(file_path):

                # Add the image to the image list
                images.append(file_path)

        # Loop over all of the images
        for image in range(len(images)):

            # Open the image file
            img = Image.open(images[image])

            # Get the width and height of the image
            # w,h = img.size

            img_name = images[image] + ".pdf"

            # Save the image in a temporary pdf at maximum resolution
            img.save(img_name, "PDF", resolution=100.0)

            wait = 10  # Time to wait (seconds)
            counter = 0  # Time Counter (seconds)

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
                page = PyPDF2.PdfReader(images[image] + ".pdf")

                # Add the page from the temporary pdf to the main pdf
                writer.add_page(page.pages[0])

                # Remove the temporary pdf
                os.remove(images[image] + ".pdf")

            else:  # No file created

                print(
                    "File not opened: File '" + img_name + "' not created! Skipping ..."
                )

        # If there is at LEAST one page created in the main pdf
        if len(writer.pages) > 0:

            # Save the main pdf
            writer.write(open(outpath, "wb"))

        else:  # Filename not present

            print("Not processing folder:", path, "...")

    else:  # Skipped creating pdf
        print(f"Skipped creating pdf '{outpath}' (already created)")


# Check if the file is an image
def is_image(filename):

    # Valid image file extensions
    EXTENSIONS = [".png", ".jpg", ".jpeg", ".tiff"]

    # Loop over the extensions
    for extension in EXTENSIONS:

        # If the filename contains the extension
        if extension in filename:

            # File is image, return true
            return True

    return False


# Check if the file is an archive
def is_archive(filename):

    # Valid archive file extensions
    EXTENSIONS = [".cbz", ".zip"]

    # Loop over all of the extensions
    for extension in EXTENSIONS:

        # If the filename contains the extension
        if extension in filename:

            # File is image, return true
            return True

    return False


def extract_archive(filename):

    # Path to extract to, file extension
    extract_path, _ = os.path.splitext(filename)
    extract_folder = os.path.basename(extract_path)

    # Get the path to the temp dir
    temp_dir = tempfile.gettempdir()
    target_path = os.path.join(temp_dir, extract_folder)

    # Path does not exist
    if not os.path.exists(target_path):

        # Open the zip file
        with zipfile.ZipFile(filename, "r") as zip:

            # Extract archive to 'extract_to'
            zip.extractall(target_path)

    else:  # Path already exists
        print(f"Skipped extracting archive '{filename}' (already extracted)")

    return target_path


# get_subfolders(path: String): [List, List]
# Given a folder path, returns all of the sub
# folders and image files in the directory and
# returns them as a tuple.
def get_subfolders(path, archive=False):

    # Path subpaths
    paths = []

    # Loop over all of the files in the directory
    for file in os.listdir(path):

        # Create the full file path for the given file
        file_path = os.path.join(path, file)

        # If the file path is a directory
        if os.path.isdir(file_path):

            # Add the path to the paths list
            paths.append(file_path)

        elif is_archive(file_path) and archive == True:

            # Extract the archive and add path to list
            paths.append(extract_archive(file_path))

    # Loop over the paths
    for folder in paths:

        # Loop over all of the subfolders (again)
        subpaths = get_subfolders(folder, archive)

        # Loop over all of the paths
        for p in subpaths:

            # Add the paths to the list
            paths.append(p)

    # Return the paths list and images list as a tuple
    return paths


# Main Function
if __name__ == "__main__":

    # Parse the arguments
    args = parser.parse_args()

    # Loop over the 'root' paths
    for root_path in args.path:

        # List of paths
        paths = [root_path]

        # Use 'root_path' or output
        output = args.output or root_path

        # Create the output folder, if required
        os.makedirs(output, exist_ok=True)

        # Loop over the paths
        while len(paths) > 0:
            directory = paths.pop()

            # Get all of the subfolders in the directory
            paths += get_subfolders(directory, args.archive)

            # Make the pdf for the folder
            make_pdf(directory, output)
