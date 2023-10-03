import sys
import tomotopy as tp

def train(model, save_path, stopping_factor = 1.01):
    model.train(0)
    print('Num docs:', len(model.docs), ', Vocab size:', len(model.used_vocabs), ', Num words:', model.num_words, flush=True)
    print('Removed top words:', model.removed_top_words, flush=True)
    print('Training...', flush=True)
    its = 0
    gradient_stop = False
    best_lost_seen = -10000000000
    while its < 1000 and not gradient_stop:
        model.train(7)
        model.train(3, freeze_topics=True)
        print('Iteration: {:05}\tll per word: {:.5f}\tperplexity: {:.5f}'.format(model.global_step, model.ll_per_word, model.perplexity), flush=True)
        its += 10
        if model.ll_per_word > best_lost_seen:
            best_lost_seen = model.ll_per_word
        
        # early stopping
        if model.ll_per_word < stopping_factor*best_lost_seen:
            gradient_stop = True
        
    if gradient_stop:
        print("Early stopping at {:05} with loss {:.5f}\tperplexity: {:.5f}".format(model.global_step, model.ll_per_word, model.perplexity), flush=True)

    print("Train for a bit more, finalize topics")
    for _ in range(0, 100, 10):
        model.train(10, freeze_topics=True)
        print('Iteration: {:05}\tll per word: {:.5f}\tperplexity: {:.5f}'.format(model.global_step, model.ll_per_word, model.perplexity), flush=True)

    print('Saving...', flush=True)
    model.save(save_path, True)
    
def create_corpus(docs, save_path):
    from nltk.corpus import stopwords
    stops = set(stopwords.words('english'))
    corpus = tp.utils.Corpus(
        tokenizer=tp.utils.SimpleTokenizer(), # leave empty tokenizer as it doesnt seem to work without 
        stopwords=lambda x: len(x) <= 2 or x in stops
    )
    corpus.process(docs)
    corpus.save(save_path)
    return corpus
    
def load_corpus(path):
    try:
        return tp.utils.Corpus.load(path)
    except IOError:
        print("No corpus file")
        return None
    
def get_topic_distribution(model,document_index,n,with_topics=True):
    '''
    model: An HPA model 
    document_index: an index corresponding to the tender list used to train the model
    n: the number of topics you want returned in order of highest to lowest probability
    with_topics: boolean, if you want topic index, or topic name returned
    
    returns the topic distribution for a single document in the form of a list of tupals, of format [(list of topic words,prob),...] 
    '''
    doc = model.docs[document_index]
    topic_probs = doc.get_topics()[:n:]
        
    if with_topics:
        output = []
        for topic_id, prob in topic_probs:
            topic_words = model.get_topic_words(topic_id, top_n=5) 
            words_temp = ", ".join([word for word, weight in topic_words])
            output.append((words_temp,round(prob,4)))
        return output
    else:
        return topic_probs

def compute_sub_topic_to_super_topic_mapping(model):
    '''
    model: HPA model
    returns a map assigning each sub topic number to its highest probability super topic, along with probability
    '''
    sub_topic_map = {}
    for super_k in range(0,model.k1):
        sub_topics = model.get_sub_topics(super_k, model.k2)
        for sub_k, prob in sub_topics:
            if sub_k in sub_topic_map:
                if prob > sub_topic_map[sub_k].prob:
                    sub_topic_map[sub_k] = {prob: prob, super_k: super_k}
            else:
                sub_topic_map[sub_k] = {prob: prob, super_k: super_k}
    return sub_topic_map
        
    