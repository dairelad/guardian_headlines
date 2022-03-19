# Python script when given a keyword, start date and number of pages;
# will scrape the Guardian news' headlines and perform sentimental analysis
# on the results to establish their polarity and subjectivity
# sentiment is a view or opinion held by a body, in this case the Guardian

import urllib
import requests
import json
import time
import settings
import pprint
import argparse
import pandas as pd
from textblob import TextBlob
import dateparser
from pandas.plotting import register_matplotlib_converters
import datetime

import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import matplotlib.dates as mdates

register_matplotlib_converters()

# code used to add a help flag when running the script (-h)
# also prints the required arguments to run when they are not provided correctly
parser = argparse.ArgumentParser(description='Scrape Guardian articles')
parser.add_argument('keyword', type=str, help='Keyword in Guardian articles')
parser.add_argument('from_date', type=str, help='"From" date for articles in format YYYY-MM-DD')
parser.add_argument('pages', type=int, help='Number of search result pages to return.')

# textblob class used to analyse text for sentiment
def sentiment_analysis(text):
    analysis = TextBlob(text)
    # polarity of a text indicates whether it is positive, negative or neutral
    # subjectivity is how much a text is based on a persons opinions vs objectiveness which is the quality of being unbiased
    return analysis.polarity, analysis.subjectivity

def scrape_articles(args):
    # create pandas df with relevant columns
    article_db = pd.DataFrame(columns=['article_title', 'article_section', 'article_date', 'article_url', 'title_sentiment', 'title_subjectivity'])

    for page in range(1, args.pages+1):
        url = 'https://content.guardianapis.com/search?&q={}&api-key={}&from-date={}&page-size=10&page={}&order-by=relevance'.format(args.keyword, settings.API_KEY, args.from_date, page)
        print('scraping page ', page)
        articles = []
        with urllib.request.urlopen(url) as url:
            data = json.loads(url.read().decode())
            results = data['response']['results']
            for article in results:
                date = article['apiUrl'].split('/')
                article_info = {
                'article_title' : article['webTitle'],
                'article_section' : article['sectionName'],
                'article_date' : dateparser.parse('{} {} {}'.format(date[4], date[5], date[6])),
                'article_url' : article['webUrl'],
                'title_sentiment' : sentiment_analysis(article['webTitle'])[0],
                'title_subjectivity' : sentiment_analysis(article['webTitle'])[1]
                }
                articles.append(article_info)
                print(article['webTitle'])
                article_db.loc[len(article_db)] = article_info
    return article_db

if __name__ == '__main__':
    args = parser.parse_args() # checks that the correct arguments have been provided to run the program
    df = scrape_articles(args) # scrapes the guardian website for the relevant articles
    print(df)

# TODO edit this code to provide more information surrounding the sentiment relating to the keyword
    print(str(df['title_sentiment'].mean()) + ' average sentiment.')
    df.to_csv('Guardian_{}_sentiment_{}.csv'.format(args.keyword, datetime.datetime.now())) # writes results to csv

    '''
    Sentiment analysis is a natural language processing technique used to determine whether
    speech is positive, negative or neutral. Sentiment analysis focuses on the polarity of a text
    (positive, negative, neutral) but it also goes beyond polarity to detect specific feelings and emotions
    (angry, happy, sad etc.), urgency (urgent, not urgent) and even intentions (interested v. not interested)

    '''
