import zipfile
from zipfile import BadZipFile
import io
import os
import tempfile
import pandas as pd
from bs4 import BeautifulSoup
import PyPDF2
from io import BytesIO    
from docx import Document
from pathlib import Path
import textract
import re
from tqdm import tqdm
import pickle
from concurrent.futures import ProcessPoolExecutor

# READ FUNCTIONS GO HERE 

docs_total = 0
doc_read_failure = 0
def read_doc(file_bytes):
    global docs_total
    global doc_read_failure
    
    docs_total += 1
    content = None
    # first try docx reader function
    try:
        doc = Document(io.BytesIO(file_bytes))
        content = []
        for paragraph in doc.paragraphs:
            content.append(paragraph.text)
        temp = "\n".join(content)
        content = temp
    except Exception as e:
        content = None
    
    # then try textract and slow temp file writing
    if content == None:
        try: # try .doc first 
            temp = tempfile.NamedTemporaryFile(suffix = ".doc")
            temp.write(file_bytes)
            content = textract.process(temp.name)
        except Exception as e:
            content = None
            try: # then .docx..
                temp2 = tempfile.NamedTemporaryFile(suffix = ".docx")
                temp2.write(file_bytes)
                content = textract.process(temp2.name)
            except Exception as e:
                # no dice
                content = None
            finally: 
                temp2.close()
        finally:
            temp.close()
            
    if content != None:
        return content
    else: # nothing worked, so just report a doc read failure
        doc_read_failure += 1
        return content
        
def read_pdf(file_bytes):
    text = ""
    
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
    for page_number in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_number]
        text += page.extract_text()
    return text

def ocr(image_file):
    # extract text from image
    image_data = image_file
    return image_data

bad_zips = 0
def file_handler(tender, zip_file, nested_file_name):
    global bad_zips
    try:
        nested_file_bytes = zip_file.read(nested_file_name)
        if nested_file_name.lower().endswith(('doc', 'docx')):
            doc_data = read_doc(nested_file_bytes)
            tender.add(nested_file_name, doc_data)
        elif nested_file_name.lower().endswith("pdf"):
            pdf_data = read_pdf(nested_file_bytes)
            tender.add(nested_file_name, pdf_data)
    except BadZipFile as badZipException:
        bad_zips += 1

# ----------------------

def zip_search(tender, zip_path, zip_data):
    with zipfile.ZipFile(zip_data, 'r') as zip_file:
        for file_info in zip_file.infolist():
            nested_file_name = file_info.filename
            if nested_file_name.lower().endswith('.zip'):
                try:
                    nested_zip_data = io.BytesIO(zip_file.open(nested_file_name).read())
                    nested_zip_path = os.path.join(zip_path, nested_file_name)
                    zip_search(tender, nested_zip_path, nested_zip_data)
                except BadZipFile as badZipException:
                    bad_zips += 1
            else:
                file_handler(tender, zip_file, nested_file_name)

def begin_thread_zip_task(ref, file_path):
    tender = Tender(ref)
    zip_search(tender, file_path, file_path)
    # save the file
    print(f"saving {ref} ...")
    tender.save()
    print("saved!")     
                        
def rec_search(directory_path):
    for root, _, files in os.walk(directory_path):
        zips_len = len(files)
        with ProcessPoolExecutor() as executor:  
            futures = []
            for file in files:  
                file_path = os.path.join(root, file)
                if file_path.endswith('.zip'):
                    parts = file_path.split(os.path.sep)
                    ref = parts[-1].split("-specification.zip")[0]
                    # check at this stage if there is already a pickle file
                    # if there is, skip doing any reading!!
                    if not Tender.exists(ref):
                        future = executor.submit(begin_thread_zip_task, ref, file_path)
                        futures.append(future)
            with tqdm(total=zips_len, desc="Reading tenders", colour='green') as pbar: 
                for future in concurrent.futures.as_completed(futures):
                    pbar.update(1)

class Tender:
    def __init__(self, reference):
        self.reference = reference
        self.file_map = {}
        
    def clean_text(self, text):
    # convert from binary string if needed
        if type(text) == bytes:
            text = text.decode("utf-8")
        text = re.sub("[^a-zA-z0-9.,]", " ", text)
        text = re.sub("\\\\", " ", text) 
        text = re.sub("\s+", " ", text)
        text = re.sub("\.+", ".", text)
        return text   
    
    def add(self, file_name, content):
        if content == None:
            print(f"Warning: None content for ref:{self.reference}, fname:{file_name}")
        else:
            content = self.clean_text(content)
            
        if file_name in self.file_map:
            # hopefully wont happen
            print(f"Warning: duplicate file name added for ref:{reference} fname:{file_name}")
        else:
            self.file_map[file_name] = content
    
    def save(self):
        with open(f"{self.reference}.pickle", 'wb') as file_handle:
            pickle.dump(self.file_map, file_handle, protocol=pickle.HIGHEST_PROTOCOL)
            
    @staticmethod
    def exists(reference):
        return os.path.exists(f"{reference}.pickle")
    
    @staticmethod
    def load(reference):
        if Tender.exists(reference):
            with open(f"{reference}.pickle", 'rb') as file_handle:
                return pickle.load(file_handle)
        else:
            return None

def remove_html_tags(text):
    soup = BeautifulSoup(text, "html.parser")
    cleaned = soup.get_text().replace('\xa0', ' ')
    cleaned = ' '.join(cleaned.split())
    return cleaned

def process_base(corpus, tenders_data):
    for index, row in tenders_data.iterrows():
        ref = str(row["Reference Number"])
        title = row["Contract Title"]
        desc = remove_html_tags(row["Description"])

        corpus.add(ref, "TITLE", title)
        corpus.add(ref, "DESCRIPTION", desc)

def main(tenders_data_path, search_path):
    # get available extra information from specification documents
    rec_search(search_path)
    
    #tenders_data = pd.read_excel(tenders_data_path)
    #tenders_data = tenders_data[["Reference Number", "Contract Title", "Description"]].dropna(subset=["Reference Number"]).drop_duplicates()

    # add title and short description as base data
    #process_base(tenders_data)

# folder with zip files, not Tenders.zip
tenders_data_path = r"~/Capstone/UWACapstoneG2/data/UpdatedAgainTenders.xlsx"
search_path = r"/home/ucc/maxichat/Capstone/Tenders/Tenders/"

main(tenders_data_path, search_path)
    
print(docs_total)
print(doc_read_failure)
print(f"bad zips: {bad_zips}")