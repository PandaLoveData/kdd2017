# -*- coding: utf-8 -*-
#!/usr/bin/env python

'''
Predict the volume for testing data
'''

import os
from datetime import datetime, timedelta
from aggregate_volume import avgVolume
from utils import *

file_suffix = '.csv'
out_path = '../results/'
dataDir = 'dataSets/'

tollgates = ['1', '1', '2', '3', '3']
directions = ['1', '0', '0', '1', '0']
toll_directions = map(lambda toll, dir: '-'.join([toll,dir]), tollgates, directions)

hist_vol = {}
test_vol = {}

pred_day = {}
pred_idx = []
pred_year = 2016
pred_month = 10

pred_start_idx = time_to_index(datetime(year=pred_year, month=pred_month, day=1, hour=8,minute=0))
pred_end_idx = time_to_index(datetime(year=pred_year, month=pred_month, day=1, hour=10, minute=0))
pred_idx_1 = range(pred_start_idx, pred_end_idx)

pred_idx.extend(pred_idx_1)

pred_start_idx = time_to_index(datetime(year=pred_year, month=pred_month, day=1, hour=17, minute=0))
pred_end_idx = time_to_index(datetime(year=pred_year, month=pred_month, day=1, hour=19, minute=0))
pred_idx_2 = range(pred_start_idx, pred_end_idx)

pred_idx.extend(pred_idx_2)

# for idx in pred_idx:
#     print idx

def history_vol(in_file, contextDir):
    print 'Pre-training...'
    in_file = dataDir + contextDir + in_file
    hist_vol_file = avgVolume(in_file) # training_20min_avg_volume.csv
    print 'Done pre-training!\n'

    print 'Reading history avg volume data from', hist_vol_file
    fr = open(hist_vol_file, 'r')
    print fr.readline() # ignore header
    filelines = fr.readlines()
    fr.close()
    print 'Done reading!\n'

    hist_win_vol = {}  # history volume of routes in window
    print 'Processing history avg volume data...'
    for toll_dir in toll_directions:
        hist_win_vol[toll_dir] = {}
    for i in range(len(filelines)):
        line = filelines[i].replace('"', '').split(',')
        # 
        tollgate_id = line[0]
        direction = line[3]
        toll_dir = '-'.join([tollgate_id, direction])

        start_time_str = line[1][1:-1]
        end_time_str   = line[2][0:-1]
        # print start_time_str, end_time_str
        start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')

        time_index = time_to_index(start_time)
        if not time_index in hist_win_vol[toll_dir]:
            hist_win_vol[toll_dir][time_index] = []
        
        volume = float(line[-1])
        hist_win_vol[toll_dir][time_index].append(volume)
    print 'Done processing!\n'

    out_file_name = out_path + 'history_avg_vol' + file_suffix
    print 'Writing to file:', out_file_name
    fw = open(out_file_name, 'w')
    outline = ','.join(['"tollgate_id"', '"start_time"', '"direction"', '"volume"']) + '\n'
    fw.writelines(outline)
    for toll_dir in sorted(hist_win_vol.keys()):
        [toll_id, direction] = toll_dir.split('-')
        toll_dir_vol = hist_win_vol[toll_dir]
        for time_index in range(0, 72):
            if not time_index in toll_dir_vol:
                toll_dir_vol[time_index] = [0.0]
            avg_volume = sum(toll_dir_vol[time_index]) / len(toll_dir_vol[time_index])
            avg_volume = str(round(avg_volume, 2))
            outline = ','.join([toll_id, str(index_to_time(time_index)), direction,
                avg_volume]) + '\n'
            fw.writelines(outline)

    fw.close()
    print 'Done writing\n'

    return out_file_name


def load_hist_vol_from(file_name):
    # history_avg_vol.csv
    print 'Load history avg volume data from file', file_name
    global hist_vol
    hist_vol = {}
    fr = open(file_name, 'r')
    print fr.readline()
    filelines = fr.readlines()
    for toll_dir in toll_directions:
        hist_vol[toll_dir] = {}
    for i in range(len(filelines)):
        line = filelines[i].split(',')
        tollgate_id = line[0]
        direction = line[2]
        toll_dir = '-'.join([tollgate_id, direction])
        volume = float(line[3])
        # remove cloase and open brackets '[' and ')'
        start_time_str = line[1]
        start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
        hist_vol[toll_dir][time_to_index(start_time)] = volume
    print 'Done loading!\n'
    return hist_vol


def vol_preprocess_testing_data(in_file, contextDir):
    print 'Preprocessing testing data...'
    # contextDir = 'testing_phase1/'
    in_file = dataDir + contextDir + in_file
    testing_vol_file = avgVolume(in_file)
    print 'Done! Output to', testing_vol_file, '\n'
    return testing_vol_file


def vol_read_testing_data(in_file, contextDir='testing_phase1'):
    # volume(table 6)_test1.csv -> test1_20min_avg_volume.csv
    testing_vol_file = vol_preprocess_testing_data(in_file, contextDir)
    
    print 'Reading testing data from', testing_vol_file
    fr = open(testing_vol_file, 'r')
    fr.readline() # skip the header
    test_data = fr.readlines()
    print test_data[0]
    print '...'
    fr.close()
    print 'Done reading testing data!\n'

    print 'Init test_vol dict...'
    global test_vol
    test_vol = {}
    print 'Done initing test_vol!\n'

    print 'Processing testing data...'
    last_day = -1
    day = -1
    for i in range(len(test_data)):
        line = test_data[i].replace('"', '').split(',')
        tollgate_id = line[0]
        direction = line[3]
        toll_dir = '-'.join([tollgate_id, direction])

        volume = float(line[4])

        start_time_str = line[1][1:]
        end_time_str = line[2][0:-1]
        start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
        
        if not start_time in test_vol:
            test_vol[start_time] = {}
        if not toll_dir in test_vol[start_time]:
            test_vol[start_time][toll_dir] = []
        
        test_vol[start_time][toll_dir].append(volume)

        day = start_time.day
        if day not in pred_day:
            pred_day[day] = {}
        # when a new day comes, predict the day before, because we 
        # cannot use later data to predict past data
        # when i == len(test_data) - 1, predict the volume of the last day 
        if ((day != last_day) and (last_day != -1)) or i == len(test_data)-1:
            # print last_day
            for idx in pred_idx:
                pred_time = index_to_time(idx)
                # get last day's time to predict
                pred_time = datetime(year=pred_year,month=pred_month, day=last_day,
                    hour=pred_time.hour,minute=pred_time.minute)
                # use previous data to help
                before_time = pred_time + timedelta(minutes=-120)
                if not before_time in test_vol.keys():
                    # should not come here
                    print 'Warning! Missing training data.'
                    assert (False)
                
                for toll_dir in toll_directions:
                    if toll_dir not in test_vol[before_time]:
                        print 'Empty volume of route in time window:', toll_dir, before_time
                        test_vol[before_time][toll_dir] = []
                    if (len(test_vol[before_time][toll_dir]) == 0):
                        print 'Empty volume for toll dir in time', str(pred_time), toll_dir
                        test_vol[before_time][toll_dir].append(0.0)
                    # get before average volume
                    test_avg_vol = sum(test_vol[before_time][toll_dir]) / len(test_vol[before_time][toll_dir])

                    pred_volume = pred_vol_by_avg(tollgate_id, direction, start_time, test_avg_vol)

                    if pred_time not in test_vol:
                        test_vol[pred_time] = {}
                        print 'Add predict time:', pred_time.strftime('%Y-%m-%d %H:%M:%S')

                    if toll_dir not in test_vol[pred_time]:
                        test_vol[pred_time][toll_dir] = 0.0
                    
                    test_vol[pred_time][toll_dir] = pred_volume
        last_day = day
    
    print 'Done processing testing data.\n'

    print 'Writing to file...'
    out_file_name = out_path + 'pred_avg_volume' + file_suffix
    fw = open(out_file_name, 'w')
    outline = ','.join(['tollgate_id','time_window','direction','volume']) + '\n'
    fw.writelines(outline)

    global pred_idx_1
    for toll_dir in sorted(toll_directions):
        [toll_id, direction] = toll_dir.split('-')
        for idx in pred_idx_1:
            pred_time = index_to_time(idx)
            for day in sorted(pred_day.keys()):
                pred_time = datetime(year=pred_year,month=pred_month,day=day,
                    hour=pred_time.hour,minute=pred_time.minute)
                end_time = pred_time + timedelta(minutes=20)
                time_window = '"[' + pred_time.strftime('%Y-%m-%d %H:%M:%S')+ \
                    ',' + end_time.strftime('%Y-%m-%d %H:%M:%S') +')"'
                if pred_time not in test_vol:
                    print idx, pred_time, 'not in test_vol'
                    for key in sorted(test_vol.keys()):
                        print key
                    return
                pred_vol = str(test_vol[pred_time][toll_dir])
                outline = ','.join([toll_id, time_window, direction, pred_vol]) + '\n'
                fw.writelines(outline)
    
    global pred_idx_2
    for toll_dir in sorted(toll_directions):
        [toll_id, direction] = toll_dir.split('-')
        for idx in pred_idx_2:
            pred_time = index_to_time(idx)
            for day in sorted(pred_day.keys()):
                pred_time = datetime(year=pred_year,month=pred_month,day=day,
                    hour=pred_time.hour,minute=pred_time.minute)
                end_time = pred_time + timedelta(minutes=20)
                time_window = '"[' + pred_time.strftime('%Y-%m-%d %H:%M:%S')+ \
                    ',' + end_time.strftime('%Y-%m-%d %H:%M:%S') +')"'
                if pred_time not in test_vol:
                    print idx, pred_time, 'not in test_vol'
                    for key in sorted(test_vol.keys()):
                        print key
                    return
                pred_vol = str(test_vol[pred_time][toll_dir])
                outline = ','.join([toll_id, time_window, direction, pred_vol]) + '\n'
                fw.writelines(outline)
    fw.close()
    print 'Done writing.\n'


def pred_vol_by_avg(toll_id, direction, time_to_pred, test_avg_vol):
    index = time_to_index(time_to_pred)
    toll_dir = '-'.join([toll_id, direction])
    pred_vol = hist_vol[toll_dir][index]
    if math.fabs(test_avg_vol) < 1e-2:
        pred_vol = pred_vol
    elif pred_vol == 0.0:
        pred_vol = test_avg_vol
    elif math.fabs((test_avg_vol - pred_vol) / pred_vol) > 0.1:
        pred_vol = pred_vol + (test_avg_vol - pred_vol) * 0.5
    return pred_vol


def main():
    # hist_file_name = '../results/training_20min_avg_volume.csv'
    hist_file_name = history_vol('volume(table 6)_training', contextDir='training/')
    load_hist_vol_from(hist_file_name) # return: global hist_vol
    vol_read_testing_data('volume(table 6)_test1')


if __name__ == '__main__':
    main()


class VolumePredictor():
    def __init__(self):
        pass

    def train_with_file(self, history_att):
        pass
    
    def save_history(self, out_file):
        pass

    def load_history(self, in_file):
        pass
    
    def read_testing_file(self, in_file):
        pass
    
    def predictions():
        pass

    def save_predictions(self, out_file):
        pass