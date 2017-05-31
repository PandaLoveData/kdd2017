# -*- coding: utf-8 -*-
#!/usr/bin/env python

'''
test avg travel time and volume locally using MAPE
'''

from datetime import datetime, time, date, timedelta

from aggregate_travel_time import avgTravelTime
from aggregate_volume import avgVolume
from utils import att_mape, vol_mape, DATETIME_FORMAT, time_to_index, MAX_TIME_INDEX
from testing_pred_att import history_avg_travel_time, load_hist_avg_travel_time, att_read_testing_data
from testing_pred_volume import history_vol, load_hist_vol_from, vol_read_testing_data
from att_predictor import att_predictor
from visual import data_viewer

dataDir = 'dataSets'
result_dir = '../results'
file_suffix = '.csv'

pred_year = 2016
pred_month = 10

start_index = time_to_index(time(hour=8, minute=0))
end_index = time_to_index(time(hour=10, minute=0))
pred_idx_1 = range(start_index, end_index)

start_index = time_to_index(time(hour=17, minute=0))
end_index = time_to_index(time(hour=19, minute=0))
pred_idx_2 = range(start_index, end_index)

pred_idx = []
pred_idx.extend(pred_idx_1)
pred_idx.extend(pred_idx_2) 

pred_att = {}
real_att = {}

pred_vol = {}
real_vol = {}

routes = []
toll_dirs = []
time_windows = []

def set_routes(_routes):
    global routes
    print 'Set routes:'
    for r in _routes:
        print r
    routes = _routes


def set_toll_dirs(_toll_dirs):
    global toll_dirs
    print 'Set toll directions:'
    for td in _toll_dirs:
        print td
    toll_dirs = _toll_dirs


def set_time_windows(_timewin):
    global time_windows
    print 'Set time windows:'
    for t in _timewin:
        print t
    time_windows = _timewin


def get_real_att(in_file, context_dir='test_local'):
    '''
    calculate real avg travel time from trajectories file
    '''
    _ap = att_predictor(data_dir='dataSets', context_dir=context_dir, 
        raw_file=in_file, result_dir='../results/local')
    real_att_f = _ap.process_raw_file()
    _ap.process_hist_file(real_att_f)
    _ap.smooth_hist_att_data()
    att_file_name = _ap.write_hist_att(out_file='valid_hist_att')

    real_att = {}
    
    print 'Reading real avg travel time from test file', att_file_name   
    fr = open(att_file_name, 'r')
    fr.readline() # skip header
    real_lines = fr.readlines()
    print 'Done reading test data.\n'

    print 'Start processing real avg travel time...'
    for i in range(len(real_lines)):
        # "B","3","2016-10-11 00:20:00","103.27"
        line = real_lines[i].replace('"', '').split(',')
        
        intersection_id = line[0]
        tollgate_id = line[1]
        route_id = intersection_id + '-' + tollgate_id
        if route_id not in real_att:
            real_att[route_id] = {}
        
        start_time = datetime.strptime(line[2], DATETIME_FORMAT)
        
        if start_time not in real_att[route_id]:
            real_att[route_id][start_time] = 0.0
        
        att = float(line[-1])
        real_att[route_id][start_time]= att

    set_routes(sorted(real_att.keys()))
    print 'Done loading real avg travel time.\n'
    return real_att


def get_pred_att(in_file):
    '''
    load prediction of avg travel time from results file
    '''
    global pred_att
    pred_att.clear()

    pred_time_windows = {}

    # in_file = '/'.join([result_dir, in_file + file_suffix])
    print 'Loading prediction data from file', in_file
    fr = open(in_file, 'r')
    fr.readline() # skip header
    pred_data = fr.readlines()
    fr.close()

    for i in range(len(pred_data)):
        # A,2,"[2016-10-11 08:00:00,2016-10-11 08:20:00)",78.02
        line = pred_data[i].replace('"', '').split(',')
        intersection_id = line[0]
        tollgate_id = line[1]
        route_id = intersection_id + '-' + tollgate_id

        if route_id not in pred_att:
            pred_att[route_id] = {}
        
        # ignore first '['
        start_time = datetime.strptime(line[2][1:], DATETIME_FORMAT)
        # time_index = time_to_index(start_time)
        if start_time not in pred_att[route_id]:
            pred_att[route_id][start_time] = 0.0
        if start_time not in pred_time_windows:
            pred_time_windows[start_time] = 0
        
        att = float(line[-1])
        pred_att[route_id][start_time] = att

    # save time windows of predictions
    print 'Time window len:', len(pred_time_windows)
    set_time_windows(sorted(pred_time_windows.keys()))
    print 'Done loading!\n'
    return pred_att


def test_pred_att():
    print 'Test local prediction of avg travel time...'
    hist_att_file = history_avg_travel_time('trajectories(table 5)_local', contextDir='training_local/')
    hist_att = load_hist_avg_travel_time(hist_att_file)
    att_read_testing_data('trajectories(table 5)_valid', contextDir='test_local/')

    pred_att = get_pred_att('pred_avg_travel_time_local')
    real_att = get_real_att('trajectories(table 5)_valid', 'test_local')
    print 'Done evaluating MAPE for avg travel time prediction. MAPE is: \n'
    print att_mape(real_att, pred_att, routes, time_windows)

def test_att_predictor():
    '''
    test att predictor and calc att mape
    '''
    print 'Test local prediction of avg travel time using predictor...'
    ap = att_predictor(data_dir='dataSets', context_dir='training_local',
        raw_file='trajectories(table 5)_local', result_dir='../results/local')
    hist_att_f = ap.process_raw_file()
    ap.process_hist_file(hist_att_f)
    ap.smooth_hist_att_data()
    ap.calc_hist_att_of_win()
    hist_avg_f = ap.write_hist_avg('hist_att_local')

    ap.read_testing_data(ap.data_dir, context_dir='test_local',
        in_file='trajectories(table 5)_valid')
    pred_file = ap.do_prediction(pred_idx, 'pred_avg_travel_time_test')

    pred_att = get_pred_att(pred_file)
    real_att = get_real_att('trajectories(table 5)_valid', 'test_local')
    print att_mape(real_att, pred_att, routes, time_windows)


def get_real_vol(in_file, contextDir):
    global real_vol
    real_vol.clear()

    in_file = '/'.join([dataDir, contextDir, in_file])
    print 'Get real volume from file:', in_file
    vol_file_name = avgVolume(in_file)
    print 'Get aggregate volume from file', vol_file_name

    fr = open(vol_file_name, 'r')
    fr.readline() # skip header
    vol_lines = fr.readlines()
    fr.close()
    print 'Done reading all lines!\n'

    print 'Start loading real volume...'
    for i in range(len(vol_lines)):
        line = vol_lines[i].replace('"', '').split(',')
        tollgate_id = line[0]
        direction = line[3]
        toll_dir = tollgate_id + '-' + direction

        # ignore first '[' 
        start_time = datetime.strptime(line[1][1:], DATETIME_FORMAT)
        day = start_time.day
        
        if toll_dir not in real_vol:
            real_vol[toll_dir] = {}
        if start_time not in real_vol[toll_dir]:
            real_vol[toll_dir][start_time] = 0
        
        vol = float(line[-1])
        real_vol[toll_dir][start_time] = vol

    print 'Done getting real volume!\n'
    return real_vol


def get_pred_vol(in_file):
    '''
    Load predictions of volume from file
    '''
    global pred_vol
    pred_vol.clear()
    local_toll_dirs = {}
    local_time_wind = {}
    print 'Reading predictions from', in_file
    fr = open(in_file, 'r')
    fr.readline() # skip header
    vol_lines = fr.readlines()
    fr.close()
    print 'Done reading!\n'

    print 'Start loading predictions...'
    for i in range(len(vol_lines)):
        line = vol_lines[i].replace('"', '').split(',')
        tollgate_id = line[0]
        direction = line[3]
        toll_dir = tollgate_id + '-' + direction
        if toll_dir not in local_toll_dirs:
            local_toll_dirs[toll_dir] = 0
        # ignore close bracket '['
        start_time = datetime.strptime(line[1][1:], DATETIME_FORMAT)

        vol = float(line[-1])

        if toll_dir not in pred_vol:
            pred_vol[toll_dir] = {}
        if start_time not in pred_vol[toll_dir]:
            pred_vol[toll_dir][start_time] = 0
        if start_time not in local_time_wind:
            # print 'New prediction time comes!', start_time
            local_time_wind[start_time] = 0
        pred_vol[toll_dir][start_time] = vol
    
    set_toll_dirs(sorted(local_toll_dirs.keys()))
    set_time_windows(sorted(local_time_wind.keys()))
    print 'Done loading!\n'
    return pred_vol


def test_pred_vol():
    print 'Test local prediction of volume...'

    hist_file_name = history_vol('volume(table 6)_training2', 'dataSet_phase2')
    hist_vol = load_hist_vol_from(hist_file_name)
    vol_pred_file_name = vol_read_testing_data('volume(table 6)_test2', 'dataSet_phase2')
    print 'vol read testing file is:', vol_pred_file_name

    pred_vol = get_pred_vol(vol_pred_file_name)
    real_vol = get_real_vol('volume(table 6)_valid', 'test_local')
    
    print 'Done evaluating MAPE for volume. MAPE is:\n'
    print vol_mape(real_vol, pred_vol, toll_dirs, time_windows)


def test_view_data():
    '''
    test view data
    '''
    dv = data_viewer()
    ap = att_predictor(data_dir='dataSets', context_dir='training',
        raw_file='trajectories(table 5)_training', result_dir='../results/local')
    hist_att_f = ap.process_raw_file()
    ap.process_hist_file(hist_att_f)
    


def main():
    # test_pred_att()
    test_att_predictor()
    test_pred_vol()


if __name__ == '__main__':
    main()