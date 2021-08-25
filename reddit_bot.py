import praw
from praw import exceptions as prawexcept
from requests import get
from json import loads
import textwrap
import time
import os

def quote():
    try:
        response = get('http://api.forismatic.com/api/1.0/?method=getQuote&format=json&lang=en')
        return loads(response.text)['quoteAuthor'], loads(response.text)['quoteText']
    except:
        print("fricken RATE LIMITS!")
        time.sleep(5)
        failure_author, failure_message=quote()
        return failure_author, failure_message

def scrape(target_comment):
    already_supplied=False
    pattern_to_reply=""
    try:
        if pattern_to_reply in target_comment.body:
            for reply in target_comment.replies:
                if reply.author == "potty-mouth-bot":
                    already_supplied=True
                elif reply.author == "schlag-bot":
                    print("schlag-bot got to em")
                    already_supplied=True
            if already_supplied:
                return
            else:
                print(f"Haven't talked yet, delivering reply to the naughty {target_comment.author}...")
                print(f"""
                {target_comment.body}
                """)
                author, text = quote()
                generated_reply=reply_switch(target_comment)
                if generated_reply is not None:
                    target_comment.reply(generated_reply)
                    print(f"Reply delivered: {generated_reply}")
                else:
                    print(f"Matched but no command registered.")
                # time.sleep(5)
    except AttributeError:
        return

def reply_switch(target_comment):
    quote_author, quote_text = quote()
    footer = textwrap.dedent(f"""

    Here's an inspirational quote, since you seem to need it, potty mouth ;)
    > {quote_text}
    
    {quote_author}

    ---
    ^(This is a bot that has made this comment. If you think this is problematic, ban me or DM the bot with your concerns.)
    """)
    try:
        if "-quote" in target_comment.body:
            author, text = quote()
            return f"Here's a fricken quote: \n> {text}\n  - {author} {footer}"
        elif "-bully" in target_comment.body:
            return f"You're a huge piece of crap, {target_comment.author} {footer}"
        elif "!schlag" in target_comment.body:
            return f"{target_comment.author}, I literally have no idea what to do with this command. {footer}"
        elif "shit" in target_comment.body:
            return f"Hey {target_comment.author}, let's try saying shoot instead. :) Make reddit a friendlier place {footer}"
        else:
            return None
    except AttributeError:
        return

def bot_run(subreddit_target):
    try:
        sr_schlagbot = rd.subreddit(subreddit_target)
        print(f"Creeping posts on {subreddit_target}:")
        posts=sr_schlagbot.hot(limit=10)
        amount_of_posts=0
        for post in posts:
            print(f" - Now in post: {post.title}")
            post.comment_sort = "new"
            try:
                comments = list(post.comments)
                for comment in comments:
                    scrape(comment)
                    for reply in comment.replies:
                        scrape(reply)
                        for sub_reply in reply.replies:
                            scrape(sub_reply)
            except AttributeError:
                continue
            amount_of_posts+=1
        print(f"Completed all {amount_of_posts} posts in {sr_schlagbot}. Taking a rest...")
        # time.sleep(5)
        amount_of_posts=0
    except prawexcept.RedditAPIException as e:
        print("potty-mouth-bot is fricken rate limited from Reddit")
        print(e)
        txt=str(e)
        minutes_left=[int(s) for s in txt.split() if s.isdigit()]
        print(f"Sleeping for {minutes_left[0]} minutes...")
        time.sleep(minutes_left[0]*60)
        print(f"Good to fricken go... Ramping up again!")
        return

r_username = os.getenv('RUSERNAME')
r_password = os.getenv('RPASSWORD')
r_client_secret = os.getenv('RCSECRET')
r_client_id = os.getenv('RCID')
print(r_client_id)

version="v0.1"
bot_name="potty-mouth-bot"
rd = praw.Reddit(client_id=r_client_id,
                client_secret=r_client_secret,
                user_agent=f'<python>:<{bot_name}>:<{version}>',
                username=r_username,
                password=r_password)
while True:
    subreddit_list=[
        # "funny",
        "me_irl"
    ]
    for target in subreddit_list:
        bot_run(target)