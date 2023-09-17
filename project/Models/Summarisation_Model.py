import zipfile
import os
import pandas as pd
from bs4 import BeautifulSoup

def list_files(ref, corpus, zip_file, full_path):
    for file_info in zip_file.infolist():
        file_name = os.path.join(full_path, file_info.filename)

        if file_name.lower().endswith(('doc', 'docx')):
            # read doc function
            doc_data = read_doc(file_name)
            add(corpus, ref, doc_data)

        elif file_name.lower().endswith('pdf'):
           # read pdf function
           pdf_data = read_pdf(file_name)
           add(corpus, ref, pdf_data)
                 
        elif file_name.lower().endswith(('jpg', 'png')):
            # ocr function
            image_data = ocr(file_name)
            add(corpus, ref, image_data)

        #print(file_name)

def zip_search(ref, corpus, file_path, full_path=""):
    with zipfile.ZipFile(file_path, 'r') as zip_file:
        full_path = os.path.join(full_path, zip_file.filename)
        list_files(ref, corpus, zip_file, full_path)
        for file_info in zip_file.infolist():
            if file_info.filename.endswith('.zip'):
                nested_zip_file = zip_file.open(file_info.filename)
                zip_search(ref, corpus, nested_zip_file, full_path)

def rec_search(corpus, directory_path):
    file_count = 0

    for root, _, files in os.walk(directory_path):
        for file in files:
            file_count += 1
            if file_count >= 500:  # test first 500 files
                return    

            file_path = os.path.join(root, file)
            if file_path.endswith('.zip'):
                parts = file_path.split(os.path.sep)
                ref = parts[-1].split("-specification.zip")[0]
                zip_search(ref, corpus, file_path)

def add_base(corpus, tenders_data):
    for index, row in tenders_data.iterrows():
        ref = str(row["Reference Number"])
        title = row["Contract Title"]
        desc = remove_html_tags(row["Description"])

        combined = f"{title}. {desc}"
        add(corpus, ref, combined)

def add(corpus, ref, data):
    if ref in corpus:
        corpus[ref].append(data)
    else:
        corpus[ref] = [data]

def remove_html_tags(text):
    soup = BeautifulSoup(text, "html.parser")
    cleaned = soup.get_text().replace('\xa0', ' ')
    cleaned = ' '.join(cleaned.split())
    return cleaned

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

def main(tenders_data_path, search_path):
    corpus = {}

    tenders_data = pd.read_excel(tenders_data_path)
    tenders_data = tenders_data[["Reference Number", "Contract Title", "Description"]].dropna(subset=["Reference Number"]).drop_duplicates()

    # add title and short description as base data
    add_base(corpus, tenders_data)

    # get available extra information from specification documents
    rec_search(corpus, search_path)

    return corpus

# folder with zip files, not Tenders.zip
# actually search recursively through everything, I think ...
tenders_data_path = r"C:/Users/Mitch/git/UWACapstoneG2/data/UpdatedAgainTenders.xlsx"
search_path = r"C:/Users/Mitch/Tenders"

corpus = main(tenders_data_path, search_path)
#for key, value in corpus.items():
#    print(f"{key}: {value}")
#    print("<=============>")

print(corpus['BMW0104219'])