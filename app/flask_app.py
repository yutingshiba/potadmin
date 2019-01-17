from flask import Flask
from flask import render_template
from flask import request
from flask import request, session, make_response, jsonify

import tweepy
import json
import re
import string
from nltk.corpus import stopwords

import tensorflow as tf
import middle

class TweetAPI(object):
    def __init__(self):
        self.consumer_key = "HV2zZ7gZzrfWIrxEHVQW6uNA1"
        self.consumer_secret = "lqdx8ygDIMQXbpwiNauO6EpvbLXe5MEoXrHbpMmgISlKEVHVrJ"
        self.access_token = "997301214344859648-XKTBtvxnxvC1ToHlzMXvf7wJ2SOIT4F"
        self.access_token_secret = "eHI6E4nmQGKWd5YnE1QwDXNNgrQgPDZ2TNF8BUdtoBFEJ"
        self.auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        self.auth.set_access_token(self.access_token, self.access_token_secret)
        self.api = tweepy.API(self.auth)

    '''
    These chars/strings will be filtered out:
    -  http://... or https://...
    -  #...
    -  @...
    -  numbers
    -  line break
    -  non-ascii symbols
    -  words with length <=2
    '''

    def filter_post(self, post):
        post = post.lower()
        # post.translate(None, string.punctuation)
        post += ' '
        post = re.sub('https?://[a-zA-Z0-9.?/&=:]*', '', post)
        post = re.sub('#.*?[ \s\n]', '', post)
        post = re.sub('@.*?[ \s\n]', '', post)
        post = re.sub('\d+', '', post)
        post = re.sub('\n', '', post)
        punc_table = set(string.punctuation)
        post = post.encode('ascii', errors='ignore').decode('ascii')

        # tweet = "I am tired! I like fruit...and milk"
        translator = str.maketrans(string.punctuation, ' ' * len(string.punctuation))  # map punctuation to space
        post = post.translate(translator)
        post = post.split(' ')

        post = [word for word in post if len(word) > 2]

        # Remove stopwords
        stop_words = stopwords.words('english')
        post = [w for w in post if w and w not in stop_words]
        post = ' '.join(post)

        return post  # Return post as a list

    def get_user_timeline(self, screen_name, count=1):
        try:
            if screen_name == '':
                raise (IOError)
            new_tweets = self.api.user_timeline(screen_name, count=count, tweet_mode="extended")
            rtn = []
            raw_posts = []
            with open(screen_name, "w") as userfile:
                post_num = 1
                for tweet in new_tweets:
                    post = tweet.full_text
                    raw_posts.append(post)
                    print('Post[{}]'.format(post_num), post, '\n')
                    post = self.filter_post(post)
                    if post:
                        rtn.append(post)
                        userfile.write('0\t')
                        userfile.write(json.dumps(post))
                        userfile.write('\n')
                    post_num += 1
            return rtn, raw_posts
        except tweepy.error.TweepError:
            print('Error: failed to retrive user {}\'s timeline. Please check the username'.format(
                screen_name))
            return None, None
        except IOError:
            print('Message', 'User name cannot be blank.')
            return None, None


def convert_rawpost_to_html(username, rawposts):
    html = '<div><h1 class="h3 mb-3 font-weight-normal">' + username + '\'s posts</h1></div>'
    for single_post in rawposts:
        html += '<div style="max-width: 800px; text-align: left"><div class="alert alert-info">' + single_post + '</div></div>'
    return html

def convert_mbti_to_html():
    pass

tweetapi = TweetAPI()
print('loading model...')
global model
model, word_vec = middle.load_model()
global graph
graph = tf.get_default_graph()

app = Flask(__name__)
# app.debug = True


@app.route('/', methods=['POST', 'GET'])
def index():
    jsonrtn = [False, 0.5, 0.5, 0.5, 0.5]
    posts_to_display = ''
    if request.method == 'POST':
        # print(request.form['user'])
        # print(request.form['numpost'])

        twitter_account = str(request.form['user'])
        num_posts = int(request.form['numpost'])
        posts, raw_posts = tweetapi.get_user_timeline(twitter_account, count=num_posts)
        if posts:
            posts_to_display = convert_rawpost_to_html(twitter_account, raw_posts)
            print('===check post===' ,posts, num_posts)
            jsonrtn[0] = True
            # response = make_response(render_template('index.html', posts_to_display=posts_to_display), 200)
            # # response = make_response('hello', 200)
            # response.headers['key'] = 'value'
            # response.headers['mbti'] = 'ENIJ'
            # return response
            # return jsonify({'status': 'ok', 'data':[{'content': render_template('index.html', posts_to_display=posts_to_display)}]})
            jsonrtn[1:5] = [.1, .2, .3, .4]
            print(len(word_vec))
            print('postshape {}'.format(len(posts)))
            with graph.as_default():
              predict_list = middle.predict(posts, model, word_vec)
            print(predict_list)
#            predict_list = predict_list.tolist()
            predict_list = [float(i) for i in predict_list]
            print(type(predict_list[0]))
            jsonrtn[1:5] = predict_list

           # jsonrtn = str(jsonrtn)
            return render_template('index.html', posts_to_display=posts_to_display, jsonrtn=json.dumps(jsonrtn))
        else:
            jsonrtn[0] = False
            posts_to_display = ''
    print('return render')
    return render_template('index.html', posts_to_display=posts_to_display, jsonrtn=json.dumps(jsonrtn))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True, use_reloader=False) # , debug=True
