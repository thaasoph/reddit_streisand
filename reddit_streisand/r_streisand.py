import pprint
import praw
import os
from datetime import date


scrapes_path = "scrapes/"



def process_submission(submission):
    if not os.path.exists(scrapes_path+submission.id):
        os.mkdir(scrapes_path+submission.id)


def main():
    if not os.path.exists(scrapes_path):
        os.mkdir(scrapes_path)

    reddit = praw.Reddit("streisand")
    for submission in reddit.subreddit("learnpython").new(limit=10):
        process_submission(submission)
    
if __name__ == "__main__":
    main()
