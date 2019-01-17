import numpy as np
from sklearn.utils import shuffle
import tensorflow.keras as kr
import tensorflow.keras.layers as ly
from nltk.corpus import stopwords

import math
import random
import re
import string
import json

import data_processor

def tp(y_true,y_pred):
    return kr.backend.sum(y_true * kr.backend.round(y_pred))
def tn(y_true, y_pred):
    return kr.backend.sum((1-y_true) * (1-kr.backend.round(y_pred)))
def fp(y_true, y_pred):
    return kr.backend.sum((1-y_true)*kr.backend.round(y_pred))
def fn(y_true, y_pred):
    return kr.backend.sum(y_true * (1-kr.backend.round(y_pred)))
def precision(y_true,y_pred):
    tensor1 = tp(y_true,y_pred)
    tensor2 = tp(y_true,y_pred)+fp(y_true,y_pred)
    return ly.Lambda(lambda x: x[0]/x[1])([tensor1, tensor2])
def recall(y_true,y_pred):
    tensor1 = tp(y_true,y_pred)
    tensor2 = tp(y_true,y_pred)+fn(y_true,y_pred)
    return ly.Lambda(lambda x: x[0]/x[1])([tensor1, tensor2])
def f1(y_true,y_pred):
    return 2./(1./recall(y_true,y_pred)+1./precision(y_true,y_pred))
def load_model():
    model=[]
    model.append(kr.models.load_model('EI_0.0008_2.h5',custom_objects={'f1':f1,'recall':recall,'precision':precision,
        'tp':tp,'tn':tn,'fp':fp,'fn':fn}))
    model.append(kr.models.load_model('NS_0.0008_2.h5',custom_objects={'f1':f1,'recall':recall,'precision':precision,
        'tp':tp,'tn':tn,'fp':fp,'fn':fn}))
    model.append(kr.models.load_model('TF_0.0008_2.h5',custom_objects={'f1':f1,'recall':recall,'precision':precision,
        'tp':tp,'tn':tn,'fp':fp,'fn':fn}))
    model.append(kr.models.load_model('JP_0.0008_2.h5',custom_objects={'f1':f1,'recall':recall,'precision':precision,
        'tp':tp,'tn':tn,'fp':fp,'fn':fn}))
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
posts=['Suning Holdings Group Ltd, announced it will add 80,000 jobs in 2019, mainly in retail, modern supply chain and digital areas to support the real #economy. https://t.co/64EzYDgTYO https://t.co/ALNuXjYSew','Fu Ying, China\'s former vice-foreign minister, also the first woman appointed to the role of spokeswoman for China\'s top legislature, has published a book recalling her years on her career. https://t.co/Ujclrc1i17 https://t.co/JhP2CpZP69','Chinese universities dominate this year\'s rankings of emerging economies universities, according to data. #education https://t.co/dbrGMxIJnX https://t.co/HTngFCxWel','China\'s licensing freeze lasted nine months till December, which makes China\'s mobile #game market suffering from its slowest revenue growth in a decade. https://t.co/DtIdLdq46n #esports https://t.co/mNbqhCRLlW','Shanghai scientists have discovered that the volume of putamen, a subcortical brain area, in adolescents as an indicator of a higher possibility in the development of schizophrenia after adulthood. https://t.co/65HhBUkJRQ #science https://t.co/lEAjFuePWT']
predict_list=predict(posts,model,word_vec)
print(predict_list)
