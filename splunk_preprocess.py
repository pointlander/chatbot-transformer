import xml.etree.ElementTree as ET
import json

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

max_len = 0
tree = ET.parse('MasheryReportingModel.xml')
root = tree.getroot()
searches = []
for item in root.findall('./SplunkSavedSearches/SplunkSavedSearch'):
    search = {}
    for child in item:
        if child.tag == 'SearchString':
            search['enterprise'] = child.text
        elif child.tag == 'SearchStringCloud':
            search['cloud'] = child.text
    if ('enterprise' in search.keys()) and ('cloud' in search.keys()):
        searches.append(search)

# item = searches[0]
# print(parse(item['enterprise']))

min_word_freq = 5
pairs = []
word_freq = {}
for item in searches:
    pair = []
    pair.append(parse(item['enterprise']))
    pair.append(parse(item['cloud']))
    pairs.append(pair)
    if len(pair[0]) > max_len:
        max_len = len(pair[0])
    if len(pair[1]) > max_len:
        max_len = len(pair[1])
    for word in pair[0]:
        word_freq[word] = word_freq.get(word, 0) + 1
    for word in pair[1]:
        word_freq[word] = word_freq.get(word, 0) + 1

words = [w for w in word_freq.keys()]
word_map = {k: v + 1 for v, k in enumerate(words)}
word_map['<unk>'] = len(word_map) + 1
word_map['<start>'] = len(word_map) + 1
word_map['<end>'] = len(word_map) + 1
word_map['<pad>'] = 0


print("Total words are: {}".format(len(word_map)))


with open('WORDMAP_corpus.json', 'w') as j:
    json.dump(word_map, j)


def encode_question(words, word_map):
    enc_c = [word_map.get(word, word_map['<unk>']) for word in words] + [word_map['<pad>']] * (max_len - len(words))
    return enc_c


def encode_reply(words, word_map):
    enc_c = [word_map['<start>']] + [word_map.get(word, word_map['<unk>']) for word in words] +     [word_map['<end>']] + [word_map['<pad>']] * (max_len - len(words))
    return enc_c

pairs_encoded = []
for pair in pairs:
    qus = encode_question(pair[0], word_map)
    ans = encode_reply(pair[1], word_map)
    pairs_encoded.append([qus, ans])

with open('pairs_encoded.json', 'w') as p:
    json.dump(pairs_encoded, p)
