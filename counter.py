import praw
import json
from Queue import Queue
from datetime import datetime
import time
from pprint import pprint

class CounterProgressSaver:
    """Serializes whatever is on its queue as JSON and writes to a file on regular intervals"""
    def __init__(self):
        self.queue = Queue(maxsize=10000)

    def write_out(self, file_name):
        # 'a' is append mode
        with open(file_name, 'a') as f:
            # dequeue until empty
            while not self.queue.empty():
                queue_item = self.queue.get_nowait()
                f.write(json.dumps(queue_item))
                f.write(',\n')

    def add_record(self, item):
        self.queue.put_nowait(item)

class CounterTracker:
    def __init__(self):
        self.time_stream = {}
        self.tag_aggregates = {}
        # Time aggregates is intended to be a heirarchy of dicts
        # Keys are the time, e.g. year, month, day
        # Values are the smaller unit
        # Year => Months, Month => Days, Day => Tags, Tag => Counts
        self.time_aggregates = {}

    def _add_to_time_aggregate(self, tag, timestamp):
        # break down for time agg is year/month/day
        dt = datetime.fromtimestamp(timestamp)
        if dt.year not in self.time_aggregates:
            self.time_aggregates[dt.year] = {}
        if dt.month not in self.time_aggregates[dt.year]:
            self.time_aggregates[dt.year][dt.month] = {}
        if dt.day not in self.time_aggregates[dt.year][dt.month]:
            self.time_aggregates[dt.year][dt.month][dt.day] = {}
        if tag not in self.time_aggregates[dt.year][dt.month][dt.day]:
            self.time_aggregates[dt.year][dt.month][dt.day][tag] = 1
        else:
            self.time_aggregates[dt.year][dt.month][dt.day][tag] += 1

    def _add_to_tag_aggregates(self, tag):
        if tag not in self.tag_aggregates:
            self.tag_aggregates[tag] = 1
        else:
            self.tag_aggregates[tag] += 1

    def _add_to_time_stream(self, tag, timestamp):
        if timestamp not in self.time_stream:
            self.time_stream[timestamp] = {}

        if tag not in self.time_stream[timestamp]:
            self.time_stream[timestamp][tag] = 1
        else:
            self.time_stream[timestamp][tag] += 1

    def add(self, tag, timestamp):
        self._add_to_time_aggregate(tag, timestamp)
        self._add_to_tag_aggregates(tag)
        self._add_to_time_stream(tag, timestamp)

class CounterUtil:
    NO_TAG = "NO TAG FOUND"
    USER_AGENT = "Linux:RedditCounter:v0.1 (by /u/thenameunforgettable)"
    MAX_POSTS_PER_API_REQUEST = 100
    LINK_PREFIX = "t3_"

    @staticmethod
    def extract_tag(submission):
        title = submission.title()
        if title is not None and "[" in title and "]" in title:
            return title[(title.index('[')+1):title.index(']')].lower()
        return CounterUtil.NO_TAG

class Counter:
    def __init__(self, subreddit, earliest_date_to_get = None, max_posts = 100, user_agent = CounterUtil.USER_AGENT):
        self.reddit_client = praw.Reddit(user_agent=user_agent)
        self.subreddit = subreddit
        if earliest_date_to_get is None:
            self.earliest_date_to_get = datetime(1985, 0, 0)
        else:
            self.earliest_date_to_get = earliest_date_to_get

        if max_posts is None or max_posts < 0:
            self.max_posts = float('inf')
        else:
            self.max_posts = max_posts
        self.posts_retrieved = 0
        self.last_submission_retrieved = None

        self.min_sleep_secs = 2.01
        self.tracker = CounterTracker()
        self.saver = CounterProgressSaver()

    def process_submission(self, submission):
        sub_tag = CounterUtil.extract_tag(submission.title)
        self.tracker.add(sub_tag, submission.created_utc)
        self.saver.add_record({submission.created_utc: sub_tag})

    def get_submissions(self, after_submission = None):
        params = {}
        if after_submission is not None:
            params = {'after': CounterUtil.LINK_PREFIX + after_submission.id}
        submissions = list(self.reddit_client.get_subreddit(self.subreddit).get_new(limit=CounterUtil.MAX_POSTS_PER_API_REQUEST, after_field='id', params = params))
        return submissions

    def print_progress(self):
        print 'Retrieved ' + str(self.posts_retrieved) + ' submissions so far'
        print 'Earliest date and time retrieved so far: ' + str(datetime.fromtimestamp(self.last_submission_retrieved.created_utc))

    def _should_keep_running(self):
        return (self.posts_retrieved < self.max_posts) and (self.last_submission_retrieved is None or datetime.fromtimestamp(self.last_post_retrieved.created_utc) > self.earliest_date_to_get)

    def run(self):
        submissions = self.get_submissions()
        while (submissions is not None) and self._should_keep_running():
            for submission in submissions:
                self.process_submission(submission)
                self.last_post_retrieved = submission
                self.last_submission_retrieved = submission
                self.posts_retrieved += 1
            self.print_progress()
            self.saver.write_out('progress.json')
            time.sleep(self.min_sleep_secs)
            submissions = self.get_submissions(self.last_submission_retrieved)


counter = Counter('unixporn', earliest_date_to_get = datetime(2015, 1, 1), max_posts = None)
counter.run()

