import zipfile
import os
import pandas as pd

def list_files(current_zip, corpus, zip_file, full_path):
    for file_info in zip_file.infolist():
        file_name = os.path.join(full_path, file_info.filename)

        if file_name.lower().endswith(('doc', 'docx')):
            # read doc function
            doc_data = read_doc(file_name)
            add(corpus, current_zip, doc_data)

        elif file_name.lower().endswith('pdf'):
           # read pdf function
           pdf_data = read_pdf(file_name)
           add(corpus, current_zip, pdf_data)
                 
        elif file_name.lower().endswith(('jpg', 'png')):
            # ocr function
            image_data = ocr(file_name)
            add(corpus, current_zip, image_data)

        #print(file_name)

def zip_search(current_zip, corpus, file_path, full_path=""):
    with zipfile.ZipFile(file_path, 'r') as zip_file:
        full_path = os.path.join(full_path, zip_file.filename)
        list_files(current_zip, corpus, zip_file, full_path)
        for file_info in zip_file.infolist():
            if file_info.filename.endswith('.zip'):
                nested_zip_file = zip_file.open(file_info.filename)
                zip_search(current_zip, corpus, nested_zip_file, full_path)

def rec_search(corpus, directory_path):
    file_count = 0

    for root, _, files in os.walk(directory_path):
        for file in files:
            file_count += 1
            if file_count >= 10:  # test first 10 files
                return    

            file_path = os.path.join(root, file)
            if file_path.endswith('.zip'):
                parts = file_path.split(os.path.sep)
                current_zip = parts[-1].split("-specification.zip")[0]
                zip_search(current_zip, corpus, file_path)

def add_base(corpus, tenders_data):
    for index, row in tenders_data.iterrows():
        ref = row["Reference Number"]
        title = row["Contract Title"]
        desc = row["Description"]

        combined = f"{title}. {desc}"
        add(corpus, ref, combined)

def add(corpus, current_zip, data):
    if current_zip in corpus:
        corpus[current_zip].append(data)
    else:
        corpus[current_zip] = [data]

# insert all read functions here per file type

def read_doc(doc_file):
    # extract text from doc
    doc_data = doc_file
    return doc_data

def read_pdf(pdf_file):
    # extract text from pdf
    pdf_data = pdf_file
    return pdf_data

def ocr(image_file):
    # extract text from image
    image_data = image_file
    return image_data

# folder with zip files, not Tenders.zip
# actually search recursively through everything, I think ...
corpus = {}

tenders_data_path = r"C:/Users/Mitch/git/UWACapstoneG2/data/UpdatedAgainTenders.xlsx"
tenders_data = pd.read_excel(tenders_data_path)
tenders_data = tenders_data[["Reference Number", "Contract Title", "Description"]].dropna(subset=["Reference Number"]).drop_duplicates()

add_base(corpus, tenders_data)

# search for extra information
search_path = r"C:/Users/Mitch/Tenders"
#rec_search(corpus, search_path)

for key, value in corpus.items():
    print(f"{key}: {value}")
    print("<=============>")