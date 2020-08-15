
import logging
import click
import os
import praw
import sys
from  subreddit_scraper import SubredditScraper

logger = logging.getLogger(__name__)
    
@click.command()
@click.option('--log', '-l', type=click.Choice(['DEBUG', 'INFO', 'WARN', 'ERROR']), default='WARN')
@click.option('--output', '-o', type=click.Path())
@click.option('--subreddit', '-r', multiple=True)
def main(log, output, subreddit):
    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s] - [%(levelname)s] - [%(funcName)s] - %(message)s'
    )
    
    if log:
        logger.setLevel(log)
    logger.info("starting reddit_streisand")

    if not os.path.exists(output):
        os.mkdir(output)

    reddit = praw.Reddit("streisand")
    scrapers = []
    for sub in subreddit:
        scrapers.append(SubredditScraper(reddit.subreddit(sub),output,batch_size=20))

    for scraper in scrapers:
        scraper.scrape()


if __name__ == "__main__":
    sys.exit(main())