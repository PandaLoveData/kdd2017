# -*- coding: utf-8 -*-
#!/usr/bin/env python

'''
Predict the avg travel time for testing data
'''

import os
from datetime import datetime, timedelta
from aggregate_travel_time import avgTravelTime
from utils import *

file_suffix = '.csv'
out_path = '../results/'
dataDir = 'dataSets/'

hist_att_list = {}  # history average travel time of routes in window
hist_att = {}

def history_avg_travel_time(in_file, contextDir):
    print 'Pre-training: avg travel time of past data...'
    history_out_file_name = avgTravelTime(dataDir+contextDir+in_file)

    print 'Training...'
    fr = open(history_out_file_name, 'r')
    fr.readline()  # skip the header
    history_data = fr.readlines()
    fr.close()

    max_win_index = 0
    for i in xrange(len(history_data)):
        line = history_data[i].replace('"', '').split(',')
        intersection_id = line[0]
        tollgate_id = line[1]

        route_id = intersection_id + '-' + tollgate_id
        if route_id not in hist_att_list.keys():
            hist_att_list[route_id] = {}
        
        trace_start_time = line[2]
        trace_start_time = datetime.strptime(trace_start_time, "%Y-%m-%d %H:%M:%S")

        time_window_index = time_to_index(trace_start_time)
        max_win_index = max(time_window_index, max_win_index)
        if time_window_index not in hist_att_list[route_id].keys():
            hist_att_list[route_id][time_window_index] = []
        
        tt = float(line[-1]) # history average travel time
        hist_att_list[route_id][time_window_index].append(tt)
    print max_win_index # just check correctness

    out_file_name = out_path + 'history_att_win' + file_suffix
    fw = open(out_file_name, 'w')
    outline = ','.join(["intersection_id","tollgate_id","time_window","avg_travel_time"]) + '\n'
    fw.writelines(outline)
    for i in range(len(hist_att_list.keys())):
        route_id = hist_att_list.keys()[i]
        for j in range(len(hist_att_list[route_id].keys())):
            [intersection_id, tollgate_id] = route_id.split('-')
            avg_att = str(round
                (sum(hist_att_list[route_id][j])/len(hist_att_list[route_id][j]),
                2))
            outline = ','.join([intersection_id, tollgate_id, 
            index_to_time(j).strftime("%Y-%m-%d %H:%M:%S"), avg_att]) + '\n'
            fw.writelines(outline)
    fw.close()
    return out_file_name


def load_hist_avg_travel_time(hist_file_name):
    global hist_att
    hist_att.clear()
    fr = open(hist_file_name, 'r')
    fr.readline() # skip header

    hist_lines = fr.readlines()
    for i in range(len(hist_lines)):
        line = hist_lines[i].split(',')
        intersection_id = line[0]
        tollgate_id = line[1]
        route_id = intersection_id + '-' + tollgate_id
        if route_id not in hist_att:
            hist_att[route_id] = {}
        
        att = float(line[3])

        start_time = datetime.strptime(line[2], '%Y-%m-%d %H:%M:%S')
        time_index = time_to_index(start_time)
        if time_index not in hist_att[route_id]:
            hist_att[route_id][time_index] = 0.0
        hist_att[route_id][time_index] = att

    return hist_att


def pre_processing_testing_data(test_file_name, contextDir):
    test_file_name = dataDir + contextDir + test_file_name
    print '\tpre_processing testing data in', test_file_name
    out_file_name = avgTravelTime(test_file_name)
    print 'Done pre-processing testing data!\n'
    return out_file_name


pred_day = {}
pred_idx = []

pred_start_idx = time_to_index(datetime(year=2017, month=10, day=1, hour=8,minute=0))
pred_end_idx = time_to_index(datetime(year=2017, month=10, day=1, hour=10, minute=0))
pred_idx.extend(range(pred_start_idx, pred_end_idx))

pred_start_idx = time_to_index(datetime(year=2017, month=10, day=1, hour=17, minute=0))
pred_end_idx = time_to_index(datetime(year=2017, month=10, day=1, hour=19, minute=0))
pred_idx.extend(range(pred_start_idx, pred_end_idx))

pred_year = 2016
pred_month = 10

def att_read_testing_data(test_file_name, contextDir):
    test_out_file_name = pre_processing_testing_data(test_file_name, contextDir)
    print test_out_file_name
    fr = open(test_out_file_name, 'r')
    print fr.readline()  # skip the header
    window_data = fr.readlines()
    fr.close()
    for i in xrange(len(window_data)):
        line = window_data[i].replace('"', '').split(',')
        intersection_id = line[0]
        tollgate_id = line[1]
        window_start_time = line[2]
        window_start_time = datetime.strptime(window_start_time, "%Y-%m-%d %H:%M:%S")
        
        assert (pred_month == window_start_time.month)
            
        day = window_start_time.day
        if day not in pred_day:
            pred_day[day] = {}
        att = float(line[3])
        route_id = intersection_id + '-' + tollgate_id
        if route_id not in pred_day[day]:
            pred_day[day][route_id] = []
    
    pred_out_file_name = out_path + 'pred_avg_travel_time' + '_' +contextDir.split('_')[-1].replace('/', '') + file_suffix
    fw = open(pred_out_file_name, 'w')
    fw.writelines(','.join(['"intersection_id"', '"tollgate_id"', '"time_window"', '"avg_travel_time"']) + '\n')
    for day in sorted(pred_day.keys()):
        print day
        for route_id in sorted(pred_day[day].keys()):
            # print route_id
            [intersection_id, tollgate_id] = route_id.split('-')
            for index in pred_idx:
                time = index_to_time(index)
                time = datetime(year=pred_year, month=pred_month, 
                    day=day, hour=time.hour, minute=time.minute)
                end_time = time + timedelta(minutes=20)
                
                 # history average value
                pred_att = round(sum(hist_att_list[route_id][index]) / len(hist_att_list[route_id][index]), 2)
                
                outline = ','.join([intersection_id, tollgate_id, 
                    '"[' + str(time) + ',' + str(end_time) + ')"', str(pred_att) ]) + '\n'

                fw.writelines(outline)
    fw.close()


def pred_att(pred_time_idx):
    for idx in pred_time_idx:
        print idx, index_to_time(idx).strftime("%H:%M")


def main():
    hist_avg_file_name = history_avg_travel_time('trajectories(table 5)_training', contextDir='training/')
    hist_avg_tt = load_hist_avg_travel_time(hist_avg_file_name)
    att_read_testing_data('trajectories(table 5)_test1', contextDir='testing_phase1/')
    # pred_att(pred_idx)


if __name__ == '__main__':
    main()
