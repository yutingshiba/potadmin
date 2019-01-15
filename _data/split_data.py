

fnames = ['EI_all.csv', 'NS_all.csv', 'TF_all.csv', 'JP_all.csv']

train_limit = int(422845 * 0.7)
valid_limit = int(422845 * 0.85)

for fname in fnames:
    count = 0
    prefix = fname[:2]
    train_out = open('{}_train.csv'.format(prefix), 'w')
    valid_out = open('{}_valid.csv'.format(prefix), 'w')
    test_out = open('{}_test.csv'.format(prefix), 'w')
    with open(fname, 'r') as fp:
        for line in fp:
            if count < train_limit:
                train_out.write(line)
            elif count < valid_limit:
                valid_out.write(line)
            else:
                test_out.write(line)
            count += 1
            
