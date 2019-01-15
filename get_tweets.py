import tweepy
import json
import re
from tkinter import *
import tkinter.messagebox as messagebox


class TweetAPI(object):
    def __init__(self):
        self.consumer_key = "HV2zZ7gZzrfWIrxEHVQW6uNA1"
        self.consumer_secret = "lqdx8ygDIMQXbpwiNauO6EpvbLXe5MEoXrHbpMmgISlKEVHVrJ"
        self.access_token = "997301214344859648-XKTBtvxnxvC1ToHlzMXvf7wJ2SOIT4F"
        self.access_token_secret = "eHI6E4nmQGKWd5YnE1QwDXNNgrQgPDZ2TNF8BUdtoBFEJ"
        self.auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        self.auth.set_access_token(self.access_token, self.access_token_secret)
        self.api = tweepy.API(self.auth, proxy='127.0.0.1:1087')

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
        post += ' '
        post = re.sub('https?://[a-zA-Z0-9.?/&=:]*', '', post)
        post = re.sub('#.*?[ \s\n]', '', post)
        post = re.sub('@.*?[ \s\n]', '', post)
        post = re.sub('\d+', '', post)
        post = re.sub('\n', '', post)
        post = post.encode('ascii', errors='ignore').decode('ascii').split(' ')
        post = [word for word in post if len(word) > 2]
        return post  # Return post as a list

    def get_user_timeline(self, screen_name, count=100):
        try:
            if screen_name == '':
                raise (IOError)
            new_tweets = self.api.user_timeline(screen_name, count=count, tweet_mode="extended")
            post = ''
            with open(screen_name, "w") as userfile:
                for tweet in new_tweets:
                    userfile.write('0\t')
                    post = tweet.full_text
                    post = self.filter_post(post)
                    userfile.write(json.dumps(post))
                    userfile.write('\n')
            messagebox.showinfo('Message', 'Successfully retrive user {}\'s timeline.'.format(
                screen_name))
            return post
        except tweepy.error.TweepError:
            messagebox.showinfo('Message',
                                'Error: failed to retrive user {}\'s timeline. Please check the username'.format(
                                    screen_name))
        except IOError:
            messagebox.showinfo('Message', 'User name cannot be blank.')


class Application(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.grid(row=0, column=0)
        self.tweetapi = TweetAPI()
        self.createWidgets()
        self.user_timeline_return_value = -1

    def createWidgets(self):
        self.L1 = Label(self, text="Username:").grid(row=1, column=0)
        self.nameInput = Entry(self)
        self.nameInput.grid(row=1, column=1)

        self.L2 = Label(self, text="Num posts:",).grid(row=2, column=0)
        self.numPostInput = Entry(self)
        self.numPostInput.grid(row=2, column=1)
        self.numPostInput.insert(END, '10')

        self.alertButton = Button(self, text='Retrive posts',
                                  command=lambda: self.tweetapi.get_user_timeline(self.nameInput.get(), count=int(self.numPostInput.get())))
        self.alertButton.grid(row=3, column=1)

app = Application()
app.master.title('Get Tweet Post')  # Set title for the main window
app.mainloop()

# tweetapi = TweetAPI()
# tweetapi.get_user_timeline('Eminemaaaaaaaa123', count=10)
