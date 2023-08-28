import numpy as np
import nltk
import pandas as pd
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
from nltk.stem import WordNetLemmatizer as wordLem
from nltk.corpus import wordnet

stop_words = ['i', 'a','actually','almost','also','although', 'do','always', 'about', 'an', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'how', 'in', 'is',
             'it', 'of', 'on','or', 'that', 'the', 'this', 'to', 'was', 'what', 'when', 'where', 'who', 'will', 'with', 'the', 'www','and','am','any',
             'become','became','but','by','can','could','did','he','she','him','his','mr','ms','our','she','so','too','us','do','does','each','either','else','for','from','had','has','have','hence','how','if',
             'just','may','maybe','me','might','mine','must','my','neither','nor','not','oh','ok','whereas','wherever','whenever','whether','which',
             'while','whom','whoever','whose','why','within','would','yes','yet','you','your']

lemm = wordLem()
def pos_tagger(nltk_tag):
    if nltk_tag.startswith('J'):
        return wordnet.ADJ
    elif nltk_tag.startswith('V'):
        return wordnet.VERB
    elif nltk_tag.startswith('N'):
        return wordnet.NOUN
    elif nltk_tag.startswith('R'):
        return wordnet.ADV
    else:
        return None
def preproccesing(docs):
    docs = docs.strip()
    docs =docs.lower()
    docs =docs.split()
    l = []
    for words in docs:
        para=''
        for char in words:
            if ord(char) < 128:
                para+=char
            else:
                para=''
                break
        words=para
        if len(words)>0 and words.isalnum():
            while words[-1] in [',', '.', ';', '?', ')', ']', '}', ':', "\"", "'","\\","!"]:
                words = words[:-1]
            while words[0] in ["\"", "'", '{', '[', '(']:
                words = words[1:]
            if words[-2:] in ["'s", "'t"]:
                words = words[:-2]
            if words[-3:] in ["'re", "'ll", "'ve"]:
                words = words[:-3]
            if '-' in words:
                for j in words.split('-'):
                    l.append(j)
            elif len(words)>1 or (len(words)==1 and words.isnumeric()):
                l.append(words)
        elif '-' in words:
            for j in words.split('-'):
                    l.append(j)
    sentence =' '.join(l)
    pos_tagged = nltk.pos_tag(nltk.word_tokenize(sentence.lower()))
    wordnet_tagged = map(lambda y: (y[0], pos_tagger(y[1])), pos_tagged)
    wordnet_tagged=list(wordnet_tagged)
    lemmatized_sentence = []
    for word, tag in wordnet_tagged:
        if tag is None and word not in stop_words:
            lemmatized_sentence.append(word)
        elif word not in stop_words:
            lemmatized_sentence.append(lemm.lemmatize(word, tag))

    lemmatized_sentence = " ".join(lemmatized_sentence)
    return lemmatized_sentence
def indexing(document_list):
    l = []
    for i in document_list:
        split_document = i.split(' ')
        for j in split_document:
            if len(j)>1:
                l.append(j)
    uni_words = list(set(l))
    uni_words.sort()
    index_table = pd.DataFrame(np.array([np.array([0] * len(uni_words))] * (len(document_list) + 2)), columns=uni_words)
    counter = 1
    for words in uni_words:
        counter += 1
        for d in range(len(document_list)):
            index_table.loc[d, words] = document_list[d].count(words)
        docfreq = len(index_table[words]) - list(index_table[words]).count(0)
        index_table.loc[len(document_list), words] = docfreq
        idf = np.log(len(document_list) / docfreq)
        index_table.loc[len(document_list) + 1, words] = idf

    for i in range(len(document_list)):
        index_table.iloc[i] = index_table.iloc[i] * index_table.iloc[len(document_list) + 1]
        index_table.iloc[i] = index_table.iloc[i] / np.sqrt(sum(index_table.iloc[i] ** 2))
    return [index_table, uni_words]
def evaluate_query(query,docs,uniquewords,index_table,links):
    temp = []
    q = query.split(' ')
    for i in q:
        if i in uniquewords:
            temp.append(i)
    temp.sort()
    index_query_table = pd.DataFrame(np.array([np.array([0] * len(uniquewords))]), columns=uniquewords)
    for w in temp:
        index_query_table.loc[0, w] = temp.count(w)
    index_query_table.iloc[0] = index_table.iloc[len(docs) + 1] * index_query_table.iloc[0]
    index_query_table.iloc[0] = index_query_table.iloc[0] / np.sqrt(sum(index_query_table.iloc[0] ** 2))
    ranks = []
    for i in range(len(docs)):
        s = np.dot(index_table.iloc[i], index_query_table.iloc[0])
        ranks.append(s)
    rank_dic=[]
    for i in range(len(ranks)):
        if pd.isna(ranks[i]):
            rank_dic.append((0, links[i], docs[i]))
        else:
            rank_dic.append((ranks[i], links[i], docs[i]))
    rank_dic.sort(reverse=True)
    return rank_dic
def load_table(path):
    df = pd.read_csv(path)
    df = df.iloc[:, 1:]
    return df
def load_documents(path):
    docs=[]
    links=[]
    data = open(path, 'r')
    temp = data.read().split('\n')
    temp2 = []
    datap={}
    for i in temp:
        temp2.append(i.split('||'))
    for i in temp2:
        if len(i) >= 2:
            docs.append(i[0])
            links.append(i[-1])
            datap[i[1]] = i[1:-1]
    return [docs,links,datap]
def load_words(path):
    data = open(path, 'r')
    data = data.read().split(',')
    return data
def save_table(df, path):
    df.to_csv(path)
def save_documents(data,datap,path,linker):
    temp = []
    for i in range(len(data)):
        p=''
        for j in data[i]:
            if ord(j)<128:
                p+=j
        d=[]
        for k in datap[linker[i]]:
            t = ''
            for n in k:
                if ord(n)<128 and ord(n)!=10:
                    t+=n
            if len(t)>0:
                d.append(t)
        p+='||'+'||'.join(d)
        temp.append(p +'||'+ linker[i])
    with open(path, 'w') as f:
        f.write('\n'.join(temp))
def save_words(data,path):
    with open(path, 'w') as f:
        temp=[]
        for i in data:
            p=''
            for j in i:
                if ord(j)<128:
                    p+=j
                else:
                    p=''
                    break
            if len(p)>0:
                temp.append(p)
        f.write(','.join(temp))
