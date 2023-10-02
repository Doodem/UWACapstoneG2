import pickle
import re
import os

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
            print(f"Warning: duplicate file name added for ref:{self.reference} fname:{file_name}")
        else:
            self.file_map[file_name] = content
    
    def save(self):
        with open(f"{self.reference}.pickle", 'wb') as file_handle:
            pickle.dump(self.file_map, file_handle, protocol=pickle.HIGHEST_PROTOCOL)
           
    @staticmethod
    def __correct_handle(reference):
        if ".pickle" in reference: # assume its a fpath, dont change
            return reference
        else: # try ref.pickle
            return f"{reference}.pickle"
        
    @staticmethod
    def exists(reference):
        return os.path.exists(Tender._Tender__correct_handle(reference))
            
    @staticmethod
    def load(reference):
        if Tender.exists(reference):
            with open(Tender._Tender__correct_handle(reference), 'rb') as file_handle:
                t = Tender(reference)
                t.file_map = pickle.load(file_handle)
                return t
        else:
            return None