from PIL import Image
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

    # Save the resulting image
    canvas.save(output_file, quality=95, optimize=True)
    print(f"Collated image saved to {output_file}_{iteration_num}.png")

def main(margin:int, gap:int, image_folder:str, a4_width:int = 4960, a4_height:int = 7016):

    image_files = [f for f in os.listdir(image_folder) if f.lower().endswith(('png', 'jpg', 'jpeg'))]
    image_size = Image.open(image_folder + image_files[0]).size

    max_pics_per_row  = (a4_width - 2 * margin + gap) // (image_size[0] + gap)
    max_pics_per_col  = (a4_height - 2 * margin + gap) // (image_size[1] + gap)

    total_num_pics = len(image_files)

    max_pics_per_page = max_pics_per_col * max_pics_per_row

    iterations = total_num_pics//max_pics_per_page

    for iteration in range(iterations):
        selected_images = image_files[iteration * max_pics_per_page : (iterations + 1) * max_pics_per_page]
        collate_images(
            image_files=selected_images,
            image_folder='../teacher_id_card_files/to_be_printed/',
            output_file="../teacher_id_card_files/to_be_printed/collated",
            image_size=image_size,
            margin=50,
            gap=20,
            a4_size=tuple(a4_width, a4_height),
            iteration_num=iteration)


main(50, 20, '../teacher_id_card_files/to_be_printed/')