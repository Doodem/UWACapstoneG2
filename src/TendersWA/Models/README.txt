How to use Embedding_Model.py 


Embedding_Model.Sentence_Transformer

No variables required in intialization, inputs can be a single string, or a list of strings. Will return a single embedding of size 768. Forward function of class checks if input is a list or a single string. If a single string, then the string is processed and the embedding returned. If the input is a list, then the list is iterated over, with the sentence embedding of each item in the list acquired. Then average pooling is conducted to produce the document embedding. 

Example usage:

Import Embedding_Model as em

model = em.Sentence_transformer()
example = ["Supply and Delivery of Aspen Bedding Material","The Customer requires a Contractor to provide bedding material made from Aspen and must be suitable for its rats and mice"]

# to get document embedding
document_embedding = model(example)

# to get embedding of a single sentence or string
sentence_embedding = model(example[0])