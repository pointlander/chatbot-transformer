import xml.etree.ElementTree as ET
import json
import torch
from torch.utils.data import Dataset
import torch.utils.data
from models import *
from utils import *

ckpt_path = 'checkpoint_9.pth.tar'

def parse(value):
    token = ''
    quote = False
    tokens = []
    for symbol in value:
        if quote:
            if symbol == '"':
                quote = False
                token = token + symbol
                tokens.append(token)
                token = ''
            elif symbol == "'":
                quote = False
                token = token + symbol
                tokens.append(token)
                token = ''
            elif symbol == '`':
                quote = False
                token = token + symbol
                tokens.append(token)
                token = ''
            else:
                token = token + symbol
        else:
            if symbol == '"':
                if len(token) > 0 :
                    tokens.append(token)
                quote = True
                token = ''
                token = token + symbol
            elif symbol == "'":
                if len(token) > 0 :
                    tokens.append(token)
                quote = True
                token = ''
                token = token + symbol
            elif symbol == '`':
                if len(token) > 0 :
                    tokens.append(token)
                quote = True
                token = ''
                token = token + symbol
            elif symbol == ' ' or symbol == '\t' or symbol == '\r' or symbol == '\n':
                if len(token) > 0 :
                    tokens.append(token)
                    token = ''
            elif symbol in ['|', '=', '>', '<', '+', '-', '*', '/', '(', ')', '[', ']']:
                if len(token) > 0 :
                    tokens.append(token)
                tokens.append(symbol)
                token = ''
            else:
                token = token + symbol
    return tokens

def evaluate(transformer, question, question_mask, max_len, word_map):
    """
    Performs Greedy Decoding with a batch size of 1
    """
    rev_word_map = {v: k for k, v in word_map.items()}
    transformer.eval()
    start_token = word_map['<cloud>']
    encoded = transformer.encode(question, question_mask)
    words = torch.LongTensor([[start_token]]).to(device)

    for step in range(max_len - 1):
        size = words.shape[1]
        target_mask = torch.triu(torch.ones(size, size)).transpose(0, 1).type(dtype=torch.uint8)
        target_mask = target_mask.to(device).unsqueeze(0).unsqueeze(0)
        decoded = transformer.decode(words, target_mask, encoded, question_mask)
        predictions = transformer.logit(decoded[:, -1])
        _, next_word = torch.max(predictions, dim = 1)
        next_word = next_word.item()
        if next_word == word_map['<end>']:
            break
        words = torch.cat([words, torch.LongTensor([[next_word]]).to(device)], dim = 1)   # (1,step+2)

    # Construct Sentence
    if words.dim() == 2:
        words = words.squeeze(0)
        words = words.tolist()

    sen_idx = [w for w in words if w not in {word_map['<start>']}]
    sentence = ' '.join([rev_word_map[sen_idx[k]] for k in range(len(sen_idx))])

    return sentence


checkpoint = torch.load(ckpt_path)
transformer = checkpoint['transformer']
with open('WORDMAP_corpus.json', 'r') as j:
    word_map = json.load(j)
print("loaded")

tree = ET.parse('MasheryReportingModel.xml')
root = tree.getroot()
for item in root.findall('./SplunkSavedSearches/SplunkSavedSearch'):
    search = {}
    for child in item:
        if child.tag == 'SearchString':
            search['enterprise'] = child.text
        elif child.tag == 'SearchStringCloud':
            search['cloud'] = child.text
    if ('enterprise' in search.keys()) and not ('cloud' in search.keys()):
        max_len = 1000
        enc_qus = [word_map['<enterprise>']] + [word_map.get(word, word_map['<unk>']) for word in parse(search['enterprise'])] + [word_map['<end>']]
        question = torch.LongTensor(enc_qus).to(device).unsqueeze(0)
        question_mask = (question!=0).to(device).unsqueeze(1).unsqueeze(1)
        sentence = evaluate(transformer, question, question_mask, int(max_len), word_map)
        print(sentence)

#while(1):
#    question = input("Question: ")
#    if question == 'quit':
#        break
#    max_len = input("Maximum Reply Length: ")
#    enc_qus = [word_map.get(word, word_map['<unk>']) for word in question.split()]
#    question = torch.LongTensor(enc_qus).to(device).unsqueeze(0)
#    question_mask = (question!=0).to(device).unsqueeze(1).unsqueeze(1)
#    sentence = evaluate(transformer, question, question_mask, int(max_len), word_map)
#    print(sentence)
