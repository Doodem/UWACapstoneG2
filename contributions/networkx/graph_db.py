import networkx
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from nltk import tokenize

# graph db class 

class graph_backend():
    def __init__(self,data,distance='cosine'):
        
        self.data = data
        self.distance = distance
        # calculate distance
        if distance == 'cosine':
            self.embeddings_matrix = np.array(self.data)
            # Calculate the cosine similarity matrix
            self.similarity_matrix =  cosine_similarity(self.embeddings_matrix)
   
        