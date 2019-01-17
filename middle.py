import numpy as np
from sklearn.utils import shuffle
import tensorflow.keras as kr
from nltk.corpus import stopwords

import math
import random
import re
import string
import json

import data_processor
def load_model():
    model=[]
    model.append(kr.models.load_model('debug.h5'))
    model.append(kr.models.load_model('debug.h5'))
    model.append(kr.models.load_model('debug.h5'))
    model.append(kr.models.load_model('debug.h5'))
    word_vec=data_processor.load_emb_file('wiki.en.vec')
    return model,word_vec

def predict(posts,model,word_vec):
    max_len=40
    URL_RE = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    result=[0,0,0,0]
    word_unk = [random.uniform(-1, 1) for n in range(300)]
    word_emp = [0 for n in range(300)]
    post_embeddings=[]
    for post in posts:
        _post = re.sub(URL_RE, '<URL>', post)
        words = [w.lower() for w in _post.split() if w.isalpha()]
        punc_table = str.maketrans('', '', string.punctuation)
        stripped = [w.translate(punc_table) if w != '<url>' else w for w in words]
        clean_words=stripped[:max_len]
        print(len(clean_words))
        print(clean_words)
        word_embeddings=[]
        for word in clean_words:
            if word in word_vec:
                word_embeddings.append(word_vec[word])
            else:
                word_embeddings.append(word_unk)
        for i in range(0,max_len-len(clean_words)):
            word_embeddings.append(word_emp)
        print(np.array(word_embeddings).shape)
        post_embeddings.append(word_embeddings)
        print('!',np.array(post_embeddings).shape)
    post_embeddings=np.array(post_embeddings)
    print(post_embeddings.shape)
    for i in range(0,4):
        result[i] = np.mean(np.round(model[i].predict(np.array(post_embeddings))))
        print(result[i])
        print('--')
    return result
#sample
model,word_vec=load_model()
posts=['we are good and better.','what is this and what is that?']
predict_list=predict(posts,model,word_vec)
print(predict_list)
