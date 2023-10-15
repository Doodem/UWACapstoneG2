from TendersWA.Preprocessing.NestedZip import NestedZip
from TendersWA.Preprocessing.Tender import Tender

import io
import os
import tempfile
import PyPDF2
from io import BytesIO    
from docx import Document
import textract
import re
from tqdm import tqdm
import pickle
from concurrent.futures import ProcessPoolExecutor
import concurrent.futures

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
    
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        for page_number in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_number]
            text += page.extract_text()
        return text
    except Exception as e:
        print(f"pdf error: {e}")
        return None

def ocr(image_file):
    # extract text from image
    image_data = image_file
    return image_data

bad_zips = 0
def file_handler(tender, file_name, raw_bytes):
    global bad_zips
    try:
        if file_name.lower().endswith(('doc', 'docx')):
            doc_data = read_doc(raw_bytes)
            tender.add(file_name, doc_data)
        elif nested_file_name.lower().endswith("pdf"):
            pdf_data = read_pdf(raw_bytes)
            tender.add(file_name, pdf_data)
    except (BadZipFile, Exception) as badZipException:
        bad_zips += 1
        print(e)

# ----------------------

def begin_thread_zip_task(ref, file_path):
    tender = Tender(ref)
    nested_zip = NestedZip(file_path)
    for file in nested_zip:
        file_handler(tender, file.raw_bytes)
        
    # save the file
    print(f"saving {ref} ...")
    tender.save()
    print("saved!")     
                        
def rec_search(directory_path):
    for root, _, files in os.walk(directory_path):
        with ProcessPoolExecutor() as executor:  
            futures = []
            files_to_process = 0
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
                        files_to_process += 1
            with tqdm(total=files_to_process, desc="Reading tenders", colour='green') as pbar: 
                for future in concurrent.futures.as_completed(futures):
                    pbar.update(1)
        
def main(tenders_data_path, search_path):
    # get available extra information from specification documents
    rec_search(search_path)

tenders_data_path = r"~/Capstone/UWACapstoneG2/data/UpdatedAgainTenders.xlsx"

# folder with zip files, not Tenders.zip
search_path = r"/home/ucc/maxichat/Capstone/Tenders/Tenders/"

main(tenders_data_path, search_path)
    
print(docs_total)
print(doc_read_failure)
print(f"bad zips: {bad_zips}")

