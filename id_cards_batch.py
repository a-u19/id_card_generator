import pandas as pd
from PIL import Image, ImageDraw, ImageFont

def open_file(file_name:str):
    return open(file_name)

def open_excel(excel_file_name:str):
    return pd.read_excel(excel_file_name, header=0)

def make_id_card(template_pic, teacher_first_name: str, teacher_last_name: str, teacher_num: str, dbs_num: int) -> None:
    teacher_first_name, teacher_last_name = teacher_first_name.lower(), teacher_last_name.lower()
    # Load the template and profile picture
    template = Image.open(template_pic)
    profile_pic = Image.open(f'pics\\{teacher_first_name}_{teacher_last_name}.jpg').resize((750, 700))  # Resize profile picture to fit the "PICTURE" box
    
    # Define positions for each element in the template
    picture_position = (765, 1400)  # Coordinates for profile picture
    name_position = (800, 2270)     # Coordinates for the name
    staff_num_position = (790, 2600)  # Coordinates for staff number
    dbs_num_position = (800, 3000)    # Coordinates for DBS number

    # Paste the profile picture onto the template at the specified position
    template.paste(profile_pic, picture_position)

    # Initialize ImageDraw
    draw = ImageDraw.Draw(template)
    
    # Load a font
    try:
        font = ImageFont.truetype("arial.ttf", 72)  # Use a basic font and size; adjust path if needed
    except IOError:
        font = ImageFont.load_default()  # Fallback to default font if "arial.ttf" is not available

    # Draw text for each field
    name_text = f"{teacher_first_name.capitalize()} {teacher_last_name.capitalize()}"
    draw.text(name_position, name_text, fill="white", font=font)
    draw.text(staff_num_position, f"Staff Number: {teacher_num}", fill="white", font=font)
    draw.text(dbs_num_position, f"DBS Number: {dbs_num}", fill="white", font=font)

    # Save the final ID card
    template.save(f"pics\\{teacher_first_name}_{teacher_last_name}_id_card_output.jpg")
    print(f"ID card saved as '{teacher_first_name}_{teacher_last_name}_id_card_output.jpg'")


def main():
    teacher_details = open_excel("teacher_details.xlsx")
    for teacher in teacher_details.iterrows():
        make_id_card("template_id.jpg", teacher[1].get('First Name'), teacher[1].get('Last Name'), teacher[1].get('Teacher Number'), teacher[1].get('DBS Number'))


main()