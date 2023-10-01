import sys
import tomotopy as tp
import numpy as np
import re
import nltk
import pandas as pd
from bs4 import BeautifulSoup

def train(model, save_path):
    model.train(0)
    print('Num docs:', len(model.docs), ', Vocab size:', len(model.used_vocabs), ', Num words:', model.num_words)
    print('Removed top words:', model.removed_top_words)
    print('Training...', file=sys.stderr, flush=True)
    for _ in range(0, 200, 10):
        model.train(7)
        model.train(3, freeze_topics=True)
        print('Iteration: {:05}\tll per word: {:.5f}'.format(model.global_step, model.ll_per_word))

    for _ in range(0, 100, 10):
        model.train(10, freeze_topics=True)
        print('Iteration: {:05}\tll per word: {:.5f}'.format(model.global_step, model.ll_per_word))

    print('Saving...', file=sys.stderr, flush=True)
    model.save(save_path, True)

tenders_structured_path = r"~/Capstone/UWACapstoneG2/data/UpdatedAgainTenders.xlsx"

tenders_structured = pd.read_excel(tenders_structured_path)
tenders_structured = tenders_structured[["Reference Number", "Contract Title", "Description"]].dropna(subset=["Reference Number"]).drop_duplicates()

def remove_html_tags(text):
    soup = BeautifulSoup(text, "html.parser")
    cleaned = soup.get_text().replace('\xa0', ' ')
    cleaned = ' '.join(cleaned.split())
    return cleaned


from nltk.corpus import stopwords
try:
    corpus = tp.utils.Corpus.load('tender.cached.corpus')
except IOError:
    docs = []
    for index, row in tenders_structured.iterrows():
        title = row["Contract Title"]
        desc = remove_html_tags(row["Description"])
        docs.append(title + " " + desc)
    stops = set(stopwords.words('english'))
    corpus = tp.utils.Corpus(
        tokenizer=tp.utils.SimpleTokenizer(), # leave empty tokenizer as it doesnt seem to work without 
        stopwords=lambda x: len(x) <= 2 or x in stops
    )
    corpus.process(docs)
    corpus.save('tender.cached.corpus')

model = tp.HPAModel(tw=tp.TermWeight.ONE, k1=10, k2=100, rm_top=0, corpus=corpus)
train(model, "struc_tender.hpa.tmm")
