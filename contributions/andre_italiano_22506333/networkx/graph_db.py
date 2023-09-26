import networkx
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from nltk import tokenize

# graph db class 


class graph_backend():
    def __init__(self,data,titles,reference_number,postcodes,distance='cosine'):
        
        self.data = data
        self.distance = distance
        self.titles = titles
        self.references = reference_number
        self.postcodes = postcodes
        self.data_dict = dict()
        i = 0
        for title,ref in range(self.titles):
            self.data_dict[i] = [self.title[i],self.references[i],self.postcodes=[i]]
            i +=1
        
        # calculate distance
        if distance == 'cosine':
            self.embeddings_matrix = np.array(self.data)
            # Calculate the cosine similarity matrix
            self.similarity_matrix =  cosine_similarity(self.embeddings_matrix)
            
    def get_top_n(self,ref,n=5):
        ref_id = self.references.index(ref)
        sim = self.similarity_matrix[ref_id]
        sim_sort = np.argsort(sim)
        closest = sim_sort[-n:]
        return closest,sim
        
    def make_graph(self,ref,same_postcode=False,n=5):
        r,sim = self.get_top_n(ref)
        G = nx.Graph()
        for item in r:
            ref_id = self.data_dict[item][1]
            ref_post = self.data_dict[]
            if ref_id == ref:
                continue
                
            
            
            
            G.add_node(ref_id,postcode =self.data_dict[item] )
            G.add_edge(ref_id,ref,sim=sim_score)
        layout = nx.spring_layout(G)
        nx.draw(G, with_labels=True,node_size=500)
        
        
        # draw edge attributes
        edge_labels = nx.get_edge_attributes(G, 'sim')
        nx.draw_networkx_edge_labels(G,pos=layout,edge_labels=edge_labels)
        
        
        plt.show()
        