import os
import zipfile
import io
import pandas as pd

# copied from Limin's script
# adjusted to run on ucc computer

def analyze_zip_contents(zip_data):
    file_types = {}
    files_with_request = 0
    doc_request_files = 0
    total_files = 0

    with zipfile.ZipFile(zip_data, 'r') as zip_ref:
        for file in zip_ref.namelist():
            if file.endswith('.zip'):
                with zip_ref.open(file) as nested_zip_file:
                    try:
                        nested_types, nested_request, nested_doc_request, nested_total = analyze_zip_contents(io.BytesIO(nested_zip_file.read()))
                        for ext, count in nested_types.items():
                            file_types[ext] = file_types.get(ext, 0) + count
                        files_with_request += nested_request
                        doc_request_files += nested_doc_request
                        total_files += nested_total
                    except:
                        print(f"Bad Zip for {file}")
            else:
                total_files += 1
                if "request" in file.lower():
                    files_with_request += 1
                    if file.lower().endswith(('.doc', '.docx')):
                        doc_request_files += 1
                file_extension = os.path.splitext(file)[1][1:].lower()
                if file_extension in ['doc', 'docx']:
                    file_extension = 'doc/docx'
                file_types[file_extension] = file_types.get(file_extension, 0) + 1

    return file_types, files_with_request, doc_request_files, total_files


def analyze_and_write(zip_files, output_file, master_zip):
    all_file_types = set()
    data = []

    for zip_path in zip_files:
        with master_zip.open(zip_path) as zip_content:
            file_types, files_with_request, doc_request_files, total_files = analyze_zip_contents(io.BytesIO(zip_content.read()))
            all_file_types.update(file_types.keys())
            data.append((os.path.basename(zip_path), file_types, files_with_request, doc_request_files, total_files))

    columns = ['zip file name', 'total number of documents'] + ['number of ' + t for t in all_file_types] + [
        'number of "Request" document', 'number of "Request" doc/docx']
    df = pd.DataFrame(columns=columns)

    for name, types, request_count, doc_request_count, total_count in data:
        row_data = {column: 0 for column in columns}
        row_data['zip file name'] = name
        row_data['total number of documents'] = total_count
        row_data['number of "Request" document'] = request_count
        row_data['number of "Request" doc/docx'] = doc_request_count
        for ext, count in types.items():
            row_data['number of ' + ext] = count
        df = df._append(pd.DataFrame([row_data]), ignore_index=True)

    df.to_excel(output_file, index=False)


tenders_zip = "/home/ucc/maxichat/Capstone/Tenders/Tenders.zip"
output_excel_path = "./tenders_analyzed.xlsx" 
with zipfile.ZipFile(tenders_zip, "r") as all_zips:
    zip_files = [file for file in all_zips.namelist() if file.endswith("zip")]
    analyze_and_write(zip_files, output_excel_path, all_zips)
