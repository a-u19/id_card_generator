import pandas as pd
import cv2
import pytesseract
from thefuzz import fuzz


def open_file(file_name: str):
    return open(file_name)


def open_excel(excel_file_name: str):
    return pd.read_excel(excel_file_name, header=0)


def replace(img_filepath: str, teacher_first_name: str, teacher_last_name: str, teacher_num: str, dbs_num: int,
            teaching_staff: bool, pfp_filepath: str, students: bool) -> None:
    # Load the image
    img = cv2.imread(img_filepath)
    pfp = cv2.imread(pfp_filepath)
    resources = [img, teacher_first_name, teacher_last_name, teacher_num, dbs_num, pfp]
    for resource in resources:
        if resource is None:
            print("Missing teacher details are as follows: "
                  f"\nTemplate img:{img is not None} \n"
                  f"teacher_first_name:{teacher_first_name} \n"
                  f"teacher_last_name:{teacher_last_name} \n"
                  f"teacher_num:{teacher_num} \n"
                  f"dbs_num:{dbs_num} \n"
                  f"pfp:{pfp is not None}"
                  f"teaching staff bool:{teaching_staff is not None}")
            return
    # cv2.imshow("hi", pfp)
    # cv2.waitKey(0)

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
    pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

    # Iterate through contours and process rectangles
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        # print(w,h)

        # Filter for rectangular regions that are significant
        if 1400>=w>=700:
            # print(w,h)
            # Draw rectangles on the original image for visualization

            # Extract the ROI for OCR
            roi = gray[y:y + h, x:x + w]
            roi = cv2.adaptiveThreshold(roi, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
            text = pytesseract.image_to_string(roi, lang='eng', config='--psm 1').strip()

            # print(text)

            # Prepare replacement text based on OCR detection
            replacement_text = ""
            if fuzz.partial_ratio("name", text.lower()) > 90:
                replacement_text = f"{teacher_first_name} {teacher_last_name}"
            elif fuzz.partial_ratio("teacher number", text.lower()) > 90:
                replacement_text = f"Teacher Number: {teacher_num}"
            elif fuzz.partial_ratio("dbs number", text.lower()) > 90:
                replacement_text = f"DBS Number: {dbs_num}"
            elif fuzz.partial_ratio("picture", text.lower()) > 90:
                replacement_text = "PICTURE"
            elif fuzz.partial_ratio("teaching staff", text.lower()) > 90:
                replacement_text = "TEACHING STAFF" if teaching_staff else "ADMIN STAFF"

            # print(replacement_text)

            if replacement_text != "PICTURE":

                # Draw the filled rectangle, leaving space for the outline
                cv2.rectangle(annotated_img, (x + 5, y + 5), (x + w - 5, y + h - 5), (223, 255, 158), thickness=-1)
                # Calculate text size to center it
                text_size = cv2.getTextSize(replacement_text, cv2.FONT_HERSHEY_SIMPLEX, 1.5, 2)[0]
                text_x = x + (w - text_size[0]) // 2
                text_y = y + (h + text_size[1]) // 2

                # Draw the replacement text in white
                cv2.putText(annotated_img, replacement_text, (text_x, text_y),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 5)

            else:
                resized_pfp = cv2.resize(pfp, (w, h))

                if resized_pfp is not None:
                    annotated_img[y:y + h, x:x + w] = resized_pfp
                    # print(f"Resized profile picture size: {resized_pfp.shape}")  # Check the resized size

                else:
                    print(f"Error: Couldn't resize the profile picture to fit {w}x{h}.")

    output_filepath = pfp_filepath.replace("jpg", "").lower() + "id_card_output.png"
    cv2.imwrite(output_filepath, annotated_img)
    print(f"Outputting {output_filepath}")


def main_teachers():
    teacher_details = open_excel("../teacher_id_card_files/teacher_details.xlsx")
    for teacher in teacher_details.iterrows():
        full_name = f"{teacher[1].get('First Name').lower()}_{teacher[1].get('Last Name').lower()}"
        # print(f'../teacher_id_card_files/{full_name}.jpg')
        replace('teacher_template_id_v3.png', teacher[1].get('First'
                                                  ' Name').title(), teacher[1].get('Last Name').title(),
                teacher[1].get('Teacher Number'), teacher[1].get('DBS Number'), teacher[1].get('Teaching Staff'),
                f'../teacher_id_card_files/teacher_images/{full_name}.jpg')


main_teachers()