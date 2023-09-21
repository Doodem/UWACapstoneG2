from transformers import pipeline

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
        
        for ref, text in docs.items(): 
            try:
                summary = self.summarizer(text, max_length=self.max_length, min_length=self.min_length, do_sample=self.do_sample)
                self.summarised_docs[ref] = summary[0]['summary_text']
            except:
                print(f"Document for '{ref}' is most likely too long")
                continue
        
        return self.summarised_docs
        
    def summary(self, ref):
        """ Return summaries from input ref """
        return print(self.summarised_docs[ref])
    
def combine(d):
    """ Combine docs for every reference """
    tmp = {}
    for ref, docs in d.items():
        ref_text = ' '.join(docs.values())
        tmp[ref] = ref_text
    return tmp

summariser = Summariser(max_length=50, min_length=30, do_sample=False) # can add type='cnn' to change what model trained on
summarised_docs = summariser.summarise_docs(combine("ADD YOUR DICTIONARY OF DICTIONARIES HERE"))

# print specified summary for a ref
summariser.summary("ADD TENDER REF HERE")

# print all summaries per ref
for ref, summary in summarised_docs.items():
    print(f"Summary for {ref}:\n{summary}")