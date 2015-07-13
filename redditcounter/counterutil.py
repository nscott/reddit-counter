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
