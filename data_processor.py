import tensorflow as tf
import numpy as np

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

import re
import string
import tqdm

URL_RE = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'


def load_emb_file(file_name):
    if not file_name:
        print('No filename specified')
        return
    word_vec = {}
    with open(file_name) as fp:
        for line in tqdm(fp):
            tokens = line.rstrip('\n').split(' ')
            word=wokens[0]
            tokens=[float(onetoken) for onetoken in tokens[1:]]
            word_vec[word]=tokens
    print('Loaded {} lines of embs with dim {}'.format(len(word_vec), 300))
    return word_vec


def parse_posts(posts_str, trunc_size=100, no_stopwords=True):
    posts = posts_str.split('|||')
    # filter out invalid posts
    posts_list = []
    for post in posts:
        # replace url
        _post = re.sub(URL_RE, '<URL>', post)
        if not _post:
            continue
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
        clean_words = [w for w in stripped if not w in stop_words]

        posts_list.append(clean_words[:trunc_size])

    return posts_list


def load_train_data(file_name='train_data.csv'):
    label_list = []
    post_list = []
    dict,embs=load_emb_file('wiki.en.vec')
    cut_post_length=64
    min_post_length=48
    with open(file_name) as fp:
        fp.readline()   # skip the first line 
        for line in tqdm(fp):
            # load raw input data line by line
            _label = line[:5]
            label = 1 if _label[0] == 'E' else 0

            #posts = filter_posts(tokens[1])
            posts = parse_posts(line.rstrip('\n')[5:])
            for post in posts:
                # treat each post regardless of author
                if(len(post)>min_post_length):
                    label_list.append(label)
                    one_post_list=[]
                    for word in post:
                        if word in dict:
                            one_post_list.append(embs[dict[word]])
                        else:
                            tmp_nparray=np.random.random(size=(300,)) - 0.5
                            one_post_list.append(tmp_nparray.tolist())
                    for i in range(0,cut_post_length-len(post)):
                        tmp_nparray=np.random.random(size=(300,)) - 0.5
                        one_post_list.append(tmp_nparray.tolist())
                    post_list.append(one_post_list)

    return np.array(label_list), np.array(post_list)


def main():
    l_list, p_list = load_train_data('./_data/train_small.csv')
    for i in range(0, 10):
        print(l_list[i])
        print(p_list[i])

if __name__ == '__main__':
    main()
