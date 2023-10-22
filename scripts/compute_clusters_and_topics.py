import TendersWA.Clustering as clustering
import TendersWA.Preprocessing.Text as text
from TendersWA.Topic_Modelling import LDATopicModeller

# user paths and settings.
tenders_structured_path = "../data/UpdatedAgainTenders.xlsx"

embedding_path = "../data/embedding_data/st_short_desc_summaries.npz"
tender_emb_refs = "../data/embedding_data/tender_references.txt"
tender_cluster_save_path = "../data/clustering/summary_clusters.csv"
cluster_topic_save_path = "../data/clustering/summary_cluster_topics.csv"
use_summaries = True
# -----------------------------------

# load embeddings and their corresponding references
import numpy
embeddings = numpy.load(embedding_path)
embeddings = [embeddings[f] for f in embeddings.files]
tender_refs = open(tender_emb_refs, "r")
content = ""
for line in tender_refs:
    content = line
    break
content = content.replace("[", "")
content = content.replace("'", "")
content = content.replace(",", "")
content = content.replace("]", "")
tender_refs = content.split(" ")

# sanity check we have all the data exactly corresponding
assert len(embeddings) == len(tender_refs)

# compute clusters on the embeddings
n_clusters = 2000
clusters = clustering.compute_clusters(embeddings, n_clusters)

# load in tender structured data
import pandas as pd
tenders_structured = pd.read_excel(tenders_structured_path)
tenders_structured = tenders_structured[["Reference Number", "Contract Title", "Description"]].dropna(subset=["Reference Number"]).drop_duplicates(subset = ["Reference Number"])

assert(tenders_structured.shape[0] == len(embeddings))

# here can choose whether to use other information (e.g. summaries) 
summary_map = {}
if use_summaries:
    import os
    import pickle
    summary_path = "../../data/extended_summaries/"
    for ref in tender_refs:
        sum_file = os.path.join(summary_path, f"{ref}.pickle.sum")
        if os.path.exists(sum_file):
            loaded_sum = pickle.load(open(sum_file, "rb"))
            summary_map[ref] = loaded_sum["summary"]

# ----------------

docs = []
for index, row in tenders_structured.iterrows():
    title = row["Contract Title"]
    desc = text.remove_html_tags(row["Description"])
    # if a summary is available for this tender, us that instead of short description
    if row["Reference Number"] in summary_map:
        docs.append(title + ". " + summary_map[row["Reference Number"]])
    else:
        docs.append(title + ". " + desc)

topic_model = LDATopicModeller(docs)

cluster_topics_l = []
cluster_numbers_l = []
for n_cluster in range(0, n_clusters):
    subset_docs = [docs[i] for i in list(numpy.where(clusters == n_cluster)[0])]
    topics = topic_model.get_topics(subset_docs)
    cluster_topics_l.append(", ".join(topics))
    cluster_numbers_l.append(n_cluster)

tender_cluster_df = pd.DataFrame({"Reference Number": tender_refs, "Cluster": clusters})
cluster_topic_df = pd.DataFrame({"Cluster": cluster_numbers_l, "Topics": cluster_topics_l})

tender_cluster_df.to_csv(tender_cluster_save_path, index = False)
cluster_topic_df.to_csv(cluster_topic_save_path, index = False)
