'''
Ideas for how the tracker will work:

tracker start Trying to implement !lenses in !python
    Adds entry with start time of current time and tags !lenses, !python
tracker stop
    Adds stop time to last entry

tracker start Adding reporting feature to habit tracker !!python
    Adds entry with start time of current time and tag !python
    !!python not included in entry text
tracker start Adding traversal to !python !lenses
    Adds current time as stop of last entry
    Adds entry with start time of current time and tags !lenses, !python

tracker done Reviewed 10 !kanji
    Adds entry with start and stop time now and tag !kanji

tracker add yesterday at 3pm to 6pm: implementing !lenses as co algebras
    Adds entry with start time yesterday at 3pm and end time yesterday at 6pm
tracker add tuesday at 11am for 2 hours: playing ping pong !!exersise
    Adds entry with start time last tuesday at 11am and end time last tuesday at 1pm
tracker add Feb 3rd: Brother !birthday
    Adds entry with start and stop time of Feb 3rd of the current year

tracker theme FP: !lenses
    Creates a theme called FP for tracking the tags !lenses, !FP
    Creates a tag !FP that can be added to entries
tracker theme Programming: !FP !python
    Creates a theme called Programming for tracking tags !FP, !lenses, !Programming 

tracker habbit add Daily Programming "Spend 2 hours outside of work programming": !Programming --time 3hr
    Creates a habbit called "Daily Programming" with the description "Spend 3
    hours outside of work programming" with a daily goal of 3 hours of entries with
    the tag Programming or any sub tag.
tracker habbit all
    Outputs a list of all habbits, numbers of successful days, total time
    Example output:
    Daily Programming: 5 days, 17hr
tracker habbit today
    Outputs habbits yet to complete today
    Example output:
    Daily Programming: 1hr/3hr
'''

import datetime
import os
import json
import re

class Utils:
    @staticmethod
    def load_file_to_entry(file_name):
        if os.path.exists(file_name):
            with open(file_name) as file:
                return Entry(**dict(json.load(file)))

    @staticmethod
    def write_entry_to_file(file_name, entry, mode = 'w'):
        with open(file_name, mode) as file:
            file.write(json.dumps(dict(entry), default=str)+'\n')

    @staticmethod
    def load_tags(tags_file):
        if os.path.exists(tags_file):
            with open(tags_file) as file:
                return (json.load(file))
        return ()

    @staticmethod
    def write_tags(tags_file, tags):
        with open(tags_file, 'w') as file:
            file.write(json.dumps(list(tags), default=str)+'\n')

    @staticmethod
    def parse_tags(text):
        tags = re.findall(r'!(\w+)', text)
        new_text = re.sub(r'!!\w+', '', text)
        return new_text, tags

class Entry:
    def __init__(self, text, start_time, stop_time = None, tags = ()):
        self._text = text
        self._start_time = start_time
        self._stop_time = stop_time
        if tags == ():
            new_text, tags = Utils.parse_tags(text)
            self._text = new_text.strip()
        self._tags = tags

    def __iter__(self):
        for k, v in self.__dict__.items():
            yield (k.strip('_'), v)


class Tracker:
    def __init__(self, dir_):
        self._dir = dir_
        self._entries_file = os.path.join(dir_, 'entries')
        self._current_file = os.path.join(dir_, 'current')
        self._tags_file = os.path.join(dir_, 'tags')

    @property
    def current(self):
        current = Utils.load_file_to_entry(self._current_file)
        return current

    def _new(self, text):
        entry = Entry(text, datetime.datetime.now())
        tags = set(Utils.load_tags(self._tags_file))
        tags = tags.union(entry._tags)
        Utils.write_tags(self._tags_file, tags)
        Utils.write_entry_to_file(self._current_file, entry)

    def stop(self, entry):
        entry._stop_time = datetime.datetime.now()
        Utils.write_entry_to_file(self._entries_file, entry, 'a')

    def start(self, text):
        if self.current != {}:
            self.stop(self.current)
        self._new(text)
