import operator
from datetime import datetime

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

    def print_top_tags(self, num = 20):
        sorted_tags = sorted(self.tag_aggregates.items(), key = operator.itemgetter(1))
        sorted_tags = sorted_tags[(len(sorted_tags) - num):]
        for tag in sorted_tags:
            print str(tag[1]) + ' posts: ' + tag[0]

    def add(self, tag, timestamp):
        self._add_to_time_aggregate(tag, timestamp)
        self._add_to_tag_aggregates(tag)
        self._add_to_time_stream(tag, timestamp)
