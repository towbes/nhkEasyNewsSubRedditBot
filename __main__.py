import praw
import requests
from lxml import etree as le
from datetime import datetime, timedelta
import json
import time


# NHK Easy News API endpoint
nhk_api_url = 'https://www3.nhk.or.jp/news/easy/news-list.json'

#Number of days to look back
lookbackDays = 10
subreddit_name = 'NHKEasyNews'

def fetch_latest_articles():
    response = requests.get(nhk_api_url)
    if response.status_code == 200:
        data = response.json()
        articles = data[0]
        return articles
    else:
        print("Failed to fetch articles")
        return []


"""
Code for get_raw_html and get_text functions taken from https://github.com/TianyiShi2001/nhk-easy which is licensed under the MIT License
The MIT License (MIT)

Copyright (c) 2020 石天熠

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
def get_raw_html(url):
    r = requests.get(url)
    r.encoding = "UTF-8"
    return r.text

def get_text(url):

    article_body_xpath = "//div[@id='js-article-body']"
    join_text = lambda html: "".join(
        html.xpath(f"{article_body_xpath}//text()")
    ).strip()

    raw_html = get_raw_html(url)
    html = le.HTML(raw_html)
    le.strip_elements(html, "rt")
    
    #Format for reddit post. Some articles end up with double \n\n to replace, others not
    text_return = join_text(html)
    if '\n\n' in text_return:
        modified_string = text_return.replace('\n\n', '\n\n&nbsp;\n\n')
    else:
        modified_string = text_return.replace('\n', '\n\n&nbsp;\n\n')
    #print(modified_string)
    return modified_string

"""
End for code from https://github.com/TianyiShi2001/nhk-easy
"""


def main():
    
    #use praw.ini for configuration details
    reddit = praw.Reddit('DEFAULT')

    # Get today's date
    today = datetime.today()
    fetchDate = today
    fetchDateFormatted = fetchDate.strftime('%Y-%m-%d')

    #Dictionary to store Date: # of articles
    last7nhk = {}

    #First get a list of articles and titles from the last 30 days
    articleList = fetch_latest_articles()

    #print("{}".format(json.dumps(dates[formatted_date], indent=4)))
    for i in range(lookbackDays):
        try:
            # Try to access current day
            #print(f"Trying date: {fetchDateFormatted}", flush=True)
            last7nhk[fetchDateFormatted] = len(articleList[fetchDateFormatted])
            fetchDate = fetchDate - timedelta(days=1)
            fetchDateFormatted = fetchDate.strftime('%Y-%m-%d')
        except KeyError:
            # Handle the KeyError by subtracting one day from today's date
            fetchDate = fetchDate - timedelta(days=1)
            fetchDateFormatted = fetchDate.strftime('%Y-%m-%d')
            #print(f"KeyError caught. Trying next date: {fetchDateFormatted}", flush=True)
    

    for key, value in last7nhk.items():
        print(f"{key}, {value} articles")

    # Get the subreddit instance
    subreddit = reddit.subreddit(subreddit_name)

    # Get the last 30 posts from the subreddit
    posts = subreddit.new(limit=50)

    #list to store post titles
    post_titles = []
    #dictionary to store Date: # of articles
    last7reddit = {}

    # Print the titles of the posts
    for post in posts:
        #print(post.title)
        post_titles.append(post.title)

    #Variable to count down date posts
    lastArticleDate = today
    # Format the date as "YYYY-MM-DD"
    lastArticleFormattedDate = today.strftime('%Y-%m-%d')

    #loop through the last 7 days
    for i in range(lookbackDays):
        # Check if there are articles from today's date
        #print(f"Checking for articles from {lastArticleFormattedDate}")
        today_articles = []

        # Print the titles of the posts
        for title in post_titles:
            #print(title)
            if lastArticleFormattedDate in title:
                today_articles.append(title)

        if today_articles:
            #print(f"Articles from {lastArticleFormattedDate}:")
            for article in today_articles:
                print(article)
            #add to dictionary
            last7reddit[lastArticleFormattedDate] = len(today_articles)
            lastArticleDate = lastArticleDate - timedelta(days=1)
            lastArticleFormattedDate = lastArticleDate.strftime('%Y-%m-%d')
        else:
            #print(f"No articles from {lastArticleFormattedDate} found.")
            lastArticleDate = lastArticleDate - timedelta(days=1)
            lastArticleFormattedDate = lastArticleDate.strftime('%Y-%m-%d')


    for key, value in last7reddit.items():
        print(f"{key}, {value} articles")

    #Dates to add articles
    fullDateMissing = []
    partialDateMissing = []

    #Find matching keys where the length doesn't match
    for key, value in last7nhk.items():
        #If there are already articles from that day, check if there are enough
        if key in last7reddit:
            if last7nhk[key] != last7reddit[key]:
                #Article number mismatch
                partialDateMissing.append(key)
        #If there are no articles posted, we need to post them
        else:
            fullDateMissing.append(key)
        

    print(f"Need to post all articles from {len(fullDateMissing)} dates")
    print(f"Need to post some articles from {len(partialDateMissing)} dates")

    #flip the date lists so that we add in reverse order
    fullDateMissing.reverse()
    partialDateMissing.reverse()

    #For each of the dates in the fullDateMissing, post an article
    for date in fullDateMissing:
        for article in articleList[date]:
        
            title = article['title']
            link = link = f"https://www3.nhk.or.jp/news/easy/{article['news_id']}/{article['news_id']}.html"
            content = get_text(link)
            
            # Format the Reddit post
            post_title = f"[{date}] {title}"
            post_text = f"[{link}]({link})\n\n&nbsp;\n\n{content}"
            
            # Submit the post
            subreddit.submit(post_title, selftext=post_text)
            print(f"Posted: {post_title}", flush=True)
            #print(f"{post_text}", flush=True)
            time.sleep(3)
    
    #For the partial dates, need to compare the titles
    for date in partialDateMissing:
        for article in articleList[date]:
        
            nhkTitle = article['title']
            print(f"Checking {nhkTitle}")
            found = any(nhkTitle in item for item in post_titles)

            if not found:
                link = link = f"https://www3.nhk.or.jp/news/easy/{article['news_id']}/{article['news_id']}.html"
                content = get_text(link)
                
                # Format the Reddit post
                post_title = f"[{date}] {nhkTitle}"
                post_text = f"[{link}]({link})\n\n&nbsp;\n\n{content}"
                
                # Submit the post
                subreddit.submit(post_title, selftext=post_text)
                print(f"Posted: {post_title}", flush=True)
                #print(f"{content}", flush=True)
            elif found:
                print(f"{nhkTitle} already exists")
            else:
                print("Something went horribly wrong")

            time.sleep(3)

    
    print("Completed Posting")


if __name__ == "__main__":
    main()