import numpy as np
from sklearn.decomposition import PCA


embedding_vectors = [...]

# Convert the list of vectors to a numpy array
embedding_array = np.array(embedding_vectors)

# Number of principal components you want to retain
num_components = 50  # Can adjust this as needed

# Initialize the PCA model with the desired number of components
pca = PCA(n_components=num_components)

# Fit the PCA model to your data and transform the data
reduced_vectors = pca.fit_transform(embedding_array)

# Now, reduced_vectors contains the lower-dimensional representation of your data
# Each row of reduced_vectors corresponds to a transformed data point

# If you want to access the principal components themselves, you can use pca.components_

# You can access the amount of variance explained by each principal component using pca.explained_variance_ratio_

# You can also access the cumulative explained variance using np.cumsum(pca.explained_variance_ratio_)

# Print the cumulative explained variance to see how much information is retained
print("Cumulative Explained Variance:", np.cumsum(pca.explained_variance_ratio_))


