import os
import zipfile
import io
from zipfile import BadZipFile

class NestedZipFile:
    def __init__(self, file_path, full_path, raw_bytes):
        self.file_path = file_path
        self.full_path = full_path
        self.raw_bytes = raw_bytes
        
# allows iteration over a zip containing nested zips
class NestedZip:
    def __init__(self, file_path):
        self.zip_queue = [zipfile.ZipFile(file_path, "r")]
        self.file_queue = []
        self.zip_path = [file_path]
        self.current_zip = None  
        self.current_zip_path = None
        
    def __iter__(self):
        return self
    
    def __next__(self):
        if len(self.file_queue) == 0: # if file queue empty, process next zip contents
            if len(self.zip_queue) > 0:
                self.current_zip = self.zip_queue.pop(0)
                self.current_zip_path = self.zip_path.pop(0)
                for file_info in self.current_zip.infolist():
                    nested_file_name = file_info.filename
                    if nested_file_name.lower().endswith(".zip"):
                        try:
                            path = os.path.join(self.current_zip_path, nested_file_name)
                            self.zip_path.append(path)
                            nested_zip = zipfile.ZipFile(io.BytesIO(self.current_zip.open(nested_file_name).read()), "r")
                            self.zip_queue.append(nested_zip)
                        except BadZipFile as badZipException:
                            print("Bad zip")
                    else:
                        self.file_queue.append(nested_file_name)
            
        if len(self.file_queue) > 0: # process files, if none here, stop
            file_name = self.file_queue.pop(0)
            file_bytes = self.current_zip.read(file_name)
            return NestedZipFile(file_name, os.path.join(self.current_zip_path, file_name), file_bytes)
        else:
            raise StopIteration