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
'''

import os
import json
import re

class Utils:
    @staticmethod
    def load_file(file_name):
        if os.path.exists(file_name):
            with open(file_name) as file:
                return dict(json.load(file))
    
    @staticmethod
    def write_file(file_name, content):
        with open(file_name, 'w') as file:
            file.write(content)
    
    @staticmethod
    def parse_tags(text):
        tags = re.findall(r'!\w+', text)
        new_text = re.sub(r'!!\w+', '', text)
        return new_text, tags

class Tracker:
    def __init__(self, dir_):
        self._dir = dir_
        self._entries_file = os.path.join(dir_, 'entries')
        self._current_file = os.path.join(dir_, 'current')
        self._tags_file = os.path.join(dir_, 'tags')
    
    @property
    def current(self):
        current = Utils.load_file(self._current_file)
        return current
    
    def _new(self, entry):
        Utils.write_file(self._current_file, entry)
    
    def start(self, entry):
        if self.current != {}:
            # TODO: stop current
            pass
        self._new(entry)
