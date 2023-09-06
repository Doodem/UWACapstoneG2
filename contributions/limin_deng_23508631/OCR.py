import os
import zipfile
import tempfile
from PIL import Image
import pytesseract


def extract_and_ocr(zip_path, output_dir):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        tender_number = os.path.basename(zip_path).split('.')[0]

        for file_info in zip_ref.infolist():
            if file_info.filename.lower().endswith(('.png', '.jpeg', '.jpg')) and not file_info.filename.startswith(
                    '._'):
                image_name = os.path.basename(file_info.filename)
                image_data = zip_ref.read(file_info.filename)

                temp_image_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
                temp_image_path = temp_image_file.name

                with open(temp_image_path, 'wb') as file:
                    file.write(image_data)

                try:
                    image = Image.open(temp_image_path)
                    image_text = pytesseract.image_to_string(image)

                    text_filename = f"{tender_number}_{image_name}.txt"
                    text_path = os.path.join(output_dir, text_filename)

                    with open(text_path, 'w') as text_file:
                        text_file.write(image_text)

                except Exception as e:
                    print(f"Error processing image {image_name}: {e}")

                os.remove(temp_image_path)  # Delete the temporary file


if __name__ == "__main__":
    main_zip_folder = "/Users/rimito/Library/CloudStorage/OneDrive-TheUniversityofWesternAustralia/Data Science/CITS5553-Capstone/tenders"
    output_text_folder = "/Users/rimito/Library/CloudStorage/OneDrive-TheUniversityofWesternAustralia/Data Science/CITS5553-Capstone/tenders"

    for root, dirs, files in os.walk(main_zip_folder):
        for file in files:
            if file.lower().endswith('.zip'):
                zip_path = os.path.join(root, file)
                extract_and_ocr(zip_path, output_text_folder)
