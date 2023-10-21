import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import cosine_similarity
from scipy.spatial import distance_matrix as scipy_distance_matrix
import pandas as pd

import folium
from folium import plugins
from folium.features import DivIcon
from datetime import datetime

class GraphDB:
    
    def __init__(self, data):
        """ Build queryable graph """
        self.data = data
        self.references = list(data.keys())
        self.titles = [self.data[item]['titles'] for item in self.references]
        
        
        
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
    
    
    def get_neighbours(self,G,ref,neighbours,max_distance,date1,date2,n):
        seen = [ref]
        
        if neighbours > 0:
            for stage in range(neighbours):
                
                nodes_list = list(G.nodes())
                
                for item in nodes_list:
                    if item in seen:
                        continue
                    seen.append(item)
                    ref_idx = self.references.index(item)
                    ref = self.references[ref_idx]
                    similarity = self.similarity_matrix[ref_idx]
                    similarity_sort = np.argsort(similarity)
                    within_distance = [idx for idx in similarity_sort if self.distance_matrix[ref_idx, idx] <= max_distance]
                    within_date = []
                    for item in within_distance:
                        temp_ref = self.references[item]
                        if self.data[ref]['expire_date'] > date1 and self.data[ref]['expire_date'] < date2:
                            within_date.append(item)
                        elif pd.isnull(self.data[ref]['expire_date']):
                            within_date.append(item) 
                    closest = within_date[-n:]
                    for i, idx in enumerate(closest):
                        closest_node = self.references[idx]            
                        similarity_value = similarity[idx]            
                        if closest_node != ref:
                            G.add_edge(ref, closest_node, similarity=round(similarity_value, 2))
        return G
        
        
        
    
    def get_topics_graph(self,cluster):
        tenders = []
        for item in self.references:
            
            if str(self.data[item]['cluster']) == cluster:
                tenders.append(item)
        G = nx.Graph()
        G.add_nodes_from(tenders)
        return G
    
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
    
    def get_node_positions(self,reference, num_nodes, max_distance,date1,date2,neighbours):
        query_result = self.closest(reference, num_nodes, max_distance,date1,date2)
        query_result_neighbours = self.get_neighbours(query_result,reference,neighbours,max_distance,date1,date2,num_nodes)
        G = self.draw_graph(query_result_neighbours)
        return nx.get_node_attributes(G, "location"), nx.get_edge_attributes(G,"similarity")
    
    def create_map(self,map_center):
        m = folium.Map(location=map_center, zoom_start=5)
        return m





    def query_and_display(self,reference, num_nodes, max_distance,expire_date,topic,topic_box,neighbours):    
        if topic_box and topic!= 'Please enter a value':

            t_ = self.get_topics_graph(topic)
            t = self.draw_graph(t_)        
            node_positions = nx.get_node_attributes(t, "location")
            node_similarity = nx.get_edge_attributes(t,"similarity")
            reference = list(node_positions.keys())[0]

            map_center = node_positions[reference]
            m = self.create_map(map_center)
            for ref,position in node_positions.items():
                title = self.data[ref]['titles']
                # plot ref marker
                folium.CircleMarker(location=position,popup=title,fill_color='blue').add_to(m)

                # plot ref label
                folium.Marker(location=position,popup=reference,icon=DivIcon(
                icon_size=(150,36),
                icon_anchor=(0,0),
                html=f'<div style="font-size: 12pt">{ref}</div>',
                )).add_to(m)
            display(m)    

        else:   
            if reference == 'Please enter a value':
                return
            if len(reference) > 20:
                title_index = self.titles.index(reference)
                reference = tender_references[title_index]

            edge_text_group = folium.FeatureGroup()
            node_positions,node_similarity = self.get_node_positions(reference, num_nodes, max_distance,expire_date[0],expire_date[1],neighbours)
            map_center = node_positions[reference]    
            # create map with centered on reference 
            m = self.create_map(map_center)


            # add markers for ref positions on map
            for ref,position in node_positions.items():

                title = self.data[ref]['titles']
                topics = self.data[ref]['topics']
                popup = title + "\n " "\n " + "---------" + 'Topics are:'  +str(topics)
                # plot ref marker
                folium.CircleMarker(location=position,popup=popup,fill_color='blue').add_to(m)
                # plot ref label
                folium.Marker(location=position,popup=reference,icon=DivIcon(
                icon_size=(150,36),
                icon_anchor=(0,0),
                html=f'<div style="font-size: 12pt">{ref}</div>',
                )).add_to(m)

            for markers, sim in node_similarity.items():


                edge = folium.PolyLine([node_positions[markers[0]],node_positions[markers[1]]],popup=str(sim))
                edge.add_to(m)
                edge_text = plugins.PolyLineTextPath(edge,text = str(sim),center=True,attributes={'fill': '007DEF', 'font-weight': 'bold', 'font-size': '24'})
                edge_text_group.add_child(edge_text)


            m.add_child(edge_text_group)
            display(m)
