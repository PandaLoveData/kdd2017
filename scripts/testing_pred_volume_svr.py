# -*- coding: utf-8 -*-
#!/usr/bin/env python

'''
Predict the volume for testing data
'''

import os
from datetime import datetime, timedelta, time
from aggregate_volume import avgVolume
from utils import *
from sklearn import svm

file_suffix = '.csv'
out_path = '../results/'
dataDir = 'dataSets'
PRED_METHOD = 'AVE'
clf = svm.SVR()

tollgates = ['1', '1', '2', '3', '3']
directions = ['1', '0', '0', '1', '0']
toll_directions = map(lambda toll, dir: '-'.join([toll,dir]), tollgates, directions)

pred_year = 2016
pred_month = 10

hist_vol = {}
test_vol = {}
pred_vol = {}

pred_day = {}
pred_idx = []

pred_start_idx = time_to_index(time(hour=8,minute=0))
pred_end_idx = time_to_index(time(hour=10, minute=0))
pred_idx_1 = range(pred_start_idx, pred_end_idx)

pred_idx.extend(pred_idx_1)

pred_start_idx = time_to_index(time(hour=17, minute=0))
pred_end_idx = time_to_index(time(hour=19, minute=0))
pred_idx_2 = range(pred_start_idx, pred_end_idx)

pred_idx.extend(pred_idx_2)

test_start_idx = time_to_index(time(hour=6,minute=0))
test_end_idx = time_to_index(time(hour=8,minute=0))
test_idx_1 = range(test_start_idx, test_end_idx)

test_start_idx = time_to_index(time(hour=15,minute=0))
test_end_idx = time_to_index(time(hour=17,minute=0))
test_idx_2 = range(test_start_idx, test_end_idx)

test_idx = []
test_idx.extend(test_idx_1)
test_idx.extend(test_idx_2)

# for idx in pred_idx:
#     print idx

# For 72 20-min windows of all days, calculate its ave
# And store it. Date set to 10-01
def history_vol(in_file, contextDir):
    print 'Pre-training...'
    in_file = '/'.join([dataDir, contextDir, in_file])
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
        date_index = time_to_date_index(start_time)
        if not date_index in hist_win_vol[toll_dir]:
            hist_win_vol[toll_dir][date_index] = {}

        volume = float(line[-1])
        hist_win_vol[toll_dir][date_index][time_index] = volume
    print 'Done processing!\n'

    # out_file_name = out_path + 'history_avg_vol_svr' + file_suffix
    # print 'Writing to file:', out_file_name
    # fw = open(out_file_name, 'w')
    # outline = ','.join(['"tollgate_id"', '"start_time"', '"direction"', '"volume"']) + '\n'
    # fw.writelines(outline)
    # for toll_dir in sorted(hist_win_vol.keys()):
    #     [toll_id, direction] = toll_dir.split('-')
    #     toll_dir_vol = hist_win_vol[toll_dir]
    #     for time_index in range(0, 72):
    #         if not time_index in toll_dir_vol:
    #             toll_dir_vol[time_index] = [0.0]
    #         avg_volume = sum(toll_dir_vol[time_index]) / len(toll_dir_vol[time_index])
    #         avg_volume = str(round(avg_volume, 2))
    #         outline = ','.join([toll_id, str(index_to_time(time_index)), direction,
    #             avg_volume]) + '\n'
    #         fw.writelines(outline)
    #
    # fw.close()
    # print 'Done writing\n'

    return 0


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
        start_time = datetime.strptime(start_time_str, DATETIME_FORMAT)
        hist_vol[toll_dir][time_to_index(start_time)] = volume
    print 'Done loading!\n'
    return hist_vol


def vol_preprocess_testing_data(in_file, contextDir):
    in_file = '/'.join([dataDir, contextDir, in_file])
    print 'Preprocessing testing data from', in_file
    testing_vol_file = avgVolume(in_file)
    print 'Done! Output to', testing_vol_file, '\n'
    return testing_vol_file


def predict_day(day):
    print 'Predicting:', day
    global test_vol
    for toll_dir in toll_directions:
        [tollgate_id, direction] = toll_dir.split('-')
        if toll_dir not in test_vol:
            print 'Empty volume of route in time window:', toll_dir, before_time
            test_vol[toll_dir] = {}
        # if (len(test_vol[toll_dir]) == 0):
        #     print 'Empty volume for toll dir in time', str(pred_time), toll_dir
        #     test_vol[before_time][toll_dir].append(0.0)
        for idx in pred_idx:
            pred_time = index_to_time(idx)
            # get day's time to predict
            pred_time = datetime(year=pred_year,month=pred_month, day=day,
                hour=pred_time.hour,minute=pred_time.minute)
            # use previous data to make adjustment
            before_time = pred_time + timedelta(minutes=-20)
            before_index = time_to_index(before_time)
            test_avg_vol = 0.0
            if not before_time in test_vol[toll_dir]:
                print 'Warning! Missing past training data.', toll_dir, before_time
            else:
                # get average volume of this day's before time
                test_avg_vol = test_vol[toll_dir][before_time]

            if PRED_METHOD == 'AVE':
                pred_volume = pred_vol_by_avg(tollgate_id, direction, pred_time, test_avg_vol)
            elif PRED_METHOD == 'SVR':
                pred_volume = pred_vol_by_svr(tollgate_id, direction, pred_time, test_avg_vol)

            # update previous data using predicted value
            if pred_time not in test_vol[toll_dir]:
                test_vol[toll_dir][pred_time] = 0
                print 'Add predict time:', pred_time.strftime(DATETIME_FORMAT)
            test_vol[toll_dir][pred_time] = pred_volume

            if toll_dir not in pred_vol:
                pred_vol[toll_dir] = {}
            if pred_time not in pred_vol[toll_dir]:
                pred_vol[toll_dir][pred_time] = 0.0
            pred_vol[toll_dir][pred_time] = pred_volume


def write_time_window_prediction(fw, time_idx):
    global pred_day, test_vol, pred_vol
    for toll_dir in toll_directions:
        [toll_id, direction] = toll_dir.split('-')
        for idx in time_idx:
            pred_time = index_to_time(idx)
            for day in sorted(pred_day.keys()):
                pred_time = datetime(year=pred_year,month=pred_month,day=day,
                    hour=pred_time.hour,minute=pred_time.minute)
                end_time = pred_time + timedelta(minutes=20)
                time_window = '"[' + pred_time.strftime(DATETIME_FORMAT)+ \
                    ',' + end_time.strftime(DATETIME_FORMAT) +')"'
                if pred_time not in pred_vol[toll_dir]:
                    print 'Warning!', idx, pred_time, 'not in test_vol'
                    continue
                vol = str(pred_vol[toll_dir][pred_time])
                outline = ','.join([toll_id, time_window, direction, vol]) + '\n'
                fw.writelines(outline)


# After reading each day, make a prediction
def vol_read_testing_data(in_file, contextDir):
    testing_vol_file = vol_preprocess_testing_data(in_file, contextDir)
    print 'Reading testing data from', testing_vol_file
    fr = open(testing_vol_file, 'r')
    fr.readline() # skip the header
    test_data = fr.readlines()
    print test_data[0]
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
        if not toll_dir in test_vol:
            test_vol[toll_dir] = {}

        start_time_str = line[1][1:]
        # end_time_str = line[2][0:-1]
        start_time = datetime.strptime(start_time_str, DATETIME_FORMAT)
        time_index = time_to_index(start_time)

        if time_index not in test_idx:
            continue # ignore data to be predicted

        if not start_time in test_vol[toll_dir]:
            test_vol[toll_dir][start_time] = 0.0

        volume = float(line[4])

        test_vol[toll_dir][start_time] = volume

        day = start_time.day
        if day not in pred_day:
            print 'Add day:', day
            pred_day[day] = 0
        # when a new day comes, predict the day before, because we
        # cannot use later data to predict past data
        # when i == len(test_data) - 1, predict the volume of the last day
        if ((day != last_day) and (last_day != -1)):
            predict_day(last_day)

        last_day = day

    predict_day(day)

    print 'Done processing testing data.\n'

    out_file_name = out_path + 'pred_avg_volume' + file_suffix
    print 'Writing to file:', out_file_name
    fw = open(out_file_name, 'w')
    outline = ','.join(['tollgate_id','time_window','direction','volume']) + '\n'
    fw.writelines(outline)

    # to obey the format of submission_sample_volume, we need to output
    # two time window predictions by sequence
    global pred_idx_1
    write_time_window_prediction(fw, pred_idx_1)
    global pred_idx_2
    write_time_window_prediction(fw, pred_idx_2)
    fw.close()
    print 'Done writing.\n'
    return out_file_name


def pred_vol_by_avg(toll_id, direction, time_to_pred, test_avg_vol):
    index = time_to_index(time_to_pred)
    toll_dir = '-'.join([toll_id, direction])
    pred_vol = hist_vol[toll_dir][index]
    if math.fabs(test_avg_vol) < 1e-2:
        pred_vol = pred_vol
    elif pred_vol == 0.0:
        pred_vol = test_avg_vol
    elif math.fabs((test_avg_vol - pred_vol) / pred_vol) > 0.1:
        pred_vol = pred_vol * 0.9 + 0.1 * test_avg_vol
    return pred_vol


def pred_vol_by_svr(toll_id, direction, time_to_pred, test_avg_vol):
    index = time_to_index(time_to_pred)
    toll_dir = '-'.join([toll_id, direction])

    print 'Custom SVR Prediction underway!\n'
    pred_vol = clf.predict(X)

    if math.fabs(test_avg_vol) < 1e-2:
        pred_vol = pred_vol
    elif pred_vol == 0.0:
        pred_vol = test_avg_vol
    elif math.fabs((test_avg_vol - pred_vol) / pred_vol) > 0.1:
        pred_vol = pred_vol * 0.9 + 0.1 * test_avg_vol
    return pred_vol


def main():
    # hist_file_name = '../results/training_20min_avg_volume.csv'
    hist_file_name = history_vol('volume(table 6)_training', contextDir='training')
    # load_hist_vol_from(hist_file_name) # return: global hist_vol # not for svr
    # read and predict at the same time
    vol_read_testing_data('volume(table 6)_test1', contextDir='testing_phase1')


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
