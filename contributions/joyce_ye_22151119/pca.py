from sklearn.decomposition import PCA
pca = PCA(n_components=2) # choose appropriate number of components to keep
pca.fit(sen_emb)
sen_emb_reduced = pca.transform(sen_emb)
print('Reduced sentence embedding shape:', sen_emb_reduced.shape)


def biplot(reduced_data, labels, pc, variable):
    """plot compositional biplot for two principle components

    :param reduced_data: embedding vector processed by PCA
    :param labels: labels of original dataset
    :param pc: all the principle components
    :param variable: the name of the variables of the data set
    """
    plt.figure(1, figsize=(14, 10))

    legend = []  #
    #classes = np.unique(labels)  # label type
    n = pc.shape[1]
    # colors = ['g', 'r', 'y']
    # markers = ['o', '^', 'x']

    x = reduced_data[:, 0]  # variable contributions for PC1
    y = reduced_data[:, 1]  # variable contributions for PC2
    scalex = 1.0 / (x.max() - x.min())
    scaley = 1.0 / (y.max() - y.min())

    # Draw a data point projection plot that is projected to
    # a two-dimensional plane using normal PCA
    #for i, label in enumerate(classes):
        plt.scatter(x[labels == label] * scalex,
                    y[labels == label] * scaley,
                    linewidth=0.01)
        # hyperparameter in plt.scatter(): c=colors[i], marker=markers[i]
        legend.append("Label: {}".format(label))

    #plt.legend(legend)

    # plot arrows as the variable contribution,
    # each variable has a score for PC1 and for PC2 respectively
    for i in range(n):
        plt.arrow(0, 0, pc[0, i], pc[1, i], color='k', alpha=0.7,
                  linewidth=1, )
        plt.text(pc[0, i] * 1.01, pc[1, i] * 1.01, variable[i],
                 ha='center', va='center', color='k', fontsize=12)

    plt.xlabel("$PC1$")
    plt.ylabel("$PC2$")
    plt.title("Compositional biplot")
    plt.grid()
    # save_fig("Compositional biplot")