# importing modules 
import pandas as pd
from torch import nn
from transformers import BertTokenizer, BertModel, BigBirdModel, LongformerModel , BertConfig,BigBirdTokenizer
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
from transformers import BertTokenizer, LongformerTokenizer
from bs4 import BeautifulSoup
from numpy.linalg import norm
from nltk import tokenize

#  model class 

class Pretrained_model(nn.Module):
    def __init__(self,custom_model,model='bert'):
        super(Pretrained_model,self).__init__()
        
        if model.lower() == 'custom':
            self.bert_config = BertConfig.from_pretrained('bert-base-uncased',output_hidden_states=True)
            self.embedding_model = BertModel.from_pretrained(custom_model,config=self.bert_config)
        if model.lower() =='bert':
            self.bert_config = BertConfig.from_pretrained('bert-base-uncased',output_hidden_states=True)
            self.embedding_model = BertModel.from_pretrained('bert-base-uncased',config=self.bert_config)
            self.model_base = 'bert-base-uncased'
        elif model.lower() == "longformer":
            self.embedding_model = LongformerModel.from_pretrained("allenai/longformer-base-4096",output_hidden_states = True, return_dict = True)
            
            self.model_base = "allenai/longformer-base-4096"
        elif model.lower() == "bigbird":
            self.embedding_model = BigBirdModel.from_pretrained("google/bigbird-roberta-base",output_hidden_states = True, return_dict = True)
            self.model_base ="google/bigbird-roberta-base"
        
        
        
    def forward(self,input_ids,attention_mask,token_type_ids):
        
        if self.model_base == "allenai/longformer-base-4096":
            global_attention_mask = [1].extend([0]*input_ids.shape[-1])
            pooled_output = self.embedding_model(input_ids=input_ids,attention_mask=attention_mask,token_type_ids=token_type_ids,global_attention_mask = global_attention_mask)
            
            return pooled_output.last_hidden_state[:,0]
        
        elif self.model_base == "google/bigbird-roberta-base":
            global_attention_mask = [1].extend([0]*input_ids.shape[-1])
            pooled_output = self.embedding_model(input_ids=input_ids,attention_mask=attention_mask,token_type_ids=token_type_ids)
            
            return pooled_output.last_hidden_state[:,0]
        else:
        
            pooled_output = self.embedding_model(input_ids=input_ids,attention_mask=attention_mask,token_type_ids=token_type_ids)        
            cls_token = pooled_output.last_hidden_state
            cls_token = cls_token[0][0]
            cls_token = cls_token.unsqueeze(0)
            return cls_token
   
    


def preprocess_and_forward(data,text_processor,model):
    sentence_embeddings = []
    processed_item = text_processor.tokenize_sentence(data)
    for sentence in processed_item:
        x = text_processor.preprocess_text(sentence)

        with torch.no_grad():               
            sentence_embeddings.append(model(x['input_ids'],x['attention_mask'],x['token_type_ids']).numpy()[0])
            
    
    # Sum sentence embeddings
    sum_embeddings = np.sum(sentence_embeddings, axis=0)
    average_embeddings = sum_embeddings/len(processed_item)
    
    return average_embeddings

def cosine_sim(A,B):
    return np.dot(A,B)/(norm(A)*norm(B))


def remove_html_tags(text):
    
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text()

def bert_preprocessing(text):
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased',model_max_length=512)
    
    return tokenizer(text = text,return_tensors = 'pt',truncation=True)


    
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
    def __init__(self, contraction_mapping = contraction_dict,model="bert"):
        self.lemmatizer = WordNetLemmatizer()
        self.contraction_mapping = contraction_mapping
        
        self.model = "bert"
        if self.model == "bert":
            self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased',model_max_length=512)
        if self.model == "longformer":
            self.tokenizer = LongformerTokenizer.from_pretrained("allenai/longformer-base-4096")
        if self.model == "bigbird":
            self.tokenizer = BigBirdTokenizer.from_pretrained("google/bigbird-roberta-base")

            
    def preprocess_text(self, text):
        text_lower = self._to_lower(text)
        text_contractions = self._expand_contractions(text_lower)
        text_no_punct = self._remove_punctuation(text_contractions)
        tokens = self._lemmatize_tokens(text_no_punct)
        tokens = self._tokenize(tokens)
        
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
        return self.tokenizer(text = text,return_tensors = 'pt',truncation=True)

    def _lemmatize_tokens(self, tokens):
        text_tokenized = [self.lemmatizer.lemmatize(token) for token in tokens]
        text = ""
        for item in text_tokenized:
            text = text + " " + item
        return text 
    def tokenize_sentence(self,doc):
        return tokenize.sent_tokenize(doc)
