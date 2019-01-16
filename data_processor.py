import numpy as np
from sklearn.utils import shuffle

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer

import math
import random
import re
import string
import tqdm
import json

URL_RE = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'


def load_emb_file(file_name):
    if not file_name:
        print('No filename specified')
        return
    word_vec = {}
    i=0
    with open(file_name) as fp:
        for line in fp:
            tokens = line.rstrip('\n').split(' ')
            if(i==0):
                print(tokens)
                i=1
            word=tokens[0]
            if(i<=10):
                print(tokens[:5],'   ',tokens[len(tokens)-3:])
            i=i+1
            if(i%100000==0):
                print("read ",i," embeddings")
            if(i>10000):
                break
            tokens=[float(onetoken) for onetoken in tokens[1:len(tokens)-1]]
            word_vec[word]=tokens
    print('Loaded {} lines of embs with dim {}'.format(len(word_vec), 300))
    return word_vec


def parse_posts(posts_str, trunc_size=100, no_stopwords=False):
    posts = posts_str.split('|||')
    # filter out invalid posts
    posts_list = []
    for post in posts:
        # replace url
        _post = re.sub(URL_RE, '<URL>', post)

        # to lower cast  \\  Drop if not alpha
        words = [w.lower() for w in _post.split() if w.isalpha()]
        
        # Remove punctuation
        punc_table = str.maketrans('', '', string.punctuation)
        stripped = [w.translate(punc_table) if w != '<url>' else w for w in words]
        if no_stopwords:
            posts_list.append(stripped[:trunc_size])
            continue

        # Remove stopwords
        stop_words = stopwords.words('english')
        clean_words = [w for w in stripped if w and w not in stop_words]

        posts_list.append(clean_words[:trunc_size])
        
        '''
        # Stemming
        porter = PorterStemmer()
        stemmed = [porter.stem(w) for w in clean_words]
        posts_list.append(stemmed[:trunc_size])
        '''
    return posts_list


def padded(post, word_vec, unk,  pad_len=64):
    post_emb = []
    for word in post[:pad_len]:
        if word in word_vec:
            post_emb.append(word_vec[word])
        else:
            post_emb.append(unk)
    # padded to pad_len
    for i in range(pad_len - len(post_emb)):
        post_emb.append([0.] * 300)
    
    return post_emb

def generate_from_file(path, batch_size, word_vec, is_test=False):
    label_list = []
    post_list = []
    # Load data
    min_len = 8
    max_len = 40 
    with open(path) as fp:
        for line in fp:
            tokens = line.rstrip('\n').split('\t')
            post = json.loads(tokens[1])
            if len(post) < min_len:
                continue
            label_list.append(int(tokens[0]))
            post_list.append(post[:max_len])

    # Shuffle data
    label_list, post_list = shuffle(label_list, post_list)

    # Generate batches
    nb_batch = math.ceil(len(label_list) / batch_size)
    word_unk = [random.uniform(-1, 1) for n in range(300)]
    
    while 1:
        for n in range(nb_batch):
            inputs = []
            for post in post_list[n*batch_size: (n+1)*batch_size]:
                inputs.append(padded(post, word_vec, word_unk, pad_len=max_len))
            outputs = label_list[n*batch_size: (n+1)*batch_size]
            
            if is_test:
                yield (np.array(inputs))
            else:
                yield (np.array(inputs), np.array(outputs))


def get_size(path):
    f=open(path)
    cnt=0
    for line in f:
        cnt+=1
    return cnt

def main():
    dict={}
    data_list, label_list = generate_arrays_from_file('./_data/EI_test.csv',32,dict)
    for dd in data_list:
        print(dd)
        input()

if __name__ == '__main__':
    main()
