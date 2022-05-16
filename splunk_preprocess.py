import xml.etree.ElementTree as ET

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
            elif symbol in ['=', '>', '<', '+', '-', '*', '/', '(', ')', '[', ']']:
                if len(token) > 0 :
                    tokens.append(token)
                tokens.append(symbol)
                token = ''
            else:
                token = token + symbol
    return tokens

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

item = searches[0]
print(parse(item['enterprise']))
