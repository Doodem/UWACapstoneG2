from transformers import pipeline
import os
import pickle

class Summariser:

    def __init__(self, max_length, min_length, type=False, do_sample=False):
        """ Summarises text inputs """

        if type:
            trained = type
        else:
            trained = 'xsum'
        self.summarizer = pipeline('summarization', model=f'facebook/bart-large-{trained}')

        self.max_length = max_length
        self.min_length = min_length
        self.do_sample = do_sample
        self.summarised_docs = {}

    def summarise_docs(self, docs):
        """ 
        max_length (int): Maximum length of the generated summary.
        min_length (int): Minimum length of the generated summary.
        do_sample (bool): Whether to use greedy sampling when generating summaries.
        
        Returns: dict of summaries per ref
        """
        
        for ref, keys in docs.items():
            # combine text
            text = self.combine(keys)     
            
            # if extra information exists
            if len(keys) > 2:
                try:
                    summary = self.summarizer(text, max_length=self.max_length, min_length=self.min_length, do_sample=self.do_sample)
                    self.summarised_docs[ref] = summary[0]['summary_text']
                    print("Tender summarised")
                except:
                    print(f"Document for '{ref}' is most likely too long")
                    continue
            
            # don't summarise title and short desc
            else:
                self.summarised_docs[ref] = text
                print("Tender not summarised")
            
        return self.summarised_docs
        
    def summary(self, ref):
        """ Return summaries from input ref """
        return print(self.summarised_docs[ref])
    
    def combine(self, keys):
        text = ""
        for key, text in keys.items():
            text += text
        return text

def load_pickles(path):
    pickles_read = {}
    pickles_unread = []

    for file in os.listdir(path):
        if file.endswith('.pickle'):
            file_path = os.path.join(path, file)
            ref = os.path.splitext(os.path.basename(file_path))[0]
            try:
                with open(file_path, "rb") as data:
                    pickles_read[ref] = pickle.load(data)
            except:
                pickles_unread.append(file)
    
    return pickles_read, pickles_unread

pickle_path = "C:/Users/Mitch/pickles/"
pickles, empty_pickles = load_pickles(pickle_path)

summariser = Summariser(max_length=50, min_length=30, do_sample=False) # can add type='cnn' to change what model trained on
summarised_docs = summariser.summarise_docs(pickles)

# print specified summary for a ref
summariser.summary("ADD TENDER REF HERE")

# print all summaries per ref
for ref, summary in summarised_docs.items():
    print(f"Summary for {ref}:\n{summary}")