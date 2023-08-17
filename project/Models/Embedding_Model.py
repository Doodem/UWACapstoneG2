# importing modules 
import pandas as pd
from torch import nn
from transformers import BertTokenizer, BertModel, BigBirdModel,AutoModelForSequenceClassification

#  model class 

class Pretrained_model(nn.Module):
    def __init__(self,model='bert'):
        super(Pretrained_model,self).__init__()
        
        if model.lower() =='bert':
            self.embedding_model = BertModel.from_pretrained('bert-base-cased')
            self.model_base = 'bert-base-cased'
        elif model.lower() == "longformer":
            self.embedding_model = AutoModelForSequenceClassification.from_pretrained("allenai/longformer-base-4096")
            self.model_base = "allenai/longformer-base-4096"
        elif model.lower() == "bigbird":
            self.embedding_model = BigBirdModel.from_pretrained("google/bigbird-roberta-base")
            self.model_base ="google/bigbird-roberta-base"
        
        
        
    def forward(self,input_data):
        _,pooled_output = self.embedding_model(input_data)
        return pooled_output
    
    


# preprocessing function
def preprocessing(data):
    pass

# evalaute function
def evaluate(data):
    pass