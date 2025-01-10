# Python script when given a keyword, start date and number of pages;
# will scrape the Guardian news' headlines and perform sentimental analysis
# on the results to establish their polarity and subjectivity
# sentiment is a view or opinion held by a body, in this case the Guardian

import urllib
import json
import settings
import argparse
import pandas as pd
from textblob import TextBlob
import dateparser
import matplotlib.pyplot as plt

# code used to add a help flag when running the script (-h)
# also prints the required arguments to run when they are not provided correctly
parser = argparse.ArgumentParser(description='Scrape Guardian articles')
parser.add_argument('keyword', type=str, help='Keyword in Guardian articles')
parser.add_argument('from_date', type=str, help='"From" date for articles in format YYYY-MM-DD')
parser.add_argument('pages', type=int, help='Number of search result pages to return.')

# textblob class used to analyse text for sentiment
# The polarity score is a float within the range [-1.0, 1.0].
# The subjectivity is a float within the range [0.0, 1.0] where 0.0 is very objective and 1.0 is very subjective.
def sentiment_analysis(text):
    analysis = TextBlob(text)
    # polarity of a text indicates whether it is positive, negative or neutral
    # subjectivity is how much a text is based on a persons opinions vs objectiveness which is the quality of being unbiased
    return analysis.polarity, analysis.subjectivity

def scrape_articles(args):
    # create pandas df with relevant columns
    article_db = pd.DataFrame(columns=['article_title', 'article_section', 'article_date', 'article_url', 'title_sentiment', 'title_subjectivity','sentiment_level','subjectivity_level'])

    for page in range(1, args.pages+1):
        url = 'https://content.guardianapis.com/search?&q={}&api-key={}&from-date={}&page-size=10&page={}&order-by=relevance'.format(args.keyword, settings.API_KEY, args.from_date, page)
        print('scraping page ', page)
        articles = []
        with urllib.request.urlopen(url) as url:
            data = json.loads(url.read().decode())
            results = data['response']['results']
            for article in results:
                date = article['apiUrl'].split('/')
                # check sentiment (Polarity)
                if sentiment_analysis(article['webTitle'])[0] < 0:
                    sent_lvl = 'Negative'
                elif  sentiment_analysis(article['webTitle'])[0] > 0:
                    sent_lvl = 'Positive'
                else:
                    sent_lvl = 'Neutral'
                #
                if sentiment_analysis(article['webTitle'])[1] < 0.5:
                    sub_lvl = 'Objective'
                elif  sentiment_analysis(article['webTitle'])[1] > 0.5:
                    sub_lvl = 'Subjective'

                article_info = {
                'article_title' : article['webTitle'],
                'article_section' : article['sectionName'],
                'article_date' : dateparser.parse('{} {} {}'.format(date[4], date[5], date[6])),
                'article_url' : article['webUrl'],
                'title_sentiment' : sentiment_analysis(article['webTitle'])[0],
                'title_subjectivity' : sentiment_analysis(article['webTitle'])[1],
                'sentiment_level' : sent_lvl,
                'subjectivity_level' : sub_lvl
                }
                articles.append(article_info)
                print(article['webTitle'])
                article_db.loc[len(article_db)] = article_info
    return article_db

def visualise_sentiment(df, args):
    neg=0; pos=0; neu=0; obj=0; sub=0
    for index, row in df.iterrows():
        if row['sentiment_level'] == 'Negative':
            neg += 1
        elif row['sentiment_level'] == 'Positive':
            pos += 1
        elif row['sentiment_level'] == 'Neutral':
            neu += 1

        if row['subjectivity_level'] == 'Objective':
            obj += 1
        elif row['subjectivity_level'] == 'Subjective':
            sub += 1

    values = [neg,pos,neu,obj,sub]
    x_axis = ['Neg','Pos','Neu','Obj','Sub']

    # plot data
    plt.bar(x_axis,values,color=['black', 'black', 'black', 'blue', 'blue'])
    plt.bar(x_axis,0)
    plt.xlabel('Measures of Sentiment')
    plt.ylabel('Count')
    plt.title(f'Sentiment surrounding the keyword ({args.keyword}) in the Guardian headlines')
    plt.legend(labels=['Sentiment', 'Subjectivity'])
    ax = plt.gca()
    leg = ax.get_legend()
    leg.legendHandles[0].set_color('black')
    leg.legendHandles[1].set_color('blue')
    plt.show()


if __name__ == '__main__':
    args = parser.parse_args() # checks that the correct arguments have been provided to run the program
    df = scrape_articles(args) # scrapes the guardian website for the relevant articles

    visualise_sentiment(df, args)
    df.to_csv('Guardian_{}_sentiment_{}.csv'.format(args.keyword, datetime.datetime.now())) # writes results to csv


    '''
    Sentiment analysis is a natural language processing technique used to determine whether
    speech is positive, negative or neutral. Sentiment analysis focuses on the polarity of a text
    (positive, negative, neutral) but it also goes beyond polarity to detect specific feelings and emotions
    (angry, happy, sad etc.), urgency (urgent, not urgent) and even intentions (interested v. not interested)

    '''
