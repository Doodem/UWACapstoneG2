import TendersWA.Models.Embedding_Model as em
import pandas as pd

model = em.Sentence_transformer()

tenders_structured_path = r"../data/UpdatedAgainTenders.xlsx"
tenders_structured = pd.read_excel(tenders_structured_path)

unspsc_titles = tenders_structured["UNSPSC Title"].tolist()
uniques = list(set(unspsc_titles))
titles = []
embs = []
for title in uniques:
    embs.append(model(title))
    titles.append(title)

import numpy as np
import pickle
np.savez("unspsc_embeddings.npz", *embs)
# to load:
# embs = np.load("unspsc_embeddings.npz")
# embs = [embs[f] for f in embs.files]

with open("unspsc_title_list.pickle", "wb") as f:
    pickle.dump(titles, f)
# to load:
# titles = pickle.load(open("unspsc_title_list.pickle", "rb"))
