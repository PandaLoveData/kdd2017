# -*- coding: utf-8 -*-
#!/usr/bin/env python

'''

'''

import os

data_dir = '../dataSets'
test_dir = 'test_local'
train_dir = 'training_local'

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

