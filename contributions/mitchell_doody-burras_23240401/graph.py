import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import cosine_similarity

class GraphDB:
    
    def __init__(self, data):
        """ Build queryable graph """
        self.references = list(data.keys())
        self.similarity_matrix = self.compute_similarity_matrix(data)
    
    def compute_similarity_matrix(self, data):
        """
        Returns: Computed similarity matrix
        """
        embeddings_matrix = np.array([keys["embedding"] for keys in data.values()])
        return cosine_similarity(embeddings_matrix)
    
    def compute_distance_matrix(self, data):
            pass
    
    def closest(self, query, n):
        """
        Returns: Top n most similar tenders to query
        """
        ref = self.references.index(query)
        similarity = self.similarity_matrix[ref]
        similarity_sort = np.argsort(similarity)
        closest = similarity_sort[-n:]
        return self.subset_graph(ref, closest, similarity)
        
    def subset_graph(self, ref, closest, similarity):
        """
        Returns: Subgraph of query node amongst closest nodes with similarity on edges
        """
        G = nx.Graph() 
        G.add_node(ref)

        for i, idx in enumerate(closest):
            closest_node = self.references[idx]
            similarity_value = similarity[i]
            G.add_edge(ref, closest_node, similarity=round(similarity_value, 2))

        return G

    def draw_graph(self, G):
        """
        Returns: Draws the graph
        """
        pos = nx.spring_layout(G)
        labels = {node: node for node in G.nodes()}  
        nx.draw(G, pos, with_labels=True, labels=labels, node_color='lightblue', node_size=800)
        edge_labels = nx.get_edge_attributes(G, 'similarity')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)