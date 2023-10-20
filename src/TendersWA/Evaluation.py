from rouge import Rouge
from bert_score import score

def eval_rouge(reference_list, generated_list):
    rouge = Rouge()
    rouge_scores = rouge.get_scores(reference_list, generated_list)
    return rouge_scores

# returns a tuple of tensor precision, recall and f1.
def eval_bert_score(reference_list, generated_list):
    return score(reference_list, generated_list, lang='en', rescale_with_baseline=True)