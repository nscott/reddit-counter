from redditcounter import RedditCounter
from datetime import datetime

counter = RedditCounter('unixporn', earliest_date_to_get = datetime(2015, 1, 1), max_posts = None)

counter.run()
