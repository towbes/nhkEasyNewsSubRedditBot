# nhkEasyNewsSubRedditBot
A python script to post NHK Easy News posts to r/NHKEasyNews

Credit to https://github.com/TianyiShi2001/nhk-easy for the code that parses the article content from NHK Easy news article page

## Setup Steps (Linux)
1. `python3 -m venv myenv`
2. `source myenv/bin/activate`
3. Run `pip install requests; pip install lxml; pip install praw`
4. Create a file 'praw.ini' and configure your reddit account information
```
[DEFAULT]
client_id=YOUR_CLIENT_ID
client_secret=YOUR_CLIENT_SECRET
password=YOUR_REDDIT_PASSWORD
username=YOUR_REDDIT_USERNAME
user_agent=YOUR_USER_AGENT
```
5. Update the subreddit name variable:
```
subreddit_name = 'nhkEasyNewsTesting'
```
6. If needed, update the lookback days variable. It's set to 10 by default
```
#Number of days to look back
lookbackDays = 10
```
6. run `python __main__.py`