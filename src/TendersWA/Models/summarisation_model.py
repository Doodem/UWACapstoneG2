from transformers import pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.tokenize import sent_tokenize

nltk.download('punkt')

class Summariser:

    """ 
    max_length (int): Maximum length of the generated summary.
    min_length (int): Minimum length of the generated summary.
    do_sample (bool): Whether to use greedy sampling when generating summaries.
        
    Returns: dict of summaries per ref
    """
    def __init__(self, max_length, min_length, type=False, do_sample=False):
        """ Summarises text inputs """

        if type:
            trained = type
        else:
            trained = 'xsum'
        model_name = f'facebook/bart-large-{trained}'
        self.summarizer = pipeline('summarization', model=model_name)

        self.max_length = max_length
        self.min_length = min_length
        self.do_sample = do_sample

    # returns the summarized text, relevant text, short_desc
    def summarise_tender(self, tender):
        
        # combine text
        text = self.combine(tender.file_map)
        # assume has more keys than just 2!
                
        # TF-IDF and cosine similarity to find relevant sentences
        short_desc = tender.file_map["DESCRIPTION"]
        relevant_sentences = self.extract_relevant_sentences(short_desc, sent_tokenize(text))
        
        # combine relevant sentences
        relevant_text = ' '.join(relevant_sentences)
        
        summarized_text = ""
        # If extra information exists
        if relevant_text:
            try:
                summary = self.summarizer(relevant_text, max_length=self.max_length, min_length=self.min_length, do_sample=self.do_sample, truncation=True)
                summarized_text = summary[0]['summary_text']
            except Exception as e:
                print(f"Document for '{tender.reference}' is most likely too long or something went wrong")
                print()
                print(relevant_text)
                print()
                print(e)
        
        return summarized_text, relevant_text, short_desc
    
    def extract_relevant_sentences(self, short_desc, text_list):
        vectorizer = TfidfVectorizer()
        short_desc_vectors = vectorizer.fit_transform([short_desc])
        full_text_vectors = vectorizer.transform(text_list)

        cosine_similarities = cosine_similarity(short_desc_vectors, full_text_vectors)

        # sort sentences by cosine similarity and select top n
        num_sentences_to_select = min(10, len(text_list))
        selected_indices = cosine_similarities.argsort()[0][-num_sentences_to_select:]
        relevant_sentences = [text_list[i] for i in selected_indices]
        return relevant_sentences
    
    def combine(self, keys):
        text_combined = "" 
        for key, text in keys.items():
            if text is not None:
                text_combined += text
        return text_combined
