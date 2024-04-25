from transformers import AutoModel, AutoTokenizer
import torch
import os
import numpy as np
from local_data_handler import *

os.environ["TRANSFORMERS_OFFLINE"] = "1"

# model_ckpt = "distilbert-base-cased"
model_ckpt = "KB/bert-base-swedish-cased" # ckpt = "checkpoint"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# model = AutoModel.from_pretrained(model_ckpt).to(device)

tokenizer = AutoTokenizer.from_pretrained('./kb-bert-base-swedish-cased', local_files_only=True)
model = AutoModel.from_pretrained("./kb-bert-base-swedish-cased", local_files_only=True).to(device)

def tokenize(batch):
    return tokenizer(batch["text"], padding=True, truncation=True)

def extract_cls_vectors(batch):
    # Place model inputs on the GPU
    inputs = {k:v.to(device) for k,v in batch.items() 
              if k in tokenizer.model_input_names}
    # Extract last hidden states
    with torch.no_grad():
        last_hidden_state = model(**inputs).last_hidden_state
    # Return vector for [CLS] token
    return {"hidden_state": last_hidden_state[:,0].cpu().numpy()}

TRAINING_LOC = "data/json/training"
def load_dataset():
    json_files = get_jsons_of_dir(TRAINING_LOC)
    

if __name__ == '__main__':
    text = "this is a test"
    encoded_text = tokenizer(text)
    print(f"encoded text: {encoded_text}")
    tokens = tokenizer.convert_ids_to_tokens(encoded_text.input_ids)
    print(tokens)


    # inputs = tokenizer(text, return_tensors="pt") # pt -> return pytorch tensors
    # print(f"Input tensor shape: {inputs['input_ids'].size()}")
    # inputs = {k:v.to(device) for k,v in inputs.items()}
    # with torch.no_grad():
    #     outputs = model(**inputs)
    # print(outputs.last_hidden_state.size())
    # print(outputs.last_hidden_state)
    # For classification tasks, it is common practice to just use the hidden state associated with the [CLS] token as the input feature. 
    # Since this token appears at the start of each sequence, we can extract it by simply indexing into outputs.last_hidden_state as follows:
    # print(f"last_hidden_state size: {outputs.last_hidden_state[:,0].size()}")
    # print(outputs.last_hidden_state[:,0])
