import tensorflow as tf
import numpy as np

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer

import re
import string
import tqdm

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


def generate_arrays_from_file(path,batch_size,dict):
    while 1:
        cut_length=16
        max_length=64
        word_unk=np.random.random(size=(300,)) - 0.5
        word_unk=word_unk.tolist()
        word_emp=np.random.random(size=(300,)) - 0.5
        word_emp=word_emp.tolist()
        f = open(path)
        cnt = 0
        _data =[]
        _label =[]
        for line in f:
            # create Numpy arrays of input data
            # and labels, from each line in the file
            _label.append(int(line[0]))
            print(int(line[0]))
            line=line[1:].strip().lstrip('[').rstrip(']')
            line=line.replace('\'','').split(',')
            print(line[:3], '  ', line[len(line) - 2:])
            one_data=[]
            for word in line:
                if word in dict:
                    one_data.append(dict[word])
                else:
                    one_data.append(word_emp)
            for i in range(0, cut_length - len(line)):
                tmp_nparray = np.random.random(size=(300,)) - 0.5
                one_data.append(word_unk)
            _data.append(one_data[:max_length])
            cnt += 1
            if cnt==batch_size:
                cnt = 0
                yield (np.array(_data), np.array(_label))
                _data = []
                _label = []
    f.close()


def main():
    dict={}
    data_list, label_list = generate_arrays_from_file('./_data/EI_test.csv',32,dict)
    for i in range(0, 10):
        print(data_list[i])
        print(label_list[i])

if __name__ == '__main__':
    main()
