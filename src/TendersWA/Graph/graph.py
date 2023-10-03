import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import cosine_similarity
from scipy.spatial import distance_matrix as scipy_distance_matrix

class GraphDB:
    
    def __init__(self, data):
        """ Build queryable graph """
        self.data = data
        self.references = list(data.keys())
        self.similarity_matrix = self.compute_similarity_matrix(data)
        self.distance_matrix = self.compute_distance_matrix(data)
    
    def compute_similarity_matrix(self, data):
        """
        Returns: Computed similarity matrix
        """
        embeddings_matrix = np.array([keys["embedding"] for keys in data.values()])
        return cosine_similarity(embeddings_matrix)
    
    def compute_distance_matrix(self, data):
        """
        Returns: Computed distance matrix
        """
        num_references = len(self.references)
        locations = [data[ref]["location"] for ref in self.references]
        dist_matrix = scipy_distance_matrix(locations, locations)
        return dist_matrix
    
    def closest(self, query, n, max_distance):
        """
        Returns: Top n most similar tenders to query within distance
        """
        ref = self.references.index(query)
        similarity = self.similarity_matrix[ref]
        similarity_sort = np.argsort(similarity)
        within_distance = [idx for idx in similarity_sort if self.distance_matrix[ref, idx] <= max_distance]
        closest = within_distance[-n:]
        return self.make_graph(query, closest, similarity)
        
    def make_graph(self, query, closest, similarity):
        """
        Returns: Subgraph of query node amongst closest nodes with similarity on edges
        """
        G = nx.Graph() 
        G.add_node(query)
        
        for i, idx in enumerate(closest):
            closest_node = self.references[idx]
            
            similarity_value = similarity[idx]
            
            if closest_node != query:
                G.add_edge(query, closest_node, similarity=round(similarity_value, 2))

        return G

    def draw_graph(self, G):
        """
        Returns: Draws the graph
        """
        pos = {ref: self.data[ref]["location"] for ref in G.nodes()}
        labels = {node: node for node in G.nodes()}  
        nx.draw(G, pos, with_labels=True, labels=labels, node_color='lightblue', node_size=800)
        edge_labels = nx.get_edge_attributes(G, 'similarity')
        nx.set_node_attributes(G, pos, "location")
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
        return G