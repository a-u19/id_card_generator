import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
import cv2
import pytesseract
from matplotlib import pyplot as plt
from thefuzz import fuzz

def open_file(file_name:str):
    return open(file_name)

def open_excel(excel_file_name:str):
    return pd.read_excel(excel_file_name, header=0)

def replace(img_filepath:str, pfp_filepath:str, teacher_first_name:str, teacher_last_name:str, teacher_num:str, dbs_num:int) -> None:
    # Load the image
    img = cv2.imread(img_filepath)
    pfp = cv2.imread(pfp_filepath)

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply thresholding
    thresh_inv = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Blur the image
    blur = cv2.GaussianBlur(thresh_inv, (1, 1), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Clone the image for visualization
    annotated_img = img.copy()

    # Initialize pytesseract for text extraction
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    # Iterate through contours and process rectangles
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)

        # Filter for rectangular regions that are significant

        if w > 300 and 100 < h < w:
            # Draw rectangles on the original image for visualization

            # Extract the ROI for OCR
            roi = gray[y:y + h, x:x + w]
            roi = cv2.adaptiveThreshold(roi, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
            # plt.imshow(roi, cmap='gray')
            text = pytesseract.image_to_string(roi, lang='eng', config='--psm 11').strip()

            # Prepare replacement text based on OCR detection
            replacement_text = ""
            if fuzz.partial_ratio("name", text.lower()) > 90:
                replacement_text = f"{teacher_first_name} {teacher_last_name}"
            elif fuzz.partial_ratio("teacher number", text.lower()) > 90:
                replacement_text = str(teacher_num)
            elif fuzz.partial_ratio("dbs number", text.lower()) > 90:
                replacement_text = str(dbs_num)

            print(replacement_text)

            if replacement_text:
                # Draw a filled dark blue rectangle (RGB: (0, 0, 128)) to replace the placeholder
                cv2.rectangle(annotated_img, (x, y), (x + w, y + h), (128, 0, 0), -1)

                # Calculate text size to center it
                text_size = cv2.getTextSize(replacement_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
                text_x = x + (w - text_size[0]) // 2
                text_y = y + (h + text_size[1]) // 2

                # Draw the replacement text in white
                cv2.putText(annotated_img, replacement_text, (text_x, text_y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            else:
                resized_pfp = cv2.resize(pfp, (w, h))

                if resized_pfp is not None:
                    annotated_img[y:y + h, x:x + w] = resized_pfp
                    # print(f"Resized profile picture size: {resized_pfp.shape}")  # Check the resized size

                else:
                    print(f"Error: Couldn't resize the profile picture to fit {w}x{h}.")

    # # Display the annotated image
    # plt.figure(figsize=(10, 10))
    # plt.imshow(cv2.cvtColor(annotated_img, cv2.COLOR_BGR2RGB))
    # plt.axis('off')
    # plt.show()

    # write images back to folder
    output_filepath = pfp_filepath.replace("jpg", "").lower() + "id_card_output_v2.png"
    cv2.imwrite(output_filepath, annotated_img)


def main():
    teacher_details = open_excel("../teacher_id_card_files/teacher_details.xlsx")
    for teacher in teacher_details.iterrows():
        full_name = f"{teacher[1].get('First Name')}_{teacher[1].get('Last Name')}"
        replace('template_id.png', f'../teacher_id_card_files/{full_name}.jpg', teacher[1].get('First'
        ' Name'), teacher[1].get('Last Name'), teacher[1].get('Teacher Number'), teacher[1].get('DBS Number'))

main()