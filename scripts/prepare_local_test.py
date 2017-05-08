# -*- coding: utf-8 -*-
#!/usr/bin/env python

'''
use sed to do this may be better
sed -i '' '/2016-10-0/n' filename
'''

import os
from datetime import datetime, time, timedelta, date

data_dir = '../dataSets'
test_dir = 'test_local'
train_dir = 'training_local'
file_suffix = '.csv'

train_files = [
    'links (table 3).csv', 
    'routes (table 4).csv', 
    'trajectories(table 5)_training.csv', 
    'volume(table 6)_training.csv', 
    'weather (table 7)_training.csv']

for filename in train_files:
    filepath = '/'.join([data_dir, train_dir, filename])
    if not os.path.exists(filepath):
        print 'Missing', filepath


def make_test_volume(in_file, contextDir):
    start_day = 11
    end_day = 18
    month = 10
    year = 2016
    start_date = date(year=year, month=month, day=start_day)
    end_date = date(year=year, month=month, day=end_day)

    in_file = '/'.join([data_dir, contextDir, in_file + file_suffix])
    fr = open(in_file, 'r')
    header = fr.readline()
    lines = fr.readline()
    fr.close()

