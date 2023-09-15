import zipfile
import os

def list_files(zip_file, full_path):
    for file_info in zip_file.infolist():
        file_name = os.path.join(full_path, file_info.filename)
        print(file_name)

def zip_search(file_path, full_path=""):
    with zipfile.ZipFile(file_path, 'r') as zip_file:
        full_path = os.path.join(full_path, zip_file.filename)
        list_files(zip_file, full_path)
        for file_info in zip_file.infolist():
            if file_info.filename.endswith('.zip'):
                nested_zip_file = zip_file.open(file_info.filename)
                zip_search(nested_zip_file, full_path)

def rec_search(directory_path):
    for root, _, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            if file_path.endswith('.zip'):
                zip_search(file_path)

# folder with zip files, not Tenders.zip
# actually search recursively through everything, I think ...
search_path = r"C:/Users/Mitch/Tenders"
rec_search(search_path)