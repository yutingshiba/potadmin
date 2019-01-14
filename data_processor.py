import tensorflow as tf
import numpy as np

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

import re
import string

URL_RE = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'


def load_emb_file(file_name):
    if not file_name:
        print('No filename specified')
        return
    vocab = []
    embs = []
    with open(file_name) as fp:
        for line in fp:
            tokens = line.rstrip('\n').split(' ')
            vocab.append(tokens[0])
            embs.append(tokens[1:])
    
    print('Loaded {} lines of embs with dim {}'.format(len(vocab), len(embs[0][0])))
    return vocab, embs


def get_embedding(file_name):
    if not file_name:
        print('No filename specified')
        return

    vocab, embs = load_emb_file(file_name)
    W_emb = tf.Variable(tf.constant(0.0, shape=[vocab_size, embedding_dim]), trainable=False, name="W_emb")
    embedding_placeholder = tf.placeholder(tf.float32, [vocab_size, embedding_dim])
    embedding_init = W.assign(embedding_placeholder)
    """
    TO DO
    """
    return
    


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
    with open(file_name) as fp:
        fp.readline()   # skip the first line 
        for line in fp:
            # load raw input data line by line
            _label = line[:5]
            label = 1 if _label[0] == 'E' else 0

            #posts = filter_posts(tokens[1])
            posts = parse_posts(line.rstrip('\n')[5:])
            for post in posts:
                # treat each post regardless of author
                label_list.append(label)
                post_list.append(post)

    return label_list, post_list


def main():
    l_list, p_list = load_train_data('./_data/train_small.csv')
    for i in range(0, 10):
        print(l_list[i])
        print(p_list[i])

if __name__ == '__main__':
    main()
