from datetime import datetime
import praw
import time

from progresssaver import ProgressSaver
from tracker import CounterTracker
from counterutil import CounterUtil

class RedditCounter:
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
        self.saver = ProgressSaver()

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
        while (submissions is not None) and len(submissions) > 0 and self._should_keep_running():
            for submission in submissions:
                self.process_submission(submission)
                self.last_post_retrieved = submission
                self.last_submission_retrieved = submission
                self.posts_retrieved += 1
            self.print_progress()
            self.saver.write_out('progress.json')
            time.sleep(self.min_sleep_secs)
            submissions = self.get_submissions(self.last_submission_retrieved)
        print('Submissions result length: ' + str(len(submissions)) + ', Should keep running? ' + str(self._should_keep_running()))
        self.tracker.print_top_tags()



