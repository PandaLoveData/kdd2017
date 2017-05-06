# -*- coding: utf-8 -*-
#!/usr/bin/env python

'''
Predict the avg travel time for testing data
'''

import os
from aggregate_travel_time import avgTravelTime
from utils import *

out_path = '../results/'

def avg_travel_time():
    dataDir = 'dataSets/'
    contextDir = 'training/'
    in_file = 'trajectories(table 5)_training'
    print 'Pre-training: avg travel time of past data...'
    history_out_file_name = avgTravelTime(dataDir+contextDir+in_file)

    print 'Predicting...'
    fr = open(history_out_file_name, 'r')
    fr.readline()  # skip the header
    history_data = fr.readlines()
    fr.close()

    hist_att_win = {}  # history average travel time of routes in window
    max_win_index = 0
    for i in xrange(len(history_data)):
        line = history_data[i].replace('"', '').split(',')
        intersection_id = line[0]
        tollgate_id = line[1]

        route_id = intersection_id + '-' + tollgate_id
        if route_id not in hist_att_win.keys():
            hist_att_win[route_id] = {}
        
        trace_start_time = line[2]
        trace_start_time = datetime.strptime(trace_start_time, "%Y-%m-%d %H:%M:%S")

        time_window_index = time_to_index(trace_start_time)
        max_win_index = max(time_window_index, max_win_index)
        if time_window_index not in hist_att_win[route_id].keys():
            hist_att_win[route_id][time_window_index] = []
        
        tt = float(line[-1]) # history average travel time
        hist_att_win[route_id][time_window_index].append(tt)
    print max_win_index # just check correctness

    for i in range(1):
        route_id = hist_att_win.keys()[0]
        print 'Route', i
        for j in range(len(hist_att_win[route_id].keys())):
            print j, round(sum(hist_att_win[route_id][j]) / len(hist_att_win[route_id][j]))


def main():
    avg_travel_time()

if __name__ == '__main__':
    main()
