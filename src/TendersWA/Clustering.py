from sklearn.cluster import KMeans
from sklearn import preprocessing

# ideally run with higher n_init value, but clustering for large values (>=2000) can be quite slow.
def compute_clusters(embeddings, n_clusters, n_init = 1):
    return KMeans(n_clusters = n_clusters, n_init = n_init).fit_predict(preprocessing.normalize(embeddings))