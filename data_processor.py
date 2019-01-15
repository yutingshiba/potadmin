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

        # to lower cast
        words = [w.lower() for w in _post.split()]
        
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


def load_train_data(file_name='train_data.csv'):
    label_list = []
    post_list = []
    dict=load_emb_file('wiki.en.vec')
    cut_post_length=64
    min_post_length=16
    num=0
    with open(file_name) as fp:
        fp.readline()   # skip the first line 
        for line in fp:
            # load raw input data line by line
            _label = line[:5]
            label = 1 if _label[0] == 'E' else 0
            #posts = filter_posts(tokens[1])
            posts = parse_posts(line.rstrip('\n')[5:])
            #print("!")
            for post in posts:
                #print(post)
                # treat each post regardless of author
                if(len(post)>min_post_length):
                    label_list.append(label)
                    one_post_list=[]
                    for word in post:
                        if word in dict:
                            one_post_list.append(dict[word])
                        else:
                            tmp_nparray=np.random.random(size=(300,)) - 0.5
                            one_post_list.append(tmp_nparray.tolist())
                    for i in range(0,cut_post_length-len(post)):
                        tmp_nparray=np.random.random(size=(300,)) - 0.5
                        one_post_list.append(tmp_nparray.tolist())
                    post_list.append(one_post_list[:64])
                    num=num+1
                if(num%1000==0):
                    print(num," items")
                if(num>=4000):
                    break
    print(np.array(label_list).shape)
    print(np.array(post_list).shape)
    return np.array(label_list), np.array(post_list)


def main():
    l_list, p_list = load_train_data('./_data/complete.csv')
    for i in range(0, 10):
        print(l_list[i])
        print(p_list[i])

if __name__ == '__main__':
    main()
