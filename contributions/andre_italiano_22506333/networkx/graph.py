import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import cosine_similarity
from scipy.spatial import distance_matrix as scipy_distance_matrix
import pandas as pd

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
    
    def closest(self, query, n, max_distance,date1,date2):
        """
        Returns: Top n most similar tenders to query within distance and time
        """
        ref = self.references.index(query)
        similarity = self.similarity_matrix[ref]
        similarity_sort = np.argsort(similarity)
        within_distance = [idx for idx in similarity_sort if self.distance_matrix[ref, idx] <= max_distance]
        within_date = []
        for item in within_distance:
            temp_ref = self.references[item]
            if self.data[temp_ref]['expire_date'] > date1 and self.data[temp_ref]['expire_date'] < date2:
                within_date.append(item)
            elif pd.isnull(self.data[temp_ref]['expire_date']):
                within_date.append(item)
                
        
        closest = within_date[-n:]
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
        G_plot = G.copy()
        nx.draw(G_plot, with_labels=True, labels=labels, node_color='lightblue', node_size=800,font_size=8)
        layout = nx.spring_layout(G)
        edge_labels = nx.get_edge_attributes(G, 'similarity')
        nx.set_node_attributes(G, pos, "location")
        nx.draw_networkx_edge_labels(G_plot, pos=layout,edge_labels=edge_labels)
        
        plt.show()
        
        return G