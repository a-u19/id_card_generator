from PIL import Image, ImageOps
import os


def collate_images(image_files, image_folder, output_file, image_size, margin, gap, a4_size, iteration_num):
    """
    Collates images into a single file for printing on A4 paper with gaps.

    :param image_files: Path to the images
    :param image_folder: Path to the folder containing images
    :param output_file: Path to save the output image
    :param image_size: Tuple (width, height) of each image in pixels
    :param margin: Space (in pixels) around the grid of images
    :param gap: Space (in pixels) between images
    :param a4_size: Size of A4 paper at 600 dpi
    :param iteration_num: Creates multiple a4 pages and labels appropriately
    """
    a4_width, a4_height = a4_size[0], a4_size[1]

    # Load all images from the folder
    if not image_files:
        print("No images found in the folder.")
        return

    # Determine the number of rows and columns that fit on A4
    images_per_row = (a4_width - 2 * margin + gap) // (image_size[0] + gap)

    # Create a blank canvas for A4
    canvas = Image.new("RGB", (a4_width, a4_height), "white")

    # Add images to the canvas
    x, y = margin, margin
    for idx, img_file in enumerate(image_files):
        img_path = image_folder + img_file
        img = Image.open(img_path).resize(image_size)

        # Paste the image onto the canvas
        canvas.paste(img, (x, y))
        x += image_size[0] + gap

        # Move to the next row if the current row is full
        if (idx + 1) % images_per_row == 0:
            x = margin
            y += image_size[1] + gap

        # Stop if the canvas is full
        if y + image_size[1] + gap > a4_height:
            break

    output_file = f"{output_file}_{iteration_num}.png"
    # Save the resulting image
    canvas.save(output_file, quality=100, optimize=True)
    print(f"Collated image saved to {output_file}")



from PIL import Image, ImageOps
import os

def images_to_pdf(image_folder, output_pdf, a4_size=(4960, 7016), dpi=600):
    """
    Creates a PDF from images, ensuring proper A4 size and DPI for printing.

    :param image_folder: Path to the folder containing images
    :param output_pdf: Path to save the output PDF
    :param a4_size: Tuple (width, height) representing A4 size in pixels
    :param dpi: DPI (dots per inch) for the PDF output
    """
    # Ensure the output directory exists
    output_dir = os.path.dirname(output_pdf)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Get a list of all image files in the folder
    image_files = [
        os.path.join(image_folder, f)
        for f in os.listdir(image_folder)
        if "collated" in f
    ]

    if not image_files:
        print("No image files found in the specified folder.")
        return

    # Sort files to maintain order
    image_files.sort()

    # Open the images and resize them to A4 if necessary
    image_list = []
    for file in image_files:
        img = Image.open(file)
        img = img.convert("RGB")  # Convert to RGB for PDF compatibility

        # Resize or pad to match A4 size
        if img.size != a4_size:
            img = ImageOps.pad(img, a4_size, color="white")  # Adds white padding if needed

        image_list.append(img)

    # Save images as a single PDF with DPI
    if image_list:
        image_list[0].save(
            output_pdf,
            save_all=True,
            append_images=image_list[1:],
            quality=100,
            resolution=dpi  # Embed the DPI
        )
        print(f"PDF created successfully: {output_pdf}")
    else:
        print("No valid images were found to create the PDF.")



def main(margin:int, gap:int, image_folder:str, a4_width:int = 4960, a4_height:int = 7016):

    image_files = [f for f in os.listdir(image_folder) if f.lower()[-10:] == 'output.png']
    if len(image_files) == 0:
        exit("No image files found")
    image_size = Image.open(image_folder + image_files[0]).size

    max_pics_per_row  = (a4_width - (2 * margin + gap)) // (image_size[0] + gap)
    max_pics_per_col  = (a4_height - (2 * margin + gap)) // (image_size[1] + gap)

    total_num_pics = len(image_files)

    max_pics_per_page = max_pics_per_col * max_pics_per_row

    iterations = (total_num_pics + max_pics_per_page - 1) // max_pics_per_page

    for iteration in range(iterations):
        selected_images = image_files[iteration * max_pics_per_page : (iterations + 1) * max_pics_per_page]
        collate_images(
            image_files=selected_images,
            image_folder='../teacher_id_card_files/teacher_images/',
            output_file="../teacher_id_card_files/to_be_printed/collated",
            image_size=image_size,
            margin=margin,
            gap=gap,
            a4_size=tuple((a4_width, a4_height)),
            iteration_num=iteration)
        print(f"Pictures {iteration * max_pics_per_page} to {(iteration + 1) * max_pics_per_page} collated")
        images_to_pdf("../teacher_id_card_files/to_be_printed", "../teacher_id_card_files/to_be_printed/output.pdf")


main(100, 100, '../teacher_id_card_files/teacher_images/')