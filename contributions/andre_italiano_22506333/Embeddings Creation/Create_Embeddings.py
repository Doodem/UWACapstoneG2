# importing packages 
from TendersWA.Models import Embedding_Model as em
import pandas as pd
import os 
from tqdm import tqdm
import pickle

# load data,
structured_data = pd.read_excel("data/tender_postcode.xlsx")
structured_data = structured_data.dropna(subset=["Reference Number"]).drop_duplicates('Reference Number')
# get title + descriptions 
titles = list(structured_data['Contract Title'])
structured_descriptions =  [em.remove_html_tags(item) for item in structured_data['Description']]
# get list of reference numbers
ref_list = list(structured_data['Reference Number'])
# get id list for tenders that have summaries, set path differently if data files are located in a different directory 
path = 'data/extended_summaries'
sum_ids = [item.split(".")[0] for item in os.listdir(path)]
# create model instance
model = em.Sentence_transformer()

# create embeddings
embeddings_output = []
path = 'data/extended_summaries/'
for item in tqdm(range(len(ref_list))):
    # check if tender has a summary from summarization model
    if ref_list[item] in sum_ids:
        # unpickle summary and get embedding
        pickle_path = path + ref_list[item] + ".pickle.sum"
        summary = pickle.load(open(pickle_path,"rb"))['summary']
        embeddings_output.append(model(titles[item] + summary ))
    else:
        embeddings_output.append(model(titles[item]+structured_descriptions[item]))

# save embeddings to file
np.savez('embedding_file_name.npz', *embedding_output)