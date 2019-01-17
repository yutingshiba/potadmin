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


def load_emb_file(file_name, debug=False):
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
            if(debug and i>10000):
                break
            tokens=[float(onetoken) for onetoken in tokens[1:len(tokens)-1]]
            word_vec[word]=tokens
    print('Loaded {} lines of embs with dim {}'.format(len(word_vec), 300))
    return word_vec


def parse_posts(posts_str, trunc_size=100, no_stopwords=False):
    posts = posts_str.split('|||')
    # filter out invalid posts
    posts_list = []
    url_count_list = []
    for post in posts:
        # replace url
        _post = re.sub(URL_RE, '<URL>', post)

        # to lower cast  \\  Drop if not alpha
        words = [w.lower() for w in _post.split()]
        #print(words)
        url_count = 0
        for w in words:
            if w  == '<url>':
                url_count += 1
        alpha_words = [w for w in words if w.isalpha()]
        #print(alpha_words, url_count)
        
        # Remove punctuation

        punc_table = str.maketrans('', '', string.punctuation)
        stripped = [w.translate(punc_table) if w != '<url>' else w for w in alpha_words]
        if no_stopwords:
            posts_list.append(stripped[:trunc_size])
            continue
        #print(stripped)

        # Remove stopwords
        stop_words = stopwords.words('english')
        clean_words = [w for w in stripped if w and w not in stop_words]
        #print(clean_words)

        #input()
        if clean_words:
            posts_list.append(clean_words[:trunc_size])
            url_count_list.append(url_count)
        
        '''
        # Stemming
        porter = PorterStemmer()
        stemmed = [porter.stem(w) for w in clean_words]
        posts_list.append(stemmed[:trunc_size])
        '''
    return posts_list, url_count_list


def gen_all_csv(fname='_data/complete.csv'):
    fp = open(fname, 'r')
    eifp = open('_data/EI_all_url)unsh.csv', 'w')
    nsfp = open('_data/NS_all_url_unsh.csv', 'w')
    tffp = open('_data/TF_all_url_unsh.csv', 'w')
    jpfp = open('_data/JP_all_url_unsh.csv', 'w')
    fp.readline()
    for line in fp:
        labels = line[:4]
        posts = line.rstrip('\n')[5:]
        posts_list, urlc_list = parse_posts(posts)
        for idx, post in enumerate(posts_list):
            # E I
            label = 1 if labels[0] == 'E' else 0
            eifp.write('{}\t{}\t{}\n'.format(label, post, urlc_list[idx]))
            # N S
            label = 1 if labels[1] == 'N' else 0
            nsfp.write('{}\t{}\t{}\n'.format(label, post, urlc_list[idx]))
            # T F
            label = 1 if labels[2] == 'T' else 0
            tffp.write('{}\t{}\t{}\n'.format(label, post, urlc_list[idx]))
            # J P
            label = 1 if labels[3] == 'J' else 0
            jpfp.write('{}\t{}\t{}\n'.format(label, post, urlc_list[idx]))



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

def generate_from_file(path, batch_size, word_vec, with_url=False, is_test=False):
    label_list = []
    post_list = []
    url_list = []
    # Load data
    min_len = 4 
    max_len = 40 
    with open(path) as fp:
        for line in fp:
            tokens = line.rstrip('\n').split('\t')
            post = json.loads(tokens[1])
            if len(post) < min_len:
                continue
            label_list.append(int(tokens[0]))
            post_list.append(post[:max_len])
            if with_url:
                url_list.append(int(tokens[2]))

    # Shuffle data
    if with_url:
        label_list, post_list, url_list = shuffle(label_list, post_list, url_list)
    else:
        label_list, post_list = shuffle(label_list, post_list)

    # Generate batches
    nb_batch = math.ceil(len(label_list) / batch_size)
    word_unk = [random.uniform(-1, 1) for n in range(300)]
    #word_unk = [-1 for n in range(300)]
    
    while 1:
        for n in range(nb_batch):
            inputs = []
            if with_url:
                for idx, post in enumerate(post_list[n*batch_size: (n+1)*batch_size]):
                    inputs.append([padded(post, word_vec, word_unk, pad_len=max_len), url_list[n*batch_size + idx]])
            else:
                for post in post_list[n*batch_size: (n+1)*batch_size]:
                    inputs.append(padded(post, word_vec, word_unk, pad_len=max_len))
            outputs = label_list[n*batch_size: (n+1)*batch_size]
            
            if is_test:
                yield (np.array(inputs))
            else:
                yield (np.array(inputs), np.array(outputs))


def get_sentence_length(path):
    f=open(path)
    dict={}
    for i in range(0,1000):
        dict[i]=0
    for line in f:
        tokens=line.rstrip('\n').split('\t')
        post=json.loads(tokens[1])
        dict[len(post)]+=1
    for i in range(0,1000):
        if(dict[i]>0):
            print(i,": ",dict[i])

def get_size(path):
    f=open(path)
    cut_length = 4
    cnt=0
    for line in f:
        tokens=line.rstrip('\n').split('\t')
        post=json.loads(tokens[1])
        if(len(post) >= cut_length):
            cnt+=1
    return cnt

def main():
    dict={}
    data_list, label_list = generate_arrays_from_file('./_data/EI_test.csv',32,dict)
    for dd in data_list:
        print(dd)
        input()

def load_test_true(path):
    label_list = []
    with open(path, 'r') as fp:
        for line in fp:
            tokens = line.rstrip('\n').split('\t')
            ws = json.loads(tokens[1])
            if len(ws) < 4:
                continue
            label = int(tokens[0])
            label_list.append(label)
    return np.array(label_list)

if __name__ == '__main__':
    gen_all_csv()
    #ll = load_test_true('_data/TF_test.csv')
    #print(ll.shape[0])
