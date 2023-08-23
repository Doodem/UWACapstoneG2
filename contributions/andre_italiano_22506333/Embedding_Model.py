# importing modules 
import pandas as pd
from torch import nn
from transformers import BertTokenizer, BertModel, BigBirdModel,AutoModelForSequenceClassification,BertConfig
import numpy as np
import math
import gensim.downloader as api
import torch
from torch import nn
import re
import nltk
nltk.download('wordnet')
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import torch.nn.functional as F
from transformers import BertTokenizer
from bs4 import BeautifulSoup

#  model class 

class Pretrained_model(nn.Module):
    def __init__(self,model='bert'):
        super(Pretrained_model,self).__init__()
        
        if model.lower() =='bert':
            self.bert_config = BertConfig.from_pretrained('bert-base-uncased',output_hidden_states=True)
            self.embedding_model = BertModel.from_pretrained('bert-base-uncased',config=self.bert_config)
            self.model_base = 'bert-base-uncased'
        elif model.lower() == "longformer":
            self.embedding_model = AutoModelForSequenceClassification.from_pretrained("allenai/longformer-base-4096")
            self.model_base = "allenai/longformer-base-4096"
        elif model.lower() == "bigbird":
            self.embedding_model = BigBirdModel.from_pretrained("google/bigbird-roberta-base")
            self.model_base ="google/bigbird-roberta-base"
        
        
        
    def forward(self,input_ids,attention_mask,token_type_ids):
        pooled_output = self.embedding_model(input_ids=input_ids,attention_mask=attention_mask,token_type_ids=token_type_ids)
        return pooled_output
    
def preprocess_for_bert(data):
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased',model_max_length=512)
    x = tokenizer(text = data,return_tensors = 'pt',truncation=True)
    return x

def preprocess_and_forward(data,model):
    x = preprocess_for_bert(data)
    
    with torch.no_grad():
        hidden_out = model(x['input_ids'],x['attention_mask'],x['token_type_ids'])
    cls_token = hidden_out.last_hidden_state
    cls_token = cls_token[0][0]
    cls_token = cls_token.unsqueeze(0)
    return cls_token

def cosine_sim(x1,x2):
    return F.cosine_similarity(x1,x2)


def remove_html_tags(text):
    
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text()



    
contraction_dict = {"ain't": "is not", "aren't": "are not","can't": "cannot", "'cause": "because", "could've": "could have", 
                    "couldn't": "could not", "didn't": "did not",  "doesn't": "does not", "don't": "do not", "hadn't": "had not", 
                    "hasn't": "has not", "haven't": "have not", "he'd": "he would","he'll": "he will", "he's": "he is", "how'd": "how did", 
                    "how'd'y": "how do you", "how'll": "how will", "how's": "how is",  "I'd": "I would", "I'd've": "I would have", 
                    "I'll": "I will", "I'll've": "I will have","I'm": "I am", "I've": "I have", "i'd": "i would", "i'd've": "i would have", 
                    "i'll": "i will",  "i'll've": "i will have","i'm": "i am", "i've": "i have", "isn't": "is not", "it'd": "it would", 
                    "it'd've": "it would have", "it'll": "it will", "it'll've": "it will have","it's": "it is", "let's": "let us", 
                    "ma'am": "madam", "mayn't": "may not", "might've": "might have","mightn't": "might not","mightn't've": "might not have", 
                    "must've": "must have", "mustn't": "must not", "mustn't've": "must not have", "needn't": "need not", "needn't've": "need not have",
                    "o'clock": "of the clock", "oughtn't": "ought not", "oughtn't've": "ought not have", "shan't": "shall not", "sha'n't": "shall not", 
                    "shan't've": "shall not have", "she'd": "she would", "she'd've": "she would have", "she'll": "she will", "she'll've": "she will have", 
                    "she's": "she is", "should've": "should have", "shouldn't": "should not", "shouldn't've": "should not have", "so've": "so have",
                    "so's": "so as", "this's": "this is","that'd": "that would", "that'd've": "that would have", "that's": "that is", "there'd": "there would", 
                    "there'd've": "there would have", "there's": "there is", "here's": "here is","they'd": "they would", "they'd've": "they would have", 
                    "they'll": "they will", "they'll've": "they will have", "they're": "they are", "they've": "they have", "to've": "to have", "wasn't": "was not", 
                    "we'd": "we would", "we'd've": "we would have", "we'll": "we will", "we'll've": "we will have", "we're": "we are", "we've": "we have", 
                    "weren't": "were not", "what'll": "what will", "what'll've": "what will have", "what're": "what are",  "what's": "what is", "what've": "what have", 
                    "when's": "when is", "when've": "when have", "where'd": "where did", "where's": "where is", "where've": "where have", "who'll": "who will", 
                    "who'll've": "who will have", "who's": "who is", "who've": "who have", "why's": "why is", "why've": "why have", "will've": "will have", 
                    "won't": "will not", "won't've": "will not have", "would've": "would have", "wouldn't": "would not", "wouldn't've": "would not have", 
                    "y'all": "you all", "y'all'd": "you all would","y'all'd've": "you all would have","y'all're": "you all are","y'all've": "you all have",
                    "you'd": "you would", "you'd've": "you would have", "you'll": "you will", "you'll've": "you will have", "you're": "you are", "you've": "you have"}

# preprocessing class
class Textprocessor:
    def __init__(self, contraction_mapping = contraction_dict):
        self.lemmatizer = WordNetLemmatizer()
        self.contraction_mapping = contraction_mapping

    def preprocess_text(self, text):
        text = self._to_lower(text)
        text = self._expand_contractions(text)
        text = self._remove_punctuation(text)
        tokens = self._tokenize(text)
        tokens = self._lemmatize_tokens(tokens)
        return tokens

    def _to_lower(self, text):
        return text.lower()

    def _expand_contractions(self, text):
        for word, new_word in self.contraction_mapping.items():
            text = text.replace(word, new_word)
        return text

    def _remove_punctuation(self, text):
        return re.sub(r'[^\w\s]', '', text)

    def _tokenize(self, text):
        return word_tokenize(text)

    def _lemmatize_tokens(self, tokens):
        return [self.lemmatizer.lemmatize(token) for token in tokens]
# evalaute function
def evaluate(data):
    pass

