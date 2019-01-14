import tensorflow as tf
import numpy as np


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


def filter_posts(posts_str):
    posts = posts_str.aplit('|||')
    # filter out invalid posts
    posts_list = []
    for post in posts:
        # replace url
        _post = re.sub('https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)', post)
        if not _post:
            continue


def load_train_data(file_name='train_data.csv'):
    label_list = []
    post_list = []
    with open(file_name) as fp:
        for line in fp:
            # load raw input data line by line
            tokens = line.rstrip('\n').split(',')
            label = 1 if tokens[0][0] == 'E' else 0
            posts = filter_posts(tokens[1])
            for post in posts:
                # treat each post regardless of author
                label_list.append(label)
                post_list.append(post)

    return label_list, post_list


def main():
    l_list, p_list = load_train_data('train_small.csv')
    for i in range(0, 100, 10):
        print(l_list[i])
        print(p_list[i])

if __name__ == '__main__':
    main()
