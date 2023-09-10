from transformers import BertTokenizer, BertForPreTraining
import torch
import pandas as pd
import os
import zipfile
import shutil
import sys
sys.path.append("../")
import Embedding_Model as em

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

model = BertForPreTraining.from_pretrained('bert-base-uncased')

# read test data 
import pandas as pd
data_file = pd.read_excel('../../../data/UpdatedAgainTenders.xlsx')
data =  list(data_file['Description'])
data = [em.remove_html_tags(text) for text in data]

# extract tenders from zip files using mitch's code 

def search(search_path):

    ref_dict = {}

# recursively through all files and folders
    for root, dirs, files in os.walk(search_path):
        for filename in files:
            if filename.endswith(".zip"):
                # get ref num
                ref = filename.rsplit("-specification.zip", 1)[0]
                file_path = os.path.join(root, filename)

                # open read zip
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    file_list = zip_ref.namelist()
                    doc_files = [file for file in file_list if "request" in file.lower() and file.lower().endswith(('.doc', '.docx'))]

                    if doc_files:
                        # add sub files, if any
                        ref_dict.setdefault(ref, []).extend([(doc_name, file_path) for doc_name in doc_files])

    for ref, doc_list in ref_dict.items():
        print(f"Reference: {ref}")
        for doc_name, file_path in doc_list:
            print(f"Document Name: {doc_name}, ZIP File Path: {file_path}")

    return ref_dict

###########################################
### filter for one relevant doc per ref ###
###########################################

def copy(copy_path, ref_dict):
    # make output folder, in not already there
    os.makedirs(copy_path, exist_ok=True)

    for ref, doc_list in ref_dict.items():
        for doc_name, file_path in doc_list:
            # copy relevant docs from zip to output folder
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                for file in zip_ref.namelist():
                    if file == doc_name:
                        extracted_path = os.path.join(copy_path, f"{ref}.docx")
                        with zip_ref.open(file) as source, open(extracted_path, "wb") as target:
                            shutil.copyfileobj(source, target)
                        print(f"Extracted: {doc_name} from {file_path} to {extracted_path}")
    return

zip_files_path = "..\..\..\data\Tenders"


output_folder = r"..\..\..\data\tender_docs_extracted_"

def extract(search_path, copy_path):
    ref_dict = search(search_path)
    copy(copy_path, ref_dict)    
    return

extract(zip_files_path, output_folder)

from docx import Document

def extract_doc_by_header(docx_path, target_header):
    doc = Document(docx_path)
    content = []
    current_header = None
    capture_content = False

    for paragraph in doc.paragraphs:
        if paragraph.style.name.startswith("Heading") and paragraph.text == target_header:
            current_header = paragraph.text
            capture_content = True
            content.append(current_header)
        elif capture_content:
            content.append(paragraph.text)
        
        # Stop capturing content if a new header is encountered
        if paragraph.style.name.startswith("Heading") and paragraph.text != current_header:
            capture_content = False
   
    return "\n".join(content)

header = "Background"
documents = []
failed =0

for item in os.listdir(r"..\..\..\data\tender_docs_extracted_"):
    try:
        
        link = output_folder + "\\" +item
       
        documents.append(extract_doc_by_header(link,header))
    except:
        failed+=1
        
        continue
        
        
documents

clipped_documents = []
for item in documents:
    thing = item[11::]
    thing = thing[:-20:]
    clipped_documents.append(thing)
    
data.extend(clipped_documents)

import random
def nsp_data(data):
    
    sentence_a = []
    sentence_b = []
    label = []

    for paragraph in data:
        sentences = [
            sentence for sentence in paragraph.split('.') if sentence != ' '
        ]
        if len(sentences) >1 :
            
            num_sentences = len(sentences)
            if num_sentences > 1:
                start = random.randint(0, num_sentences-2)
                # 50/50 whether is IsNextSentence or NotNextSentence
                if random.random() >= 0.5:
                    # this is IsNextSentence
                    sentence_a.append(sentences[start])
                    sentence_b.append(sentences[start+1])
                    label.append(0)
                else:
                    index = random.randint(0, num_sentences-1)
                    # this is NotNextSentence
                    sentence_a.append(sentences[start])
                    sentence_b.append(sentences[index])
                    label.append(1)

    inputs = tokenizer(sentence_a, sentence_b, return_tensors='pt',
                       max_length=512, truncation=True, padding='max_length')
    inputs['next_sentence_label'] = torch.LongTensor([label]).T
    return inputs

def mlm_data(inputs):
    inputs['labels'] = inputs.input_ids.detach().clone()
    # create random array of floats with equal dimensions to input_ids tensor
    rand = torch.rand(inputs.input_ids.shape)
    # create mask array
    mask_arr = (rand < 0.15) * (inputs.input_ids != 101) *  (inputs.input_ids != 102) * (inputs.input_ids != 0)
    selection = []

    for i in range(inputs.input_ids.shape[0]):
        selection.append(torch.flatten(mask_arr[i].nonzero()).tolist()
        )
    for i in range(inputs.input_ids.shape[0]):
        inputs.input_ids[i, selection[i]] = 103
    return inputs

class OurDataset(torch.utils.data.Dataset):
    def __init__(self, encodings):
        self.encodings = encodings
    def __getitem__(self, idx):
        return {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
    def __len__(self):
        return len(self.encodings.input_ids)
    
inputs_nsp = nsp_data(data)
inputs = mlm_data(inputs_nsp)
dataset = OurDataset(inputs)
loader = torch.utils.data.DataLoader(dataset, batch_size=16, shuffle=True)

from tqdm import tqdm  # for our progress bar
from transformers import AdamW
epochs = 2
device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
# and move our model over to the selected device
model.to(device)


# activate training mode
model.train()
# initialize optimizer
optim = AdamW(model.parameters(), lr=1e-4)

for epoch in range(epochs):
    # setup loop with TQDM and dataloader
    loop = tqdm(loader, leave=True)
    for batch in loop:
        # initialize calculated gradients (from prev step)
        optim.zero_grad()
        # pull all tensor batches required for training
        input_ids = batch['input_ids'].to(device)
        token_type_ids = batch['token_type_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        next_sentence_label = batch['next_sentence_label'].to(device)
        labels = batch['labels'].to(device)
        # process
        outputs = model(input_ids, attention_mask=attention_mask,
                        token_type_ids=token_type_ids,
                        next_sentence_label=next_sentence_label,
                        labels=labels)
        # extract loss
        loss = outputs.loss
        # calculate loss for every parameter that needs grad update
        loss.backward()
        # update parameters
        optim.step()
        # print relevant info to progress bar
        loop.set_description(f'Epoch {epoch}')
        loop.set_postfix(loss=loss.item())
        
model.save_model("fine_tuned_bert")
