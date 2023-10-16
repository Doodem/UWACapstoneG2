import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation

# common stop words taken from sklearn, followed by some we noticede are useful to remove.
stopwords  = ["a","about","above","across","after","afterwards","again","against","all","almost","alone","along","already","also","although","always","am","among","amongst","amoungst","amount","an","and","another","any","anyhow","anyone","anything","anyway","anywhere","are","around","as","at","back","be","became","because","become","becomes","becoming","been","before","beforehand","behind","being","below","beside","besides","between","beyond","bill","both","bottom","but","by","call","can","cannot","cant","co","con","could","couldnt","cry","de","describe","detail","do","done","down","due","during","each","eg","eight","either","eleven","else","elsewhere","empty","enough","etc","even","ever","every","everyone","everything","everywhere","except","few","fifteen","fifty","fill","find","fire","first","five","for","former","formerly","forty","found","four","from","front","full","further","get","give","go","had","has","hasnt","have","he","hence","her","here","hereafter","hereby","herein","hereupon","hers","herself","him","himself","his","how","however","hundred","i","ie","if","in","inc","indeed","interest","into","is","it","its","itself","keep","last","latter","latterly","least","less","ltd","made","many","may","me","meanwhile","might","mill","mine","more","moreover","most","mostly","move","much","must","my","myself","name","namely","neither","never","nevertheless","next","nine","no","nobody","none","noone","nor","not","nothing","now","nowhere","of","off","often","on","once","one","only","onto","or","other","others","otherwise","our","ours","ourselves","out","over","own","part","per","perhaps","please","put","rather","re","same","see","seem","seemed","seeming","seems","serious","several","she","should","show","side","since","sincere","six","sixty","so","some","somehow","someone","something","sometime","sometimes","somewhere","still","such","system","take","ten","than","that","the","their","them","themselves","then","thence","there","thereafter","thereby","therefore","therein","thereupon","these","they","thick","thin","third","this","those","though","three","through","throughout","thru","thus","to","together","too","top","toward","towards","twelve","twenty","two","un","under","until","up","upon","us","very","via","was","we","well","were","what","whatever","when","whence","whenever","where","whereafter","whereas","whereby","wherein","whereupon","wherever","whether","which","while","whither","who","whoever","whole","whom","whose","why","will","with","within","without","would","yet","you","your","yours","yourself","yourselves",
             
"business", "businesses", "service", "services", "provision", "provisions", "department", "departments", "project", "projects", "work", "works", "temporary", "management", "tender", "tenders", "briefing", "end", "communication"]

class LDATopicModeller:
    def __init__(self, docs):
        # uses tf-idf as well to remove common/bad words
        self.tfidf_vectorizer = TfidfVectorizer(stop_words=stopwords, min_df=1, max_df = 0.3)
        self.tfidf_vectorizer.fit(docs)

    def get_topics(self, subset_docs, n_topics = 5):
        tfidf = self.tfidf_vectorizer.transform(subset_docs)
        lda = LatentDirichletAllocation(n_components=1, max_iter=20, learning_method="batch")
        lda_fitted = lda.fit(tfidf)
        topics = self.tfidf_vectorizer.get_feature_names_out()[lda_fitted.components_.argsort()]
        topics = list(topics[0][-n_topics:])
        return topics